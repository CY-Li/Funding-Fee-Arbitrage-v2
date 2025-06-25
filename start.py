#!/usr/bin/env python3
"""
簡單的啟動腳本 - 用於 Zeabur 部署調試
"""

import os
import sys
import logging

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

def main():
    try:
        logging.info("Starting application...")
        
        # 檢查環境變數
        port = os.environ.get('PORT', 8080)
        logging.info(f"PORT environment variable: {port}")
        
        # 檢查必要的檔案是否存在
        required_files = ['web_server.py', 'config.py', 'requirements.txt']
        for file in required_files:
            if os.path.exists(file):
                logging.info(f"✓ {file} exists")
            else:
                logging.error(f"✗ {file} missing")
                return 1
        
        # 導入並啟動 Flask 應用
        logging.info("Importing Flask application...")
        from web_server import app
        
        logging.info("Starting Flask server...")
        app.run(host='0.0.0.0', port=int(port), debug=False)
        
    except Exception as e:
        logging.error(f"Error starting application: {e}", exc_info=True)
        return 1

if __name__ == '__main__':
    sys.exit(main()) 