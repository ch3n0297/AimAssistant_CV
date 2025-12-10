#!/usr/bin/env python3
"""
Aim Assist System - 主程式

整合所有模組，提供輔助瞄準功能。
按 T 切換開關，按 ESC 退出。

使用方式:
    python main.py
    python main.py --config custom_config.yaml
"""

import sys
import time
import argparse
from pathlib import Path
from typing import Optional

import yaml
from pynput import keyboard

# 加入專案路徑
sys.path.insert(0, str(Path(__file__).parent))

from core.capture import ScreenCapture
from core.detector import EnemyDetector, Detection
from core.target_selector import TargetSelector
from core.controller import AimController
from core.mouse_control import MouseController
from overlay.hud import OverlayManager
from utils.coordinate import get_scale_factors
from utils.logger import Logger


class AimAssistSystem:
    """Aim Assist 系統主類別"""

    def __init__(self, config_path: str = "config.yaml"):
        """
        初始化系統

        Args:
            config_path: 設定檔路徑
        """
        # 載入設定
        self.config = self._load_config(config_path)

        # 系統狀態
        self.running = True
        self.aim_enabled = False

        # 效能追蹤
        self.fps = 0.0
        self.latency_ms = 0.0
        self.frame_count = 0
        self.last_fps_time = time.perf_counter()
        self.fps_frame_count = 0

        # 初始化模組
        self._init_modules()

        # 設定鍵盤監聽
        self._setup_keyboard()

        print("\n=== Aim Assist System ===")
        print("按 T 切換 Aim Assist 開關")
        print("按 ESC 退出程式")
        print("========================\n")

    def _load_config(self, config_path: str) -> dict:
        """載入設定檔"""
        config_file = Path(__file__).parent / config_path

        if not config_file.exists():
            print(f"警告: 找不到設定檔 {config_file}，使用預設設定")
            return self._default_config()

        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        print(f"已載入設定檔: {config_file}")
        return config

    def _default_config(self) -> dict:
        """預設設定"""
        return {
            'capture': {
                'screen_width': 1920,
                'screen_height': 1080,
                'target_size': [640, 360]
            },
            'detection': {
                'model_path': '/home/hjc/coSpace/CV_final/ModelTraining/models/enemy_detection_v11n/best.pt',
                'confidence_threshold': 0.5,
                'device': 'cuda'
            },
            'controller': {
                'kp': 0.15,
                'kd': 0.05,
                'alpha': 0.85,
                'dead_zone': 5,
                'max_speed': 30
            },
            'overlay': {
                'enabled': True,
                'show_all_boxes': True,
                'show_fps': True,
                'show_latency': True
            },
            'logging': {
                'enabled': True,
                'output_dir': './logs',
                'log_interval': 100
            }
        }

    def _init_modules(self):
        """初始化所有模組"""
        cap_cfg = self.config['capture']
        det_cfg = self.config['detection']
        ctrl_cfg = self.config['controller']
        ovl_cfg = self.config['overlay']
        log_cfg = self.config['logging']

        # 螢幕擷取
        print("初始化螢幕擷取模組...")
        self.capture = ScreenCapture(
            screen_width=cap_cfg['screen_width'],
            screen_height=cap_cfg['screen_height'],
            target_size=tuple(cap_cfg['target_size'])
        )

        # 座標縮放因子
        self.scale_x, self.scale_y = get_scale_factors(
            model_size=tuple(cap_cfg['target_size']),
            screen_size=(cap_cfg['screen_width'], cap_cfg['screen_height'])
        )

        # YOLO 偵測器
        print("初始化 YOLO 偵測器...")
        self.detector = EnemyDetector(
            model_path=det_cfg['model_path'],
            confidence_threshold=det_cfg['confidence_threshold'],
            device=det_cfg['device']
        )

        # 目標選擇器
        self.selector = TargetSelector()

        # PD 控制器
        self.controller = AimController(
            kp=ctrl_cfg['kp'],
            kd=ctrl_cfg['kd'],
            alpha=ctrl_cfg['alpha'],
            dead_zone=ctrl_cfg['dead_zone'],
            max_speed=ctrl_cfg['max_speed']
        )

        # 滑鼠控制器
        self.mouse = MouseController()

        # Overlay
        self.overlay_enabled = ovl_cfg['enabled']
        if self.overlay_enabled:
            print("初始化 Overlay...")
            self.overlay = OverlayManager(
                width=cap_cfg['screen_width'],
                height=cap_cfg['screen_height']
            )

        # 日誌記錄器
        self.logger = Logger(
            output_dir=log_cfg['output_dir'],
            enabled=log_cfg['enabled'],
            log_interval=log_cfg['log_interval']
        )

        print("所有模組初始化完成!")

    def _setup_keyboard(self):
        """設定鍵盤監聽"""
        def on_press(key):
            try:
                if key == keyboard.Key.esc:
                    print("\n偵測到 ESC，準備退出...")
                    self.running = False
                elif hasattr(key, 'char') and key.char == 't':
                    self.aim_enabled = not self.aim_enabled
                    status = "ON" if self.aim_enabled else "OFF"
                    print(f"Aim Assist: {status}")
                    if not self.aim_enabled:
                        self.controller.reset()
            except AttributeError:
                pass

        self.keyboard_listener = keyboard.Listener(on_press=on_press)
        self.keyboard_listener.start()

    def _update_fps(self):
        """更新 FPS 計算"""
        self.fps_frame_count += 1
        current_time = time.perf_counter()
        elapsed = current_time - self.last_fps_time

        if elapsed >= 1.0:
            self.fps = self.fps_frame_count / elapsed
            self.fps_frame_count = 0
            self.last_fps_time = current_time

    def run(self):
        """主迴圈"""
        print("\n開始運行...")

        try:
            while self.running:
                loop_start = time.perf_counter()

                # 1. 擷取畫面
                frame = self.capture.capture()

                # 2. YOLO 推論
                detections, inference_time = self.detector.detect_with_timing(frame)

                # 3. 將偵測座標轉換為螢幕座標
                screen_detections = [
                    det.to_screen_coords(self.scale_x, self.scale_y)
                    for det in detections
                ]

                # 4. 目標選擇
                cursor_pos = self.mouse.get_position()
                target = self.selector.select(screen_detections, cursor_pos)

                # 5. 控制器計算並移動滑鼠（如果啟用）
                if self.aim_enabled and target:
                    target_pos = (target.center_x, target.center_y)
                    dx, dy = self.controller.compute(cursor_pos, target_pos)
                    self.mouse.move_relative(dx, dy)

                # 6. 計算總延遲
                loop_time = (time.perf_counter() - loop_start) * 1000
                self.latency_ms = loop_time

                # 7. 更新 FPS
                self._update_fps()

                # 8. 更新 Overlay
                if self.overlay_enabled:
                    self.overlay.update(
                        detections=screen_detections,
                        locked_target=target,
                        fps=self.fps,
                        latency_ms=self.latency_ms,
                        aim_enabled=self.aim_enabled
                    )

                # 9. 記錄日誌
                self.logger.log(
                    aim_assist_enabled=self.aim_enabled,
                    detection_count=len(detections),
                    inference_time_ms=inference_time,
                    total_latency_ms=self.latency_ms,
                    fps=self.fps,
                    locked_target_x=target.center_x if target else None,
                    locked_target_y=target.center_y if target else None
                )

                self.frame_count += 1

        except KeyboardInterrupt:
            print("\n收到中斷信號...")

        finally:
            self.shutdown()

    def shutdown(self):
        """關閉系統"""
        print("\n正在關閉系統...")

        # 停止鍵盤監聽
        if hasattr(self, 'keyboard_listener'):
            self.keyboard_listener.stop()

        # 關閉擷取模組
        if hasattr(self, 'capture'):
            self.capture.close()

        # 關閉 Overlay
        if hasattr(self, 'overlay') and self.overlay_enabled:
            self.overlay.close()

        # 儲存日誌摘要
        if hasattr(self, 'logger'):
            stats = self.logger.get_statistics()
            if stats:
                print("\n=== 運行統計 ===")
                print(f"總幀數: {stats.get('total_frames', 0)}")
                print(f"平均推論時間: {stats.get('avg_inference_time_ms', 0):.2f} ms")
                print(f"平均延遲: {stats.get('avg_latency_ms', 0):.2f} ms")
                print(f"平均 FPS: {stats.get('avg_fps', 0):.1f}")
                print("================")
            self.logger.close()

        print("系統已關閉")


def main():
    """程式入口"""
    parser = argparse.ArgumentParser(description='Aim Assist System')
    parser.add_argument(
        '--config', '-c',
        default='config.yaml',
        help='設定檔路徑 (預設: config.yaml)'
    )
    parser.add_argument(
        '--no-overlay',
        action='store_true',
        help='不顯示 Overlay'
    )

    args = parser.parse_args()

    # 建立並運行系統
    system = AimAssistSystem(config_path=args.config)

    if args.no_overlay:
        system.overlay_enabled = False

    system.run()


if __name__ == "__main__":
    main()
