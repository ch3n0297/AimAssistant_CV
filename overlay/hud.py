"""
Overlay HUD 模組 (Overlay Window Module)

負責在遊戲畫面上方顯示透明的偵測框和狀態資訊。
使用 PyQt5 實現透明視窗。
"""

import sys
from typing import List, Optional, Callable, TYPE_CHECKING
from dataclasses import dataclass
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QTimer, QRect
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QBrush

# 為了避免循環 import，使用 TYPE_CHECKING
if TYPE_CHECKING:
    from core.detector import Detection


# 如果無法 import Detection，定義一個簡單的 Protocol
@dataclass
class DetectionLike:
    """Detection 的簡化版本，用於類型提示"""
    x1: float
    y1: float
    x2: float
    y2: float
    score: float
    class_id: int

    @property
    def center_x(self) -> float:
        return (self.x1 + self.x2) / 2

    @property
    def center_y(self) -> float:
        return (self.y1 + self.y2) / 2

    @property
    def width(self) -> float:
        return self.x2 - self.x1

    @property
    def height(self) -> float:
        return self.y2 - self.y1


# 使用 Union 類型，接受任何有這些屬性的物件
Detection = DetectionLike  # type alias for runtime


class OverlayWindow(QWidget):
    """透明 Overlay 視窗，用於顯示偵測框和狀態"""

    def __init__(
        self,
        width: int = 1920,
        height: int = 1080,
        parent=None
    ):
        """
        初始化 Overlay 視窗

        Args:
            width: 視窗寬度
            height: 視窗高度
            parent: 父視窗
        """
        super().__init__(parent)

        self.screen_width = width
        self.screen_height = height

        # 偵測結果
        self.detections: List[Detection] = []
        self.locked_target: Optional[Detection] = None

        # 狀態資訊
        self.fps: float = 0.0
        self.latency_ms: float = 0.0
        self.aim_enabled: bool = False

        # 顯示設定
        self.show_all_boxes: bool = True
        self.show_fps: bool = True
        self.show_latency: bool = True

        # 設定視窗屬性
        self._setup_window()

    def _setup_window(self):
        """設定視窗屬性"""
        # 設定視窗大小和位置
        self.setGeometry(0, 0, self.screen_width, self.screen_height)

        # 設定視窗標誌
        self.setWindowFlags(
            Qt.FramelessWindowHint |      # 無邊框
            Qt.WindowStaysOnTopHint |     # 置頂
            Qt.Tool |                     # 工具視窗（不在工作列顯示）
            Qt.WindowTransparentForInput  # 滑鼠穿透
        )

        # 設定透明背景
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

        # 設定視窗標題
        self.setWindowTitle("Aim Assist Overlay")

    def update_data(
        self,
        detections: List[Detection],
        locked_target: Optional[Detection],
        fps: float,
        latency_ms: float,
        aim_enabled: bool
    ):
        """
        更新顯示資料

        Args:
            detections: 所有偵測結果（螢幕座標）
            locked_target: 鎖定的目標
            fps: 當前 FPS
            latency_ms: 延遲毫秒數
            aim_enabled: Aim Assist 是否啟用
        """
        self.detections = detections
        self.locked_target = locked_target
        self.fps = fps
        self.latency_ms = latency_ms
        self.aim_enabled = aim_enabled

        # 觸發重繪
        self.update()

    def paintEvent(self, event):
        """繪製事件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 繪製偵測框
        if self.show_all_boxes:
            self._draw_detections(painter)

        # 繪製鎖定目標框
        self._draw_locked_target(painter)

        # 繪製狀態資訊
        self._draw_status(painter)

        painter.end()

    def _draw_detections(self, painter: QPainter):
        """繪製所有偵測框"""
        # 設定綠色邊框
        pen = QPen(QColor(0, 255, 0, 200))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)

        for det in self.detections:
            # 跳過鎖定目標（會單獨繪製）
            if self.locked_target and self._is_same_detection(det, self.locked_target):
                continue

            rect = QRect(
                int(det.x1),
                int(det.y1),
                int(det.width),
                int(det.height)
            )
            painter.drawRect(rect)

            # 繪製信心分數
            painter.setFont(QFont("Arial", 10))
            painter.drawText(
                int(det.x1),
                int(det.y1) - 5,
                f"{det.score:.2f}"
            )

    def _draw_locked_target(self, painter: QPainter):
        """繪製鎖定目標框"""
        if not self.locked_target:
            return

        det = self.locked_target

        # 設定紅色粗邊框
        pen = QPen(QColor(255, 0, 0, 255))
        pen.setWidth(3)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)

        rect = QRect(
            int(det.x1),
            int(det.y1),
            int(det.width),
            int(det.height)
        )
        painter.drawRect(rect)

        # 繪製中心點
        center_x = int(det.center_x)
        center_y = int(det.center_y)
        painter.drawLine(center_x - 10, center_y, center_x + 10, center_y)
        painter.drawLine(center_x, center_y - 10, center_x, center_y + 10)

        # 繪製 "LOCKED" 標籤
        painter.setFont(QFont("Arial", 12, QFont.Bold))
        painter.drawText(
            int(det.x1),
            int(det.y1) - 8,
            "LOCKED"
        )

    def _draw_status(self, painter: QPainter):
        """繪製狀態資訊"""
        # 設定字體和顏色
        painter.setFont(QFont("Consolas", 14, QFont.Bold))

        # 背景半透明黑色
        bg_brush = QBrush(QColor(0, 0, 0, 150))

        # 狀態文字
        status_text = "AIM: ON" if self.aim_enabled else "AIM: OFF"
        status_color = QColor(0, 255, 0) if self.aim_enabled else QColor(255, 0, 0)

        lines = [status_text]

        if self.show_fps:
            lines.append(f"FPS: {self.fps:.1f}")

        if self.show_latency:
            lines.append(f"Latency: {self.latency_ms:.1f}ms")

        lines.append(f"Targets: {len(self.detections)}")

        # 計算背景大小
        line_height = 22
        padding = 10
        max_width = 180
        total_height = len(lines) * line_height + padding * 2

        # 繪製背景
        bg_rect = QRect(10, 10, max_width, total_height)
        painter.fillRect(bg_rect, bg_brush)

        # 繪製文字
        y = 10 + padding + 15
        for i, line in enumerate(lines):
            if i == 0:
                painter.setPen(status_color)
            else:
                painter.setPen(QColor(255, 255, 255))
            painter.drawText(10 + padding, y, line)
            y += line_height

    def _is_same_detection(self, det1: Detection, det2: Detection) -> bool:
        """檢查兩個偵測是否相同"""
        return (
            abs(det1.x1 - det2.x1) < 1 and
            abs(det1.y1 - det2.y1) < 1 and
            abs(det1.x2 - det2.x2) < 1 and
            abs(det1.y2 - det2.y2) < 1
        )


class OverlayManager:
    """Overlay 管理器，用於非阻塞方式運行 Overlay"""

    def __init__(
        self,
        width: int = 1920,
        height: int = 1080
    ):
        """
        初始化 Overlay 管理器

        Args:
            width: 視窗寬度
            height: 視窗高度
        """
        self.width = width
        self.height = height
        self.app: Optional[QApplication] = None
        self.window: Optional[OverlayWindow] = None
        self._initialized = False

    def init(self):
        """初始化 Qt 應用程式和視窗"""
        if self._initialized:
            return

        # 檢查是否已有 QApplication 實例
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)

        self.window = OverlayWindow(self.width, self.height)
        self.window.show()
        self._initialized = True

    def update(
        self,
        detections: List[Detection],
        locked_target: Optional[Detection],
        fps: float,
        latency_ms: float,
        aim_enabled: bool
    ):
        """更新 Overlay 顯示"""
        if not self._initialized:
            self.init()

        self.window.update_data(
            detections=detections,
            locked_target=locked_target,
            fps=fps,
            latency_ms=latency_ms,
            aim_enabled=aim_enabled
        )

        # 處理 Qt 事件
        self.app.processEvents()

    def close(self):
        """關閉 Overlay"""
        if self.window:
            self.window.close()
        self._initialized = False


# 測試用
if __name__ == "__main__":
    import time
    import random

    print("測試 Overlay HUD 模組...")
    print("將顯示一個透明視窗，5 秒後自動關閉")

    app = QApplication(sys.argv)
    window = OverlayWindow(1920, 1080)
    window.show()

    # 模擬資料更新
    def update_mock_data():
        detections = []
        for _ in range(random.randint(0, 3)):
            x = random.randint(100, 1700)
            y = random.randint(100, 900)
            w = random.randint(50, 100)
            h = random.randint(50, 100)
            detections.append(Detection(
                x1=x, y1=y, x2=x+w, y2=y+h,
                score=random.uniform(0.5, 1.0),
                class_id=0
            ))

        locked = detections[0] if detections else None

        window.update_data(
            detections=detections,
            locked_target=locked,
            fps=random.uniform(25, 35),
            latency_ms=random.uniform(15, 50),
            aim_enabled=True
        )

    # 定時更新
    timer = QTimer()
    timer.timeout.connect(update_mock_data)
    timer.start(100)  # 每 100ms 更新一次

    # 5 秒後關閉
    QTimer.singleShot(5000, app.quit)

    app.exec_()
    print("測試完成!")
