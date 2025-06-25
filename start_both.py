#!/usr/bin/env python3
"""
啟動腳本 - 同時運行 web 服務器和交易機器人
"""

import os
import sys
import time
import logging
import subprocess
import threading
import signal

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

def run_web_server():
    """運行 web 服務器"""
    try:
        logging.info("Starting web server...")
        port = os.environ.get('PORT', 8080)
        cmd = [
            'gunicorn',
            '--bind', f'0.0.0.0:{port}',
            '--workers', '1',
            '--timeout', '120',
            'app:app'
        ]
        subprocess.run(cmd, check=True)
    except Exception as e:
        logging.error(f"Web server error: {e}")

def run_trading_bot():
    """運行交易機器人"""
    try:
        logging.info("Starting trading bot...")
        # 等待 web 服務器啟動
        time.sleep(5)
        subprocess.run([sys.executable, 'trading_bot.py'], check=True)
    except Exception as e:
        logging.error(f"Trading bot error: {e}")

def main():
    """主函數"""
    logging.info("Starting both web server and trading bot...")
    
    # 創建線程
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    bot_thread = threading.Thread(target=run_trading_bot, daemon=True)
    
    # 啟動線程
    web_thread.start()
    bot_thread.start()
    
    # 等待線程完成
    try:
        web_thread.join()
        bot_thread.join()
    except KeyboardInterrupt:
        logging.info("Received interrupt signal, shutting down...")
        sys.exit(0)

if __name__ == '__main__':
    main() 