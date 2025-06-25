#!/usr/bin/env python3
"""
主入口文件 - 用於 Zeabur 部署
啟動 Flask web 服務器
"""

import os
import sys
from web_server import app

if __name__ == '__main__':
    # 從環境變數獲取端口，Zeabur 會自動設置 PORT 環境變數
    port = int(os.environ.get('PORT', 8080))
    
    # 啟動 Flask 應用
    app.run(host='0.0.0.0', port=port, debug=False) 