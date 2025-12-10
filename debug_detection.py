#!/usr/bin/env python3
"""
除錯腳本 - 測試擷取和偵測是否正常運作
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import cv2
import numpy as np
from core.capture import ScreenCapture
from core.detector import EnemyDetector

def main():
    print("=== 除錯模式 ===")
    print("此腳本會擷取螢幕並測試偵測")
    print()

    # 初始化
    print("初始化擷取模組...")
    capture = ScreenCapture()

    print("初始化偵測器...")
    detector = EnemyDetector(
        model_path="/home/hjc/coSpace/CV_final/ModelTraining/models/enemy_detection_v11n/best.pt",
        confidence_threshold=0.3,  # 降低閾值以便看到更多偵測
        device="cuda"
    )

    print()
    print("3 秒後開始擷取...")
    print("請確保遊戲畫面在螢幕上!")
    time.sleep(3)

    # 擷取多幀
    for i in range(5):
        print(f"\n--- 第 {i+1} 幀 ---")

        # 擷取
        frame = capture.capture()
        raw_frame = capture.capture_raw()

        print(f"擷取尺寸: {frame.shape} (模型輸入)")
        print(f"原始尺寸: {raw_frame.shape}")

        # 偵測
        start = time.perf_counter()
        detections = detector.detect(frame)
        elapsed = (time.perf_counter() - start) * 1000

        print(f"偵測時間: {elapsed:.2f} ms")
        print(f"偵測數量: {len(detections)}")

        # 顯示偵測結果
        for j, det in enumerate(detections):
            print(f"  [{j}] 位置: ({det.x1:.0f}, {det.y1:.0f}) - ({det.x2:.0f}, {det.y2:.0f}), "
                  f"中心: ({det.center_x:.0f}, {det.center_y:.0f}), "
                  f"信心: {det.score:.2f}")

        # 儲存帶有標註的圖片
        output_frame = frame.copy()

        # frame 已經是 BGR 格式，可直接用於 cv2

        # 畫偵測框
        for det in detections:
            x1, y1, x2, y2 = int(det.x1), int(det.y1), int(det.x2), int(det.y2)
            cv2.rectangle(output_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(output_frame, f"{det.score:.2f}", (x1, y1 - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        # 儲存
        output_path = f"debug_frame_{i+1}.png"
        cv2.imwrite(output_path, output_frame)
        print(f"已儲存: {output_path}")

        time.sleep(1)

    # 也儲存一張原始尺寸的圖片 (已經是 BGR)
    cv2.imwrite("debug_raw_screen.png", raw_frame)
    print(f"\n已儲存原始螢幕截圖: debug_raw_screen.png")

    capture.close()

    print("\n=== 除錯完成 ===")
    print("請檢查生成的圖片:")
    print("  - debug_frame_*.png: 模型輸入尺寸 (640x360) + 偵測框")
    print("  - debug_raw_screen.png: 原始螢幕截圖 (1920x1080)")
    print()
    print("如果偵測框有標註敵人，表示模型正常。")
    print("如果沒有任何偵測，可能是:")
    print("  1. 遊戲畫面不在螢幕上")
    print("  2. 模型無法識別當前遊戲畫面中的敵人")
    print("  3. 需要調整 confidence_threshold")

if __name__ == "__main__":
    main()
