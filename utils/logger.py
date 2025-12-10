"""
日誌記錄模組 (Logger Module)

負責記錄系統運行狀態和效能數據。
"""

import os
import csv
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict


@dataclass
class LogEntry:
    """日誌條目"""
    timestamp: str
    frame_id: int
    aim_assist_enabled: bool
    detection_count: int
    inference_time_ms: float
    total_latency_ms: float
    fps: float
    locked_target_x: Optional[float] = None
    locked_target_y: Optional[float] = None


class Logger:
    """日誌記錄器"""

    def __init__(
        self,
        output_dir: str = "./logs",
        enabled: bool = True,
        log_interval: int = 1
    ):
        """
        初始化日誌記錄器

        Args:
            output_dir: 日誌輸出目錄
            enabled: 是否啟用日誌
            log_interval: 每 N 幀記錄一次
        """
        self.output_dir = output_dir
        self.enabled = enabled
        self.log_interval = log_interval

        self.frame_count = 0
        self.entries: List[LogEntry] = []
        self.session_start: Optional[datetime] = None
        self.csv_file: Optional[str] = None

        if enabled:
            self._setup()

    def _setup(self):
        """設定日誌環境"""
        # 建立輸出目錄
        os.makedirs(self.output_dir, exist_ok=True)

        # 建立日誌檔案名稱
        self.session_start = datetime.now()
        timestamp = self.session_start.strftime("%Y%m%d_%H%M%S")
        self.csv_file = os.path.join(self.output_dir, f"session_{timestamp}.csv")

        # 寫入 CSV 標頭
        with open(self.csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'timestamp', 'frame_id', 'aim_assist_enabled',
                'detection_count', 'inference_time_ms', 'total_latency_ms',
                'fps', 'locked_target_x', 'locked_target_y'
            ])

        print(f"日誌檔案: {self.csv_file}")

    def log(
        self,
        aim_assist_enabled: bool,
        detection_count: int,
        inference_time_ms: float,
        total_latency_ms: float,
        fps: float,
        locked_target_x: Optional[float] = None,
        locked_target_y: Optional[float] = None
    ):
        """
        記錄一筆日誌

        Args:
            aim_assist_enabled: Aim Assist 是否啟用
            detection_count: 偵測數量
            inference_time_ms: 推論時間（毫秒）
            total_latency_ms: 總延遲（毫秒）
            fps: 當前 FPS
            locked_target_x: 鎖定目標 x 座標
            locked_target_y: 鎖定目標 y 座標
        """
        if not self.enabled:
            return

        self.frame_count += 1

        # 根據 log_interval 決定是否記錄
        if self.frame_count % self.log_interval != 0:
            return

        entry = LogEntry(
            timestamp=datetime.now().isoformat(),
            frame_id=self.frame_count,
            aim_assist_enabled=aim_assist_enabled,
            detection_count=detection_count,
            inference_time_ms=inference_time_ms,
            total_latency_ms=total_latency_ms,
            fps=fps,
            locked_target_x=locked_target_x,
            locked_target_y=locked_target_y
        )

        self.entries.append(entry)

        # 寫入 CSV
        self._write_entry(entry)

    def _write_entry(self, entry: LogEntry):
        """寫入單筆日誌到 CSV"""
        if not self.csv_file:
            return

        with open(self.csv_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                entry.timestamp,
                entry.frame_id,
                entry.aim_assist_enabled,
                entry.detection_count,
                entry.inference_time_ms,
                entry.total_latency_ms,
                entry.fps,
                entry.locked_target_x,
                entry.locked_target_y
            ])

    def get_statistics(self) -> Dict[str, Any]:
        """
        取得統計資料

        Returns:
            統計資料字典
        """
        if not self.entries:
            return {}

        inference_times = [e.inference_time_ms for e in self.entries]
        latencies = [e.total_latency_ms for e in self.entries]
        fps_values = [e.fps for e in self.entries]

        return {
            'total_frames': self.frame_count,
            'logged_entries': len(self.entries),
            'avg_inference_time_ms': sum(inference_times) / len(inference_times),
            'max_inference_time_ms': max(inference_times),
            'min_inference_time_ms': min(inference_times),
            'avg_latency_ms': sum(latencies) / len(latencies),
            'max_latency_ms': max(latencies),
            'min_latency_ms': min(latencies),
            'avg_fps': sum(fps_values) / len(fps_values),
        }

    def save_summary(self):
        """儲存摘要報告"""
        if not self.enabled or not self.entries:
            return

        stats = self.get_statistics()
        summary_file = os.path.join(
            self.output_dir,
            f"summary_{self.session_start.strftime('%Y%m%d_%H%M%S')}.json"
        )

        with open(summary_file, 'w') as f:
            json.dump(stats, f, indent=2)

        print(f"摘要報告: {summary_file}")

    def close(self):
        """關閉日誌記錄器並儲存摘要"""
        if self.enabled:
            self.save_summary()


# 測試用
if __name__ == "__main__":
    import time
    import random

    print("測試日誌記錄模組...")

    logger = Logger(output_dir="./logs", enabled=True, log_interval=1)

    # 模擬記錄
    for i in range(100):
        logger.log(
            aim_assist_enabled=True,
            detection_count=random.randint(0, 5),
            inference_time_ms=random.uniform(15, 30),
            total_latency_ms=random.uniform(30, 80),
            fps=random.uniform(25, 35),
            locked_target_x=random.uniform(0, 1920) if random.random() > 0.3 else None,
            locked_target_y=random.uniform(0, 1080) if random.random() > 0.3 else None
        )

    # 顯示統計
    stats = logger.get_statistics()
    print("\n統計資料:")
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")

    logger.close()
    print("\n測試完成!")
