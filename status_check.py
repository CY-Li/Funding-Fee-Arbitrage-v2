#!/usr/bin/env python3
"""
狀態檢查腳本
用於檢查系統的當前運行狀態
"""

import os
import json
import pandas as pd
from datetime import datetime
import config

def check_config():
    """檢查配置狀態"""
    print("=== 配置狀態 ===")
    print(f"測試模式: {config.TEST_MODE}")
    print(f"交易對數量: {len(config.TRADING_PAIRS)}")
    print(f"最小資金費率差: {config.MIN_FUNDING_RATE_DIFFERENCE:.2%}")
    print(f"平倉資金費率差: {config.CLOSE_FUNDING_RATE_DIFFERENCE:.2%}")
    print(f"倉位大小: ${config.POSITION_SIZE_USDT}")
    print(f"最大總敞口: ${config.MAX_TOTAL_EXPOSURE_USDT}")
    print(f"循環間隔: {config.LOOP_INTERVAL_SECONDS} 秒")
    print(f"Web 服務器端口: {config.WEB_SERVER_PORT}")
    
    # 檢查 API 密鑰
    print(f"\nAPI 密鑰狀態:")
    print(f"Gate.io API Key: {'已設置' if config.GATEIO_API_KEY else '未設置'}")
    print(f"Gate.io Secret: {'已設置' if config.GATEIO_SECRET_KEY else '未設置'}")
    print(f"Bitget API Key: {'已設置' if config.BITGET_API_KEY else '未設置'}")
    print(f"Bitget Secret: {'已設置' if config.BITGET_SECRET_KEY else '未設置'}")
    print(f"Bitget Passphrase: {'已設置' if config.BITGET_API_PASSPHRASE else '未設置'}")

def check_files():
    """檢查文件狀態"""
    print("\n=== 文件狀態 ===")
    
    files_to_check = [
        'config.json',
        'trading_history.csv',
        'main.py',
        'simple_start.py',
        'trading_bot.py',
        'web_server.py'
    ]
    
    for file in files_to_check:
        if os.path.exists(file):
            size = os.path.getsize(file)
            mtime = datetime.fromtimestamp(os.path.getmtime(file))
            print(f"✓ {file} - {size} bytes, 修改時間: {mtime}")
        else:
            print(f"✗ {file} - 不存在")

def check_trade_history():
    """檢查交易歷史"""
    print("\n=== 交易歷史狀態 ===")
    
    if not os.path.exists('trading_history.csv'):
        print("交易歷史文件不存在 - 這是正常的（首次運行或測試模式）")
        return
    
    try:
        df = pd.read_csv('trading_history.csv')
        print(f"交易記錄總數: {len(df)}")
        
        if not df.empty:
            # 統計開倉和平倉
            open_trades = df[df['action'] == 'OPEN']
            close_trades = df[df['action'] == 'CLOSE']
            
            print(f"開倉記錄: {len(open_trades)}")
            print(f"平倉記錄: {len(close_trades)}")
            
            # 檢查未平倉的交易
            if 'trade_id' in df.columns:
                trades_by_id = df.groupby('trade_id')
                open_positions = []
                for trade_id, group in trades_by_id:
                    if len(group) == 1 and group.iloc[0]['action'] == 'OPEN':
                        open_positions.append(group.iloc[0]['pair'])
                
                if open_positions:
                    print(f"當前未平倉交易: {open_positions}")
                else:
                    print("當前無未平倉交易")
            
            # 顯示最近的交易
            if len(df) > 0:
                latest_trade = df.iloc[0]
                print(f"最近交易: {latest_trade['pair']} - {latest_trade['action']} - {latest_trade['timestamp_utc']}")
        
    except Exception as e:
        print(f"讀取交易歷史時出錯: {e}")

def check_environment():
    """檢查環境變數"""
    print("\n=== 環境變數 ===")
    
    env_vars = [
        'GATEIO_API_KEY',
        'GATEIO_SECRET_KEY', 
        'BITGET_API_KEY',
        'BITGET_SECRET_KEY',
        'BITGET_API_PASSPHRASE',
        'TEST_MODE',
        'TRADING_PAIRS'
    ]
    
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            if 'KEY' in var or 'SECRET' in var or 'PASSPHRASE' in var:
                print(f"{var}: {'已設置'}")
            else:
                print(f"{var}: {value}")
        else:
            print(f"{var}: 未設置")

def main():
    """主函數"""
    print("資金費率套利系統狀態檢查")
    print("=" * 50)
    
    check_config()
    check_files()
    check_trade_history()
    check_environment()
    
    print("\n=== 總結 ===")
    if config.TEST_MODE:
        print("系統正在測試模式下運行 - 不會執行實際交易")
    else:
        print("系統正在實盤模式下運行 - 將執行實際交易")
    
    if not config.GATEIO_API_KEY or not config.BITGET_API_KEY:
        print("警告: API 密鑰未完全設置，系統可能無法正常工作")
    else:
        print("API 密鑰已設置，系統應該可以正常運行")

if __name__ == '__main__':
    main() 