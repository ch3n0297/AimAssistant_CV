"""
滑鼠控制模組 (Mouse Control Module)

負責控制系統滑鼠的移動。
使用 pynput 進行滑鼠控制。
"""

from typing import Tuple
from pynput.mouse import Controller as MouseControllerBase
from pynput.mouse import Button


class MouseController:
    """滑鼠控制器，負責移動系統滑鼠"""

    def __init__(self):
        """初始化滑鼠控制器"""
        self.mouse = MouseControllerBase()

    def get_position(self) -> Tuple[int, int]:
        """
        取得目前滑鼠位置

        Returns:
            (x, y) 滑鼠座標
        """
        return self.mouse.position

    def move_absolute(self, x: float, y: float):
        """
        移動滑鼠到絕對位置

        Args:
            x: 目標 x 座標
            y: 目標 y 座標
        """
        self.mouse.position = (int(x), int(y))

    def move_relative(self, dx: float, dy: float):
        """
        相對移動滑鼠

        Args:
            dx: x 方向移動量
            dy: y 方向移動量
        """
        # pynput 的 move 方法是相對移動
        self.mouse.move(int(round(dx)), int(round(dy)))

    def click(self, button: str = 'left'):
        """
        點擊滑鼠

        Args:
            button: 按鈕名稱 ('left', 'right', 'middle')
        """
        btn = {
            'left': Button.left,
            'right': Button.right,
            'middle': Button.middle
        }.get(button, Button.left)

        self.mouse.click(btn)


# 測試用
if __name__ == "__main__":
    import time

    print("測試滑鼠控制模組...")
    print("注意: 此測試會移動你的滑鼠!")
    print("按 Ctrl+C 取消測試\n")

    time.sleep(2)

    mouse = MouseController()

    # 取得目前位置
    start_pos = mouse.get_position()
    print(f"起始位置: {start_pos}")

    # 相對移動測試
    print("\n執行相對移動測試 (向右移動 100 像素)...")
    for i in range(10):
        mouse.move_relative(10, 0)
        time.sleep(0.05)

    current_pos = mouse.get_position()
    print(f"目前位置: {current_pos}")

    # 移回原位
    print("\n移回原位...")
    mouse.move_absolute(start_pos[0], start_pos[1])

    final_pos = mouse.get_position()
    print(f"最終位置: {final_pos}")

    print("\n測試完成!")
