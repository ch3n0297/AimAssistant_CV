"""
目標選擇模組 (Target Selector Module)

負責從偵測結果中選擇最佳目標。
預設選擇距離滑鼠最近的目標。
"""

from typing import List, Optional, Tuple
from .detector import Detection
import math


class TargetSelector:
    """目標選擇器，自動選擇距離滑鼠最近的目標"""

    # 螢幕中心點（玩家位置）
    SCREEN_CENTER = (960, 540)

    def __init__(self):
        """初始化目標選擇器"""
        self.candidates: List[Detection] = []
        self.current_target: Optional[Detection] = None

    def select(
        self,
        detections: List[Detection],
        cursor_pos: Tuple[float, float]
    ) -> Optional[Detection]:
        """
        從偵測結果中選擇目標

        Args:
            detections: 偵測結果列表（螢幕座標）
            cursor_pos: 目前滑鼠位置 (x, y)

        Returns:
            選中的目標，若無合適目標則返回 None
        """
        if not detections:
            self.candidates = []
            self.current_target = None
            return None

        # 過濾掉包含螢幕中心的偵測框（可能是自己的玩家）
        screen_cx, screen_cy = self.SCREEN_CENTER
        filtered_detections = [
            det for det in detections
            if not self._point_in_box(screen_cx, screen_cy, det)
        ]

        # 儲存候選目標（過濾後）
        self.candidates = filtered_detections

        if not filtered_detections:
            self.current_target = None
            return None

        cursor_x, cursor_y = cursor_pos

        min_distance = float('inf')
        nearest_target = None

        for detection in filtered_detections:
            # 計算距離（使用目標中心點）
            distance = math.sqrt(
                (detection.center_x - cursor_x) ** 2 +
                (detection.center_y - cursor_y) ** 2
            )

            if distance < min_distance:
                min_distance = distance
                nearest_target = detection

        self.current_target = nearest_target
        return nearest_target

    def get_candidates(self) -> List[Detection]:
        """
        取得所有候選目標

        Returns:
            候選目標列表
        """
        return self.candidates

    def get_current_target(self) -> Optional[Detection]:
        """
        取得目前鎖定的目標

        Returns:
            目前鎖定的目標，若無則返回 None
        """
        return self.current_target

    @staticmethod
    def calculate_distance(
        pos1: Tuple[float, float],
        pos2: Tuple[float, float]
    ) -> float:
        """
        計算兩點之間的距離

        Args:
            pos1: 第一個點 (x, y)
            pos2: 第二個點 (x, y)

        Returns:
            兩點之間的歐氏距離
        """
        return math.sqrt(
            (pos1[0] - pos2[0]) ** 2 +
            (pos1[1] - pos2[1]) ** 2
        )

    @staticmethod
    def _point_in_box(x: float, y: float, detection: Detection) -> bool:
        """
        檢查點是否在偵測框內

        Args:
            x: 點的 X 座標
            y: 點的 Y 座標
            detection: 偵測框

        Returns:
            True 如果點在框內，否則 False
        """
        return (detection.x1 <= x <= detection.x2 and
                detection.y1 <= y <= detection.y2)


# 測試用
if __name__ == "__main__":
    from detector import Detection

    print("測試目標選擇模組...")

    selector = TargetSelector()

    # 模擬偵測結果
    detections = [
        Detection(x1=100, y1=100, x2=150, y2=150, score=0.9, class_id=0),
        Detection(x1=500, y1=300, x2=550, y2=350, score=0.85, class_id=0),
        Detection(x1=800, y1=200, x2=850, y2=250, score=0.7, class_id=0),
    ]

    # 模擬滑鼠位置
    cursor_pos = (960, 540)  # 螢幕中央

    # 選擇目標
    target = selector.select(detections, cursor_pos)

    print(f"\n滑鼠位置: {cursor_pos}")
    print(f"候選目標數量: {len(selector.get_candidates())}")

    if target:
        print(f"選中目標: center=({target.center_x:.1f}, {target.center_y:.1f})")
        distance = selector.calculate_distance(cursor_pos, (target.center_x, target.center_y))
        print(f"距離: {distance:.1f} 像素")
    else:
        print("無選中目標")
