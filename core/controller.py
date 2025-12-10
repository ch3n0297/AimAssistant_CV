"""
PD 控制器模組 (Aim Controller Module)

負責計算平滑的滑鼠移動向量。
使用 PD 控制器 + α-β 平滑以實現流暢的準星移動。
"""

from typing import Tuple, Optional
import math


class AimController:
    """
    PD 控制器，計算平滑的滑鼠移動向量

    控制邏輯:
    1. 計算誤差: error = target - cursor
    2. PD 輸出: output = Kp * error + Kd * (error - prev_error) / dt
    3. α-β 平滑: smoothed = alpha * output + (1 - alpha) * prev_output
    4. 限制最大速度
    5. 死區檢查
    """

    def __init__(
        self,
        kp: float = 0.15,
        kd: float = 0.05,
        alpha: float = 0.85,
        dead_zone: float = 5.0,
        max_speed: float = 30.0
    ):
        """
        初始化控制器

        Args:
            kp: 比例係數 (Proportional gain)
            kd: 微分係數 (Derivative gain)
            alpha: 平滑係數 (0-1)，越高越平滑
            dead_zone: 死區半徑（像素），距離小於此值時不移動
            max_speed: 最大移動速度（像素/幀）
        """
        self.kp = kp
        self.kd = kd
        self.alpha = alpha
        self.dead_zone = dead_zone
        self.max_speed = max_speed

        # 內部狀態
        self.prev_error_x: float = 0.0
        self.prev_error_y: float = 0.0
        self.prev_output_x: float = 0.0
        self.prev_output_y: float = 0.0

    def compute(
        self,
        cursor_pos: Tuple[float, float],
        target_pos: Tuple[float, float],
        dt: float = 1.0
    ) -> Tuple[float, float]:
        """
        計算滑鼠移動向量

        Args:
            cursor_pos: 目前滑鼠位置 (x, y)
            target_pos: 目標位置 (x, y)
            dt: 時間間隔（幀），預設為 1

        Returns:
            移動向量 (dx, dy)
        """
        cursor_x, cursor_y = cursor_pos
        target_x, target_y = target_pos

        # 1. 計算誤差
        error_x = target_x - cursor_x
        error_y = target_y - cursor_y

        # 2. 計算距離，檢查死區
        distance = math.sqrt(error_x ** 2 + error_y ** 2)
        if distance < self.dead_zone:
            # 在死區內，不移動
            self.prev_error_x = error_x
            self.prev_error_y = error_y
            return (0.0, 0.0)

        # 3. PD 控制器
        # P 項
        p_x = self.kp * error_x
        p_y = self.kp * error_y

        # D 項
        d_x = self.kd * (error_x - self.prev_error_x) / dt
        d_y = self.kd * (error_y - self.prev_error_y) / dt

        # PD 輸出
        output_x = p_x + d_x
        output_y = p_y + d_y

        # 4. α-β 平滑
        smoothed_x = self.alpha * output_x + (1 - self.alpha) * self.prev_output_x
        smoothed_y = self.alpha * output_y + (1 - self.alpha) * self.prev_output_y

        # 5. 限制最大速度
        speed = math.sqrt(smoothed_x ** 2 + smoothed_y ** 2)
        if speed > self.max_speed:
            scale = self.max_speed / speed
            smoothed_x *= scale
            smoothed_y *= scale

        # 更新內部狀態
        self.prev_error_x = error_x
        self.prev_error_y = error_y
        self.prev_output_x = smoothed_x
        self.prev_output_y = smoothed_y

        return (smoothed_x, smoothed_y)

    def reset(self):
        """重置控制器狀態"""
        self.prev_error_x = 0.0
        self.prev_error_y = 0.0
        self.prev_output_x = 0.0
        self.prev_output_y = 0.0

    def update_params(
        self,
        kp: Optional[float] = None,
        kd: Optional[float] = None,
        alpha: Optional[float] = None,
        dead_zone: Optional[float] = None,
        max_speed: Optional[float] = None
    ):
        """
        動態更新控制器參數

        Args:
            kp: 比例係數
            kd: 微分係數
            alpha: 平滑係數
            dead_zone: 死區半徑
            max_speed: 最大速度
        """
        if kp is not None:
            self.kp = kp
        if kd is not None:
            self.kd = kd
        if alpha is not None:
            self.alpha = alpha
        if dead_zone is not None:
            self.dead_zone = dead_zone
        if max_speed is not None:
            self.max_speed = max_speed


# 測試用
if __name__ == "__main__":
    print("測試 PD 控制器模組...")

    controller = AimController(
        kp=0.15,
        kd=0.05,
        alpha=0.85,
        dead_zone=5,
        max_speed=30
    )

    # 模擬準星從 (0, 0) 移動到 (100, 100)
    cursor_x, cursor_y = 0.0, 0.0
    target_x, target_y = 100.0, 100.0

    print(f"\n目標位置: ({target_x}, {target_y})")
    print(f"起始位置: ({cursor_x}, {cursor_y})")
    print("\n模擬移動過程:")

    for i in range(20):
        dx, dy = controller.compute(
            cursor_pos=(cursor_x, cursor_y),
            target_pos=(target_x, target_y)
        )

        cursor_x += dx
        cursor_y += dy

        distance = math.sqrt((target_x - cursor_x) ** 2 + (target_y - cursor_y) ** 2)
        print(f"  幀 {i+1:2d}: pos=({cursor_x:6.2f}, {cursor_y:6.2f}) "
              f"delta=({dx:6.2f}, {dy:6.2f}) 距離={distance:.2f}")

        if distance < controller.dead_zone:
            print(f"\n已進入死區，停止移動")
            break
