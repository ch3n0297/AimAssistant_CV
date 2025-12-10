"""
YOLO 推論模組 (Enemy Detector Module)

負責載入 YOLOv11n 模型並執行敵人偵測。
使用 Ultralytics 進行推論。
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Optional
import torch


@dataclass
class Detection:
    """偵測結果資料類別"""
    x1: float           # 左上角 x (相對於模型輸入尺寸)
    y1: float           # 左上角 y
    x2: float           # 右下角 x
    y2: float           # 右下角 y
    score: float        # 信心分數
    class_id: int       # 類別 ID

    @property
    def center_x(self) -> float:
        """邊界框中心 x 座標"""
        return (self.x1 + self.x2) / 2

    @property
    def center_y(self) -> float:
        """邊界框中心 y 座標"""
        return (self.y1 + self.y2) / 2

    @property
    def width(self) -> float:
        """邊界框寬度"""
        return self.x2 - self.x1

    @property
    def height(self) -> float:
        """邊界框高度"""
        return self.y2 - self.y1

    def to_screen_coords(self, scale_x: float, scale_y: float) -> 'Detection':
        """
        將座標轉換為螢幕座標

        Args:
            scale_x: x 方向縮放比例
            scale_y: y 方向縮放比例

        Returns:
            新的 Detection 物件，座標已轉換為螢幕座標
        """
        return Detection(
            x1=self.x1 * scale_x,
            y1=self.y1 * scale_y,
            x2=self.x2 * scale_x,
            y2=self.y2 * scale_y,
            score=self.score,
            class_id=self.class_id
        )


class EnemyDetector:
    """敵人偵測器，使用 YOLOv11n 模型"""

    def __init__(
        self,
        model_path: str,
        confidence_threshold: float = 0.5,
        device: str = "cuda"
    ):
        """
        初始化偵測器

        Args:
            model_path: 模型權重路徑 (.pt 檔)
            confidence_threshold: 信心閾值，低於此值的偵測結果會被過濾
            device: 推論裝置 ("cuda" 或 "cpu")
        """
        self.confidence_threshold = confidence_threshold
        self.device = device

        # 檢查 CUDA 是否可用
        if device == "cuda" and not torch.cuda.is_available():
            print("警告: CUDA 不可用，回退至 CPU")
            self.device = "cpu"

        # 載入模型
        print(f"載入模型: {model_path}")
        print(f"使用裝置: {self.device}")

        from ultralytics import YOLO
        self.model = YOLO(model_path)
        self.model.to(self.device)

        # 預熱模型
        self._warmup()

        print("模型載入完成")

    def _warmup(self):
        """預熱模型以獲得穩定的推論時間"""
        dummy_input = np.zeros((360, 640, 3), dtype=np.uint8)
        for _ in range(3):
            self.model(dummy_input, verbose=False)

    def detect(self, frame: np.ndarray) -> List[Detection]:
        """
        執行敵人偵測

        Args:
            frame: RGB 格式的輸入影像，shape 為 (H, W, 3)

        Returns:
            偵測結果列表
        """
        # 執行推論
        results = self.model(frame, verbose=False, conf=self.confidence_threshold)

        detections = []

        # 解析結果
        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue

            for box in boxes:
                # 取得邊界框座標
                xyxy = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0].cpu().numpy())
                cls = int(box.cls[0].cpu().numpy())

                detection = Detection(
                    x1=float(xyxy[0]),
                    y1=float(xyxy[1]),
                    x2=float(xyxy[2]),
                    y2=float(xyxy[3]),
                    score=conf,
                    class_id=cls
                )
                detections.append(detection)

        return detections

    def detect_with_timing(self, frame: np.ndarray) -> tuple:
        """
        執行偵測並返回推論時間

        Args:
            frame: RGB 格式的輸入影像

        Returns:
            (detections, inference_time_ms)
        """
        import time
        start = time.perf_counter()
        detections = self.detect(frame)
        inference_time = (time.perf_counter() - start) * 1000
        return detections, inference_time


# 測試用
if __name__ == "__main__":
    import time
    from capture import ScreenCapture

    model_path = "/home/hjc/coSpace/CV_final/ModelTraining/models/enemy_detection_v11n/best.pt"

    print("測試 YOLO 推論模組...")

    detector = EnemyDetector(
        model_path=model_path,
        confidence_threshold=0.5,
        device="cuda"
    )

    with ScreenCapture() as capture:
        # 測試推論速度
        times = []
        detection_counts = []

        for i in range(50):
            frame = capture.capture()
            detections, inference_time = detector.detect_with_timing(frame)
            times.append(inference_time)
            detection_counts.append(len(detections))

            if i == 0:
                print(f"\n第一幀偵測結果:")
                print(f"  偵測數量: {len(detections)}")
                for det in detections:
                    print(f"    - [{det.x1:.1f}, {det.y1:.1f}, {det.x2:.1f}, {det.y2:.1f}] "
                          f"score={det.score:.2f} center=({det.center_x:.1f}, {det.center_y:.1f})")

        avg_time = sum(times) / len(times)
        max_time = max(times)
        min_time = min(times)
        avg_count = sum(detection_counts) / len(detection_counts)

        print(f"\n推論 50 幀:")
        print(f"  平均時間: {avg_time:.2f} ms")
        print(f"  最大時間: {max_time:.2f} ms")
        print(f"  最小時間: {min_time:.2f} ms")
        print(f"  理論 FPS: {1000 / avg_time:.1f}")
        print(f"  平均偵測數量: {avg_count:.1f}")
