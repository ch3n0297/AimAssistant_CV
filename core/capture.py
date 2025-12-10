"""
螢幕擷取模組 (Screen Capture Module)

負責擷取全螢幕畫面並縮放至模型輸入尺寸。
使用 mss 進行高效能螢幕截圖。
"""

import numpy as np
import cv2
import mss
from typing import Tuple, Optional


class ScreenCapture:
    """螢幕擷取類別，負責擷取並縮放螢幕畫面"""

    def __init__(
        self,
        screen_width: int = 1920,
        screen_height: int = 1080,
        target_size: Tuple[int, int] = (640, 360)
    ):
        """
        初始化螢幕擷取模組

        Args:
            screen_width: 螢幕寬度 (固定 1920)
            screen_height: 螢幕高度 (固定 1080)
            target_size: 模型輸入尺寸 (寬, 高)，預設 (640, 360)
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.target_size = target_size

        # 初始化 mss
        self.sct = mss.mss()

        # 定義擷取區域（主螢幕）
        self.monitor = {
            "top": 0,
            "left": 0,
            "width": screen_width,
            "height": screen_height
        }

        # 計算縮放比例
        self.scale_x = screen_width / target_size[0]
        self.scale_y = screen_height / target_size[1]

    def capture(self) -> np.ndarray:
        """
        擷取螢幕並縮放至目標尺寸

        Returns:
            np.ndarray: BGR 格式的 numpy array，shape 為 (H, W, 3)
                       (YOLO 預期 BGR 格式輸入)
        """
        # 擷取螢幕
        screenshot = self.sct.grab(self.monitor)

        # 轉換為 numpy array (BGRA 格式)
        frame = np.array(screenshot)

        # BGRA -> BGR (保持 BGR 格式給 YOLO)
        frame = frame[:, :, :3]

        # 縮放至目標尺寸
        frame = cv2.resize(frame, self.target_size, interpolation=cv2.INTER_LINEAR)

        return frame

    def capture_raw(self) -> np.ndarray:
        """
        擷取螢幕原始尺寸（不縮放）

        Returns:
            np.ndarray: BGR 格式的 numpy array，shape 為 (1080, 1920, 3)
        """
        screenshot = self.sct.grab(self.monitor)
        frame = np.array(screenshot)
        frame = frame[:, :, :3]  # BGRA -> BGR
        return frame

    def get_scale_factors(self) -> Tuple[float, float]:
        """
        取得從模型座標到螢幕座標的縮放比例

        Returns:
            Tuple[float, float]: (scale_x, scale_y)
        """
        return (self.scale_x, self.scale_y)

    def close(self):
        """關閉 mss 資源"""
        self.sct.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# 測試用
if __name__ == "__main__":
    import time

    print("測試螢幕擷取模組...")

    with ScreenCapture() as capture:
        # 測試擷取速度
        times = []
        for i in range(100):
            start = time.perf_counter()
            frame = capture.capture()
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)

            if i == 0:
                print(f"Frame shape: {frame.shape}")
                print(f"Frame dtype: {frame.dtype}")

        avg_time = sum(times) / len(times)
        max_time = max(times)
        min_time = min(times)

        print(f"\n擷取 100 幀:")
        print(f"  平均時間: {avg_time:.2f} ms")
        print(f"  最大時間: {max_time:.2f} ms")
        print(f"  最小時間: {min_time:.2f} ms")
        print(f"  理論 FPS: {1000 / avg_time:.1f}")
