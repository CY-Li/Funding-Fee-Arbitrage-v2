#!/usr/bin/env python3
import os
import sys
import logging
import threading
import time

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def init_deployment():
    """初始化部署數據"""
    try:
        import init_deployment
        init_deployment.init_deployment_data()
    except Exception as e:
        logging.warning(f"Failed to initialize deployment data: {e}")

def run_web():
    """Run web server"""
    try:
        from web_server import app
        port = int(os.environ.get('PORT', 8080))
        logging.info(f"Starting web server on port {port}")
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        logging.error(f"Web server error: {e}")

def run_bot():
    """Run trading bot"""
    try:
        time.sleep(5)  # Wait for web server to start
        logging.info("Starting trading bot")
        import trading_bot
        trading_bot.main()
    except Exception as e:
        logging.error(f"Trading bot error: {e}")

def main():
    logging.info("Starting application...")
    
    # 初始化部署數據
    init_deployment()
    
    # Start trading bot in background
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Run web server in main thread
    run_web()

if __name__ == '__main__':
    main() 