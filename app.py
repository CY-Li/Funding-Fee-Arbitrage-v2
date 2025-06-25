#!/usr/bin/env python3
"""
簡化的 Flask 應用程式入口點 - 用於 Zeabur 部署
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

def create_app():
    """創建 Flask 應用程式"""
    try:
        logging.info("Creating Flask application...")
        
        # 導入 web_server 模組
        from web_server import app
        
        logging.info("Flask application created successfully")
        return app
        
    except Exception as e:
        logging.error(f"Error creating Flask application: {e}", exc_info=True)
        raise

# 創建應用程式實例
app = create_app()

if __name__ == '__main__':
    try:
        port = int(os.environ.get('PORT', 8080))
        logging.info(f"Starting server on port {port}")
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        logging.error(f"Error starting server: {e}", exc_info=True)
        sys.exit(1) 