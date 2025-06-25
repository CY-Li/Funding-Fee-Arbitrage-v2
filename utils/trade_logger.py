import csv
import os
from datetime import datetime
import logging

LOG_FILE = 'trading_history.csv'
FIELDNAMES = [
    'timestamp_utc', 
    'pair', 
    'action', # OPEN or CLOSE
    'short_exchange', 
    'long_exchange', 
    'size_usdt',
    'short_price', # The price at which the action was taken
    'long_price', # The price at which the action was taken
    'funding_rate_diff_annualized_percent', # The rate diff at the time of the action
    'close_reason',  # 新增：平倉理由
    'realized_pnl',  # 新增：已實現損益
    'funding_fee_profit',  # 新增：資金費率套利收益
    'trade_id'       # 新增：用於追蹤開倉/平倉配對
]

def initialize_trade_log():
    """初始化交易日誌文件，如果不存在則創建空的 CSV 文件"""
    if not os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
                writer.writeheader()
            logging.info(f"Created empty trade log file: {LOG_FILE}")
        except Exception as e:
            logging.error(f"Failed to create trade log file: {e}")

def log_trade(pair, action, short_exchange, long_exchange, size_usdt, short_price, long_price, rate_diff, close_reason=None, realized_pnl=None, funding_fee_profit=None, trade_id=None):
    """Logs a trade event to the CSV file."""
    
    # 確保文件存在
    initialize_trade_log()
    
    file_exists = os.path.isfile(LOG_FILE)
    
    try:
        with open(LOG_FILE, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
            
            if not file_exists:
                writer.writeheader()
                
            if action == 'OPEN' and not trade_id:
                trade_id = f"{pair}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            writer.writerow({
                'timestamp_utc': datetime.utcnow().isoformat(),
                'pair': pair,
                'action': action.upper(),
                'short_exchange': short_exchange,
                'long_exchange': long_exchange,
                'size_usdt': size_usdt,
                'short_price': f"{short_price:.6f}",
                'long_price': f"{long_price:.6f}",
                'funding_rate_diff_annualized_percent': f"{rate_diff*100:.4f}",
                'close_reason': close_reason if action == 'CLOSE' else '',
                'realized_pnl': realized_pnl if action == 'CLOSE' else '',
                'funding_fee_profit': funding_fee_profit if action == 'CLOSE' else '',
                'trade_id': trade_id
            })
        logging.info(f"Successfully logged {action.upper()} action for {pair} to {LOG_FILE}")
    except IOError as e:
        logging.error(f"Error writing to trade log file: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred in log_trade: {e}", exc_info=True) 

def calculate_realized_pnl(open_short_price, open_long_price, 
                         close_short_price, close_long_price, 
                         position_size_usdt):
    """
    計算已實現損益
    
    計算公式：
    做空部分：(開倉價格 - 平倉價格) / 開倉價格 * 倉位大小
    做多部分：(平倉價格 - 開倉價格) / 開倉價格 * 倉位大小
    總收益 = 做空收益 + 做多收益
    """
    short_pnl = (open_short_price - close_short_price) / open_short_price * position_size_usdt
    long_pnl = (close_long_price - open_long_price) / open_long_price * position_size_usdt
    total_pnl = short_pnl + long_pnl
    return round(total_pnl, 2) 