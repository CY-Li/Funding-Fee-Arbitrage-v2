#!/usr/bin/env python3
"""
調試啟動腳本 - 提供詳細的錯誤信息
"""

import os
import sys
import logging
import traceback

# 設定詳細的日誌
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

def main():
    try:
        logging.info("=== 開始調試啟動 ===")
        
        # 檢查環境變數
        port = os.environ.get('PORT', 8080)
        logging.info(f"PORT: {port}")
        logging.info(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")
        
        # 檢查當前目錄
        logging.info(f"Current directory: {os.getcwd()}")
        logging.info(f"Files in current directory: {os.listdir('.')}")
        
        # 檢查 Python 版本
        logging.info(f"Python version: {sys.version}")
        
        # 檢查必要的檔案
        required_files = ['web_server.py', 'config.py', 'requirements.txt']
        for file in required_files:
            if os.path.exists(file):
                logging.info(f"✓ {file} exists")
                logging.info(f"  Size: {os.path.getsize(file)} bytes")
            else:
                logging.error(f"✗ {file} missing")
                return 1
        
        # 嘗試導入模組
        logging.info("Testing imports...")
        
        try:
            import config
            logging.info("✓ config module imported successfully")
        except Exception as e:
            logging.error(f"✗ Failed to import config: {e}")
            logging.error(traceback.format_exc())
            return 1
        
        try:
            from web_server import app
            logging.info("✓ web_server module imported successfully")
        except Exception as e:
            logging.error(f"✗ Failed to import web_server: {e}")
            logging.error(traceback.format_exc())
            return 1
        
        # 測試 Flask 應用程式
        logging.info("Testing Flask application...")
        try:
            with app.test_client() as client:
                response = client.get('/health')
                logging.info(f"Health check response: {response.status_code}")
                if response.status_code == 200:
                    logging.info("✓ Flask application is working")
                else:
                    logging.error(f"✗ Health check failed: {response.status_code}")
                    return 1
        except Exception as e:
            logging.error(f"✗ Flask test failed: {e}")
            logging.error(traceback.format_exc())
            return 1
        
        logging.info("=== 調試完成，應用程式準備就緒 ===")
        return 0
        
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        logging.error(traceback.format_exc())
        return 1

if __name__ == '__main__':
    sys.exit(main()) 