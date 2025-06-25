#!/usr/bin/env python3
"""
整合應用程式 - 在主進程中同時運行 web 服務器和交易機器人
"""

import os
import sys
import time
import logging
import threading
import signal
from flask import Flask

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

def create_app():
    """創建 Flask 應用程式"""
    try:
        logging.info("Creating Flask application...")
        
        # 檢查必要的文件
        required_files = ['web_server.py', 'config.py']
        for file in required_files:
            if not os.path.exists(file):
                logging.error(f"Required file {file} not found")
                raise FileNotFoundError(f"Required file {file} not found")
            logging.info(f"✓ Found {file}")
        
        # 導入 web_server 模組
        logging.info("Importing web_server module...")
        from web_server import app
        
        logging.info("Flask application created successfully")
        return app
        
    except Exception as e:
        logging.error(f"Error creating Flask application: {e}", exc_info=True)
        raise

def run_trading_bot():
    """運行交易機器人"""
    try:
        logging.info("Starting trading bot in background...")
        
        # 檢查必要的文件
        if not os.path.exists('trading_bot.py'):
            logging.error("trading_bot.py not found")
            return
        
        # 導入並運行交易機器人
        import trading_bot
        
        # 設置一個標誌來控制交易機器人的運行
        trading_bot.running = True
        
        # 運行交易機器人的主循環
        trading_bot.main()
        
    except Exception as e:
        logging.error(f"Trading bot error: {e}", exc_info=True)

def run_web_server(app):
    """運行 web 服務器"""
    try:
        logging.info("Starting web server...")
        port = int(os.environ.get('PORT', 8080))
        app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
    except Exception as e:
        logging.error(f"Web server error: {e}", exc_info=True)

def signal_handler(signum, frame):
    """信號處理器"""
    logging.info(f"Received signal {signum}, shutting down...")
    sys.exit(0)

def main():
    """主函數"""
    logging.info("Starting integrated application...")
    
    # 設置信號處理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 創建 Flask 應用程式
    try:
        app = create_app()
        logging.info("Application instance created successfully")
    except Exception as e:
        logging.error(f"Failed to create application: {e}")
        sys.exit(1)
    
    # 啟動交易機器人線程
    bot_thread = threading.Thread(target=run_trading_bot, daemon=True)
    bot_thread.start()
    logging.info("Trading bot thread started")
    
    # 等待一下讓交易機器人初始化
    time.sleep(3)
    
    # 在主線程中運行 web 服務器
    try:
        run_web_server(app)
    except KeyboardInterrupt:
        logging.info("Received interrupt signal, shutting down...")
        sys.exit(0)

if __name__ == '__main__':
    main() 