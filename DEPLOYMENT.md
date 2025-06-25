# Zeabur 部署說明

## 部署配置

本專案已配置為使用 Zeabur 進行部署，無需 Docker。

### 配置文件

- `Procfile` - 指定啟動命令
- `requirements.txt` - Python 依賴項
- `runtime.txt` - Python 版本
- `nixpacks.toml` - Nixpacks 構建配置
- `zeabur.toml` - Zeabur 部署配置

### 啟動命令

```bash
gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 app:app
```

### 環境變數

在 Zeabur 的 Variables 部分設置以下環境變數：

- `GATEIO_API_KEY` - Gate.io API 金鑰
- `GATEIO_SECRET_KEY` - Gate.io 密鑰
- `BITGET_API_KEY` - Bitget API 金鑰
- `BITGET_SECRET_KEY` - Bitget 密鑰
- `BITGET_API_PASSPHRASE` - Bitget API 密碼

### 部署步驟

1. 將代碼推送到 Git 倉庫
2. 在 Zeabur 中連接 Git 倉庫
3. 設置環境變數
4. 部署應用程式

### 故障排除

如果部署失敗，請檢查：

1. 所有必要的文件是否存在
2. 環境變數是否正確設置
3. 依賴項是否正確安裝
4. 端口是否正確綁定 