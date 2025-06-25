# Zeabur 部署說明

## 部署配置

本專案已配置為使用 Zeabur 進行部署，無需 Docker。應用程式會同時運行 web 服務器和交易機器人。

### 配置文件

- `Procfile` - 指定啟動命令 (`python main.py`)
- `requirements.txt` - Python 依賴項
- `runtime.txt` - Python 版本
- `nixpacks.toml` - Nixpacks 構建配置
- `zeabur.toml` - Zeabur 部署配置

### 啟動流程

1. `main.py` - 主入口點
2. `simple_start.py` - 啟動 web 服務器和交易機器人

### 環境變數

在 Zeabur 的 Variables 部分設置以下環境變數：

#### 必需的 API 密鑰
- `GATEIO_API_KEY` - Gate.io API 金鑰
- `GATEIO_SECRET_KEY` - Gate.io 密鑰
- `BITGET_API_KEY` - Bitget API 金鑰
- `BITGET_SECRET_KEY` - Bitget 密鑰
- `BITGET_API_PASSPHRASE` - Bitget API 密碼

#### 可選的配置環境變數
- `TRADING_PAIRS` - 交易對列表（JSON 格式）
- `MIN_FUNDING_RATE_DIFFERENCE` - 最小資金費率差（預設 0.10）
- `MAX_PRICE_SPREAD` - 最大價格偏差（預設 0.005）
- `POSITION_SIZE_USDT` - 倉位大小（預設 100.0）
- `MAX_TOTAL_EXPOSURE_USDT` - 最大總風險敞口（預設 1000.0）
- `TEST_MODE` - 測試模式（預設 true）

### 部署步驟

1. 將代碼推送到 Git 倉庫
2. 在 Zeabur 中連接 Git 倉庫
3. 設置環境變數
4. 部署應用程式

### 服務說明

#### Web 服務器
- 端口：由 `PORT` 環境變數指定（預設 8080）
- 功能：提供交易歷史、資金費率分析、配置管理
- 端點：
  - `/` - 主頁（交易歷史）
  - `/funding-rates` - 資金費率分析
  - `/config` - 配置管理
  - `/health` - 健康檢查

#### 交易機器人
- 運行在背景線程中
- 功能：自動執行資金費率套利交易
- 配置：通過 web 界面或環境變數管理
- 日誌：與 web 服務器共享日誌輸出

### 故障排除

如果部署失敗，請檢查：

1. 所有必要的文件是否存在
2. 環境變數是否正確設置
3. 依賴項是否正確安裝
4. API 金鑰是否有效
5. 網絡連接是否正常

### 監控

- 通過 web 界面監控交易狀態
- 查看 Zeabur 日誌了解運行狀況
- 使用 `/health` 端點檢查服務狀態 