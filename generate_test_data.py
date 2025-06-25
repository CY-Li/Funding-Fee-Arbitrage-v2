#!/usr/bin/env python3
"""
測試數據生成腳本
生成一些符合條件的交易記錄，用於測試前端顯示
"""

import csv
import os
from datetime import datetime, timedelta
import random

def generate_test_trades():
    """生成測試交易記錄"""
    
    # 確保交易日誌文件存在
    from utils.trade_logger import initialize_trade_log
    initialize_trade_log()
    
    # 測試交易對
    pairs = ["FUN/USDT", "SNT/USDT", "RSS3/USDT", "BADGER/USDT", "JST/USDT"]
    
    # 生成一些開倉記錄
    open_trades = []
    for i, pair in enumerate(pairs):
        # 生成隨機的資金費率差異（確保大於 10%）
        rate_diff = random.uniform(0.12, 0.25)  # 12% - 25%
        
        # 生成隨機價格
        base_price = random.uniform(0.01, 1.0)
        short_price = base_price * (1 + random.uniform(-0.001, 0.001))
        long_price = base_price * (1 + random.uniform(-0.001, 0.001))
        
        # 生成時間戳（最近 24 小時內）
        timestamp = datetime.utcnow() - timedelta(hours=random.uniform(1, 24))
        
        trade_id = f"{pair}_{int(timestamp.timestamp())}"
        
        open_trade = {
            'timestamp_utc': timestamp.isoformat(),
            'pair': pair,
            'action': 'OPEN',
            'short_exchange': 'Gate.io',
            'long_exchange': 'Bitget',
            'size_usdt': 100.0,
            'short_price': f"{short_price:.6f}",
            'long_price': f"{long_price:.6f}",
            'funding_rate_diff_annualized_percent': f"{rate_diff*100:.4f}",
            'close_reason': '',
            'realized_pnl': '',
            'funding_fee_profit': '',
            'trade_id': trade_id
        }
        open_trades.append(open_trade)
    
    # 生成一些平倉記錄
    closed_trades = []
    for i in range(3):  # 只為前 3 個交易生成平倉記錄
        open_trade = open_trades[i]
        
        # 生成平倉時間（開倉後 2-8 小時）
        close_time = datetime.fromisoformat(open_trade['timestamp_utc']) + timedelta(hours=random.uniform(2, 8))
        
        # 生成平倉價格（稍微偏離開倉價格）
        open_short_price = float(open_trade['short_price'])
        open_long_price = float(open_trade['long_price'])
        
        close_short_price = open_short_price * (1 + random.uniform(-0.02, 0.02))
        close_long_price = open_long_price * (1 + random.uniform(-0.02, 0.02))
        
        # 計算已實現損益
        from utils.trade_logger import calculate_realized_pnl
        realized_pnl = calculate_realized_pnl(
            open_short_price, open_long_price,
            close_short_price, close_long_price,
            100.0
        )
        
        # 生成資金費率套利收益
        funding_fee_profit = random.uniform(0.5, 2.0)
        
        close_trade = {
            'timestamp_utc': close_time.isoformat(),
            'pair': open_trade['pair'],
            'action': 'CLOSE',
            'short_exchange': open_trade['short_exchange'],
            'long_exchange': open_trade['long_exchange'],
            'size_usdt': open_trade['size_usdt'],
            'short_price': f"{close_short_price:.6f}",
            'long_price': f"{close_long_price:.6f}",
            'funding_rate_diff_annualized_percent': f"{random.uniform(0.02, 0.05)*100:.4f}",
            'close_reason': random.choice(['RATE_REVERSAL', 'MAX_HOLDING_TIME', 'LOW_ARBITRAGE_RATE']),
            'realized_pnl': f"{realized_pnl:.2f}",
            'funding_fee_profit': f"{funding_fee_profit:.2f}",
            'trade_id': open_trade['trade_id']
        }
        closed_trades.append(close_trade)
    
    # 寫入 CSV 文件
    all_trades = open_trades + closed_trades
    
    # 按時間排序
    all_trades.sort(key=lambda x: x['timestamp_utc'], reverse=True)
    
    with open('trading_history.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'timestamp_utc', 'pair', 'action', 'short_exchange', 'long_exchange',
            'size_usdt', 'short_price', 'long_price', 'funding_rate_diff_annualized_percent',
            'close_reason', 'realized_pnl', 'funding_fee_profit', 'trade_id'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_trades)
    
    print(f"已生成 {len(open_trades)} 條開倉記錄和 {len(closed_trades)} 條平倉記錄")
    print("測試數據已寫入 trading_history.csv")
    
    # 顯示統計信息
    print("\n=== 生成的交易統計 ===")
    print(f"總交易記錄: {len(all_trades)}")
    print(f"開倉記錄: {len(open_trades)}")
    print(f"平倉記錄: {len(closed_trades)}")
    print(f"未平倉交易: {len(open_trades) - len(closed_trades)}")
    
    # 顯示收益統計
    total_realized_pnl = sum(float(trade['realized_pnl']) for trade in closed_trades if trade['realized_pnl'])
    total_funding_profit = sum(float(trade['funding_fee_profit']) for trade in closed_trades if trade['funding_fee_profit'])
    total_profit = total_realized_pnl + total_funding_profit
    
    print(f"\n=== 收益統計 ===")
    print(f"已實現損益: ${total_realized_pnl:.2f}")
    print(f"資金費率套利收益: ${total_funding_profit:.2f}")
    print(f"總收益: ${total_profit:.2f}")

if __name__ == '__main__':
    generate_test_trades() 