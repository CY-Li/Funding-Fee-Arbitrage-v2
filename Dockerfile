# 使用官方的 Python 3.10 slim 版本作為基礎映像檔
FROM python:3.10-slim-bullseye

# 設定容器內的工作目錄
WORKDIR /app

# 設定環境變數，防止 Python 生成 .pyc 檔案，並確保日誌直接輸出
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 更新 pip 並安裝依賴
# 首先只複製 requirements.txt 來利用 Docker 的層快取機制
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 將專案中的所有檔案複製到工作目錄
COPY . .

# Zeabur 會使用儀表板中設定的啟動指令覆蓋這個 CMD。
# 這裡只提供一個預設值。
CMD ["/bin/bash"] 