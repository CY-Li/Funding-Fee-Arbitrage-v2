# Zeabur 部署檢查總結

## ✅ 已完成的檢查和修正

### 1. 專案結構檢查
- ✅ 主入口文件 `main.py` 已創建
- ✅ Web 服務器 `web_server.py` 存在
- ✅ 交易機器人 `trading_bot.py` 存在
- ✅ 配置模組 `config.py` 存在並已更新
- ✅ 依賴列表 `requirements.txt` 完整
- ✅ Docker 配置 `Dockerfile` 正確
- ✅ Docker 忽略文件 `.dockerignore` 已修正

### 2. 模組結構檢查
- ✅ `utils/__init__.py` 已創建
- ✅ `exchanges/__init__.py` 已創建
- ✅ 所有必要的 Python 模組都存在

### 3. 配置文件檢查
- ✅ `config.json` 存在且格式正確
- ✅ `config.py` 支持環境變數覆蓋
- ✅ 預設交易對列表已設置

### 4. 數據文件檢查
- ✅ `all_funding_rates.csv` 存在 (3.1MB)
- ✅ `analysis_summary.json` 存在 (93KB)

### 5. 模板文件檢查
- ✅ `templates/index.html` 存在
- ✅ `templates/funding_rates.html` 存在
- ✅ `templates/config.html` 存在

### 6. Docker 配置檢查
- ✅ `Dockerfile` 使用正確的 Python 3.10-slim 基礎映像
- ✅ `.dockerignore` 不再排除重要數據文件
- ✅ 啟動命令已更新為 `python main.py`

## 📋 部署步驟

### 1. 準備 Git 倉庫
```bash
git add .
git commit -m "Prepare for Zeabur deployment"
git push origin main
```

### 2. 在 Zeabur 創建服務
1. 登入 [Zeabur](https://zeabur.com/)
2. 創建新專案
3. 選擇 "Deploy your source code"
4. 連接你的 Git 倉庫
5. 選擇 Docker 部署方式

### 3. 創建兩個服務

#### Web 服務
- 服務名稱: `web`
- 啟動命令: `python main.py`
- 環境變數: 見下方

#### Worker 服務
- 服務名稱: `worker`
- 啟動命令: `python trading_bot.py`
- 環境變數: 見下方

### 4. 設置環境變數

#### 必需的 API 密鑰
```
GATEIO_API_KEY=你的_Gate.io_API_密鑰
GATEIO_SECRET_KEY=你的_Gate.io_密鑰
BITGET_API_KEY=你的_Bitget_API_密鑰
BITGET_SECRET_KEY=你的_Bitget_密鑰
BITGET_API_PASSPHRASE=你的_Bitget_密碼短語
```

#### 交易模式
```
TEST_MODE=False  # 設為 False 啟用實盤交易
```

#### 可選的策略參數
```
POSITION_SIZE_USDT=100.0
MIN_FUNDING_RATE_DIFFERENCE=0.10
MAX_PRICE_SPREAD=0.005
CLOSE_FUNDING_RATE_DIFFERENCE=0.02
STOP_LOSS_USDT=-2.0
MAX_HOLDING_DURATION_HOURS=168
MIN_HOLDING_HOURS_FOR_REVERSAL=4.0
MAX_HOLDING_PRICE_SPREAD=0.01
LOOP_INTERVAL_SECONDS=60
```

### 5. 部署
1. 保存所有環境變數設置
2. 重新部署兩個服務
3. 檢查服務狀態和日誌

## 🔍 部署後檢查

### Web 服務檢查
- 訪問提供的公共 URL
- 確認主頁能正常載入
- 測試資金費率分析頁面
- 測試配置管理頁面

### Worker 服務檢查
- 查看服務日誌
- 確認交易機器人正常啟動
- 檢查是否有錯誤訊息

## ⚠️ 注意事項

1. **API 密鑰安全**: 確保 API 密鑰只在 Zeabur 環境變數中設置，不要提交到 Git
2. **測試模式**: 首次部署建議保持 `TEST_MODE=True`，確認一切正常後再改為 `False`
3. **資金安全**: 實盤交易前請仔細檢查所有參數設置
4. **監控**: 部署後要定期檢查服務狀態和交易日誌

## 🆘 常見問題

### 服務無法啟動
- 檢查環境變數是否正確設置
- 查看服務日誌中的錯誤訊息
- 確認 API 密鑰是否有效

### 數據文件缺失
- 確認 `.dockerignore` 沒有排除重要文件
- 檢查 Git 倉庫是否包含所有必要文件

### 導入錯誤
- 確認所有 Python 模組都存在
- 檢查 `requirements.txt` 是否包含所有依賴

## 📞 支援

如果遇到部署問題，請檢查：
1. Zeabur 服務日誌
2. 環境變數設置
3. Git 倉庫內容完整性 