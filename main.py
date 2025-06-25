#!/usr/bin/env python3
"""
主入口文件 - 備用啟動點
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
    """主函數"""
    logging.info("Starting application from main.py...")
    
    # 檢查 simple_start.py 是否存在
    if os.path.exists('simple_start.py'):
        logging.info("Found simple_start.py, importing and running...")
        import simple_start
        simple_start.main()
    else:
        logging.error("simple_start.py not found!")
        sys.exit(1)

if __name__ == '__main__':
    main() 