# Aim Assist System

基於 YOLOv11n 的 2D 遊戲輔助瞄準系統，專為研究與教學用途設計。

> ⚠️ **免責聲明**: 本系統僅供研究、教學與技術展示用途，不鼓勵、不支援任何形式的遊戲作弊行為。

## 功能特色

- 🎯 **即時敵人偵測**: 使用 YOLOv11n 模型進行高效能目標偵測
- 🖱️ **平滑準星移動**: PD 控制器 + α-β 平滑演算法，避免瞬移
- 🖼️ **透明 Overlay**: 顯示偵測框、FPS、延遲等資訊
- ⚡ **低延遲**: GPU 推論 ~3ms，端到端延遲 <100ms
- ⚙️ **可調參數**: 透過 YAML 設定檔自訂控制器行為

## 系統需求

- **作業系統**: Linux (需要 X11 顯示環境)
- **Python**: 3.8+
- **GPU**: NVIDIA GPU (支援 CUDA 12.x)
- **螢幕解析度**: 1920×1080

## 安裝

### 1. 建立虛擬環境

```bash
cd /home/hjc/coSpace/CV_final/AimAssistSystem
python3 -m venv venv
source venv/bin/activate
```

### 2. 安裝依賴

```bash
pip install -r requirements.txt
```

### 3. 確認 GPU 可用

```bash
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
```

## 使用方式

### 啟動系統

```bash
source venv/bin/activate
python main.py
```

### 命令列參數

```bash
# 使用自訂設定檔
python main.py --config custom_config.yaml

# 不顯示 Overlay（除錯用）
python main.py --no-overlay
```

### 操作說明

1. 開啟瀏覽器，進入 [ZombsRoyale.io](https://zombsroyale.io)
2. 將遊戲設為全螢幕 (1920×1080)
3. 執行 `python main.py`
4. 按 `T` 開啟 Aim Assist
5. 系統會自動偵測敵人並平滑移動滑鼠

### 快捷鍵

| 按鍵 | 功能 |
|------|------|
| `T` | 切換 Aim Assist 開關 |
| `ESC` | 退出程式 |

## 設定檔

編輯 `config.yaml` 調整系統行為：

```yaml
# 控制器參數（影響準星移動手感）
controller:
  kp: 0.15        # 比例係數（越高越快，但可能抖動）
  kd: 0.05        # 微分係數（抑制震盪）
  alpha: 0.85     # 平滑係數（越高越平滑）
  dead_zone: 5    # 死區半徑（像素）
  max_speed: 30   # 最大移動速度（像素/幀）

# 偵測設定
detection:
  confidence_threshold: 0.5  # 信心閾值
  device: "cuda"             # cuda 或 cpu
```

### 參數調整建議

| 目標 | 調整方式 |
|------|---------|
| 更快吸附 | 提高 `kp`、降低 `alpha` |
| 更平滑 | 降低 `kp`、提高 `alpha` |
| 減少抖動 | 提高 `dead_zone`、提高 `alpha` |

## 專案結構

```
AimAssistSystem/
├── main.py              # 主程式入口
├── config.yaml          # 設定檔
├── requirements.txt     # Python 依賴
├── SPEC.md              # 系統規格文件
│
├── core/                # 核心模組
│   ├── capture.py       # 螢幕擷取
│   ├── detector.py      # YOLO 推論
│   ├── target_selector.py  # 目標選擇
│   ├── controller.py    # PD 控制器
│   └── mouse_control.py # 滑鼠控制
│
├── overlay/             # UI 模組
│   └── hud.py           # 透明 Overlay
│
├── utils/               # 工具模組
│   ├── coordinate.py    # 座標轉換
│   └── logger.py        # 日誌記錄
│
└── logs/                # 日誌輸出
```

## 效能指標

在 RTX 3060 上測試：

| 指標 | 數值 |
|------|------|
| 模型推論時間 | ~3 ms |
| 端到端延遲 | <30 ms |
| 系統 FPS | >30 FPS |

## 日誌與分析

系統會自動在 `logs/` 目錄產生 CSV 日誌，包含：

- 每幀偵測數量
- 推論時間
- 總延遲
- FPS

可用於後續效能分析與研究。

## 疑難排解

### CUDA 不可用

```bash
# 檢查 NVIDIA 驅動
nvidia-smi

# 確認 PyTorch CUDA 版本相容
python -c "import torch; print(torch.version.cuda)"
```

### pynput/PyQt5 錯誤

確保在有 X11 顯示的環境下執行：

```bash
echo $DISPLAY  # 應該顯示 :0 或類似值
```

### 模型載入失敗

確認模型路徑正確：

```bash
ls -la /home/hjc/coSpace/CV_final/ModelTraining/models/enemy_detection_v11n/best.pt
```

## 授權

本專案僅供學術研究與教學用途。
