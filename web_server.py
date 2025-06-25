import os
import pandas as pd
import numpy as np
from flask import Flask, jsonify, render_template, abort, request
import logging
import config
import requests
import csv
import time
import json
from datetime import datetime, timedelta
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Health check endpoint
@app.route('/health')
def health_check():
    """Simple health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Application is running'})

# Define the path to the CSV file
# This assumes web_server.py is run from the project root directory
TRADE_HISTORY_FILE = 'trading_history.csv'

# --- Funding Rate Analysis Constants ---
GATE_CONTRACTS_ENDPOINT = "https://api.gateio.ws/api/v4/futures/usdt/contracts"
BITGET_CONTRACTS_ENDPOINT = "https://api.bitget.com/api/mix/v1/market/contracts?productType=umcbl"
GATE_FUNDING_ENDPOINT = "https://api.gateio.ws/api/v4/futures/usdt/funding_rate"
BITGET_FUNDING_ENDPOINT = "https://api.bitget.com/api/mix/v1/market/history-fundRate"
RAW_DATA_CSV = "all_funding_rates.csv"
ANALYSIS_JSON = "analysis_summary.json"
OPPORTUNITY_THRESHOLD = 0.0001  # 0.01%

# --- Time Range ---
now = int(time.time())
start_time = now - 30 * 24 * 60 * 60

# --- Helper Functions for Funding Rate Analysis ---
def get_common_symbols():
    """Fetch all USDT perpetual symbols from Gate.io and Bitget and find the common ones."""
    try:
        # Gate.io symbols (format: BTC_USDT)
        r_gate = requests.get(GATE_CONTRACTS_ENDPOINT, timeout=10)
        r_gate.raise_for_status()
        gate_symbols = {c['name'].replace('_', '') for c in r_gate.json()}

        # Bitget symbols (format: BTCUSDT)
        r_bitget = requests.get(BITGET_CONTRACTS_ENDPOINT, timeout=10)
        r_bitget.raise_for_status()
        bitget_symbols = {c['symbolName'] for c in r_bitget.json().get('data', [])}
        
        common = sorted(list(gate_symbols.intersection(bitget_symbols)))
        logging.info(f"Found {len(common)} common symbols.")
        return common
    except Exception as e:
        logging.error(f"Error fetching symbols: {e}")
        return []

def fetch_gate_rates(symbol):
    """Fetch funding rates for a specific symbol from Gate.io."""
    params = {'contract': f"{symbol[:-4]}_{symbol[-4:]}", 'limit': 1000, 'start_time': start_time}
    try:
        r = requests.get(GATE_FUNDING_ENDPOINT, params=params, timeout=10)
        if r.status_code != 200: return []
        return [
            {'symbol': symbol, 'exchange': 'gateio', 'timestamp': datetime.utcfromtimestamp(e['t']).isoformat() + 'Z', 'funding_rate': e['r']}
            for e in r.json()
        ]
    except Exception:
        return []

def fetch_bitget_rates(symbol):
    """Fetch funding rates for a specific symbol from Bitget."""
    params = {'symbol': f"{symbol}_UMCBL", 'pageSize': 100, 'pageNo': 1, 'startTime': start_time * 1000}
    try:
        r = requests.get(BITGET_FUNDING_ENDPOINT, params=params, timeout=10)
        if r.status_code != 200 or not r.json().get('data'): return []
        return [
            {'symbol': symbol, 'exchange': 'bitget', 'timestamp': datetime.utcfromtimestamp(int(e['settleTime']) / 1000).isoformat() + 'Z', 'funding_rate': e['fundingRate']}
            for e in r.json()['data']
        ]
    except Exception:
        return []

def filter_to_settlement_times(data):
    """Filter data to keep only the record closest to each settlement time (00, 08, 16 UTC)."""
    def round_to_nearest_8h(dt):
        hour = dt.hour
        nearest = min([0, 8, 16], key=lambda h: abs(hour - h))
        return dt.replace(hour=nearest, minute=0, second=0, microsecond=0)

    grouped = defaultdict(list)
    for row in data:
        dt = datetime.fromisoformat(row['timestamp'].replace('Z', ''))
        slot_dt = round_to_nearest_8h(dt)
        key = (row['symbol'], row['exchange'], slot_dt.date(), slot_dt.hour)
        grouped[key].append((abs((dt - slot_dt).total_seconds()), row))

    filtered = []
    for v in grouped.values():
        v.sort(key=lambda x: x[0])
        filtered.append(v[0][1])
    return filtered

def perform_analysis(data):
    """Perform analysis on funding rate data."""
    analysis_results = []
    data_by_symbol = defaultdict(list)
    for row in data:
        data_by_symbol[row['symbol']].append(row)

    for symbol, rows in data_by_symbol.items():
        grouped_by_ts = defaultdict(dict)
        for row in rows:
            grouped_by_ts[row['timestamp']][row['exchange']] = float(row['funding_rate'])
        
        diffs = [exchanges['bitget'] - exchanges['gateio'] for exchanges in grouped_by_ts.values() if 'gateio' in exchanges and 'bitget' in exchanges]
        if not diffs: continue

        count = len(diffs)
        mean_abs_diff = sum(map(abs, diffs)) / count
        avg_annualized_return = mean_abs_diff * 3 * 365
        
        variance = sum([(d - (sum(diffs) / count))**2 for d in diffs]) / count
        std_dev = variance**0.5
        
        opportunity_count = sum(1 for d in diffs if abs(d) > OPPORTUNITY_THRESHOLD)
        opportunity_freq = opportunity_count / count

        analysis_results.append({
            "symbol": symbol,
            "avg_annualized_return": avg_annualized_return,
            "opportunity_frequency": opportunity_freq,
            "std_dev": std_dev,
            "data_points": count
        })
    
    analysis_results.sort(key=lambda x: x['avg_annualized_return'], reverse=True)
    return analysis_results

def load_funding_data():
    """Load existing funding rate data from files."""
    analysis_data = []
    raw_data = []
    
    # Load analysis summary
    if os.path.exists(ANALYSIS_JSON):
        try:
            with open(ANALYSIS_JSON, 'r', encoding='utf-8') as f:
                analysis_data = json.load(f)
            logging.info(f"Loaded analysis data for {len(analysis_data)} symbols")
        except Exception as e:
            logging.error(f"Error loading analysis data: {e}")
    
    # Load raw data
    if os.path.exists(RAW_DATA_CSV):
        try:
            with open(RAW_DATA_CSV, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                raw_data = list(reader)
            logging.info(f"Loaded raw data: {len(raw_data)} records")
        except Exception as e:
            logging.error(f"Error loading raw data: {e}")
    
    return analysis_data, raw_data

def get_trade_data():
    """讀取並處理交易歷史數據"""
    if not os.path.exists(TRADE_HISTORY_FILE):
        logging.info(f"'{TRADE_HISTORY_FILE}' not found. This is normal for first run or test mode.")
        return pd.DataFrame()
    
    try:
        df = pd.read_csv(TRADE_HISTORY_FILE)
        logging.info(f"Loaded CSV. Shape: {df.shape}. Columns: {df.columns.tolist()}")
        
        if df.empty:
            logging.info("CSV is empty after loading.")
            return df
        
        # 檢查必要的欄位是否存在
        required_columns = ['timestamp_utc', 'pair', 'action']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logging.error(f"Missing required columns in CSV: {missing_columns}")
            logging.error(f"Available columns: {df.columns.tolist()}")
            return pd.DataFrame()
            
        # --- 向下兼容處理 ---
        # 確保所有新版欄位都存在，若不存在則補上空值
        for col in ['trade_id', 'close_reason', 'realized_pnl']:
            if col not in df.columns:
                df[col] = pd.NA
        
        # 填充空的 trade_id，以便識別和處理舊紀錄
        legacy_mask = df['trade_id'].isna()
        num_legacy = legacy_mask.sum()
        if num_legacy > 0:
            # 為每個 legacy 紀錄生成一個唯一的 ID
            df.loc[legacy_mask, 'trade_id'] = [f'legacy_{i}' for i in range(num_legacy)]
        logging.info(f"Processed trade_ids. Found {num_legacy} legacy records.")

        # --- 數據清洗 ---
        # 確保時間欄位格式正確, 對於無法解析的日期，將其設為 NaT (Not a Time)
        original_rows = len(df)
        # 加上 utc=True，讓所有時間都變成有時區的 (tz-aware) UTC 時間
        df['timestamp_utc'] = pd.to_datetime(df['timestamp_utc'], errors='coerce', utc=True)
        
        # 移除時間格式不正確的損壞資料行
        df.dropna(subset=['timestamp_utc'], inplace=True)
        
        if len(df) < original_rows:
            logging.warning(f"Removed {original_rows - len(df)} rows with invalid datetime format from CSV.")

        if df.empty:
            logging.info("DataFrame is empty after removing corrupted rows.")
            return df

        # 按時間降序排序
        df = df.sort_values(by='timestamp_utc', ascending=False)
        
        # 將所有 NaN/NA 值替換為 None，以確保 JSON 兼容性
        df = df.replace({np.nan: None, pd.NA: None})

        return df
    except Exception as e:
        logging.error(f"CRITICAL: Error in get_trade_data: {e}", exc_info=True)
        return pd.DataFrame()

@app.route('/')
def index():
    """提供主頁面"""
    return render_template('index.html')

@app.route('/funding-rates')
def funding_rates():
    """提供資金費率分析頁面"""
    return render_template('funding_rates.html')

@app.route('/history/open')
def get_open_positions():
    """提供當前未平倉的交易"""
    df = get_trade_data()
    if df.empty:
        logging.info("get_open_positions: DataFrame is empty from get_trade_data.")
        return jsonify([])
    
    try:
        open_positions = []
        # 舊紀錄無法判斷是否為未平倉，因此直接排除
        trades_by_id = df[~df['trade_id'].astype(str).str.startswith('legacy_')].groupby('trade_id')
        
        for trade_id, group in trades_by_id:
            # 未平倉交易 = 只有一筆 OPEN 紀錄
            if len(group) == 1 and group.iloc[0]['action'] == 'OPEN':
                trade = group.iloc[0].to_dict()
                trade['holding_time'] = (pd.Timestamp.utcnow() - pd.Timestamp(trade['timestamp_utc'])).total_seconds() / 3600
                open_positions.append(trade)
        
        logging.info(f"Returning {len(open_positions)} open positions.")
        return jsonify(open_positions)
    except Exception as e:
        logging.error(f"Error processing open positions: {e}", exc_info=True)
        abort(500, description="Could not process open positions data.")

@app.route('/history/closed')
def get_closed_positions():
    """提供已平倉的交易"""
    df = get_trade_data()
    if df.empty:
        logging.info("get_closed_positions: DataFrame is empty from get_trade_data.")
        return jsonify([])
    
    try:
        closed_positions = []
        
        # 1. 將所有無法配對的舊紀錄視為已平倉
        legacy_trades = df[df['trade_id'].astype(str).str.startswith('legacy_')]
        for _, trade in legacy_trades.iterrows():
            position = trade.to_dict()
            # 由於是舊紀錄，我們不知道確切的開倉/平倉時間，只用一個時間戳
            position['time'] = position.pop('timestamp_utc') 
            position['close_reason'] = position.get('close_reason') or '舊紀錄 (無法配對)'
            
            # 補上新格式需要的欄位，但給予明確的空值或標記
            position['open_time'] = None
            position['close_time'] = position['time'] # 將主要時間戳視為平倉時間
            position['holding_time'] = -1 # 用-1作為標記，表示未知
            closed_positions.append(position)
        
        # 2. 處理有完整開/平倉紀錄的新交易
        trades_by_id = df[~df['trade_id'].astype(str).str.startswith('legacy_')].groupby('trade_id')
        
        for trade_id, group in trades_by_id:
            # 已平倉交易 = 有 OPEN 和 CLOSE 兩筆紀錄
            if len(group) == 2:
                open_trade_df = group[group['action'] == 'OPEN']
                close_trade_df = group[group['action'] == 'CLOSE']

                if not open_trade_df.empty and not close_trade_df.empty:
                    open_trade = open_trade_df.iloc[0]
                    close_trade = close_trade_df.iloc[0]
                    
                    position = {
                        'trade_id': trade_id,
                        'pair': open_trade['pair'],
                        'open_time': open_trade['timestamp_utc'],
                        'close_time': close_trade['timestamp_utc'],
                        'holding_time': (pd.Timestamp(close_trade['timestamp_utc']) - pd.Timestamp(open_trade['timestamp_utc'])).total_seconds() / 3600,
                        'short_exchange': open_trade['short_exchange'],
                        'long_exchange': open_trade['long_exchange'],
                        'size_usdt': open_trade['size_usdt'],
                        'open_short_price': open_trade['short_price'],
                        'open_long_price': open_trade['long_price'],
                        'close_short_price': close_trade['short_price'],
                        'close_long_price': close_trade['long_price'],
                        'open_funding_rate_diff': open_trade['funding_rate_diff_annualized_percent'],
                        'close_funding_rate_diff': close_trade['funding_rate_diff_annualized_percent'],
                        'close_reason': close_trade['close_reason'],
                        'realized_pnl': close_trade['realized_pnl'],
                        'funding_fee_profit': close_trade['funding_fee_profit']
                    }
                    closed_positions.append(position)
        
        # 3. 將所有已平倉紀錄按時間排序
        closed_positions.sort(key=lambda x: x['close_time'], reverse=True)
        logging.info(f"Returning {len(closed_positions)} closed positions ({len(legacy_trades)} legacy).")
        return jsonify(closed_positions)
    except Exception as e:
        logging.error(f"Error processing closed positions: {e}", exc_info=True)
        abort(500, description="Could not process closed positions data.")

# --- Funding Rate Analysis API Endpoints ---
@app.route('/api/analysis')
def get_analysis():
    """API endpoint to get analysis summary"""
    analysis_data, _ = load_funding_data()
    return jsonify(analysis_data)

@app.route('/api/raw-data/<symbol>')
def get_raw_data(symbol):
    """API endpoint to get raw funding rate data for a specific symbol"""
    _, raw_data = load_funding_data()
    
    # Filter data for the specific symbol
    symbol_data = [row for row in raw_data if row['symbol'] == symbol]
    
    # Group by timestamp
    grouped_data = defaultdict(dict)
    for row in symbol_data:
        timestamp = row['timestamp']
        exchange = row['exchange']
        rate = float(row['funding_rate'])
        grouped_data[timestamp][exchange] = rate
    
    # Convert to list format for frontend
    result = []
    for timestamp, exchanges in grouped_data.items():
        if 'gateio' in exchanges and 'bitget' in exchanges:
            diff = exchanges['bitget'] - exchanges['gateio']
            # 套利費率差：顯示做空-做多獲得的費率差
            arbitrage_rate_diff = abs(diff)  # 套利費率差總是正值
            annual_return = arbitrage_rate_diff * 3 * 365 * 100  # Convert to percentage
            
            result.append({
                'timestamp': timestamp,
                'bitget_rate': exchanges['bitget'] * 100,  # Convert to percentage
                'gateio_rate': exchanges['gateio'] * 100,  # Convert to percentage
                'difference': diff * 100,  # Convert to percentage (原始差異，可能為負)
                'abs_difference': arbitrage_rate_diff * 100,  # Convert to percentage (套利費率差)
                'annual_return': annual_return,
                'is_opportunity': arbitrage_rate_diff > OPPORTUNITY_THRESHOLD
            })
    
    # Sort by timestamp (newest first)
    result.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return jsonify(result)

@app.route('/api/update-data', methods=['POST'])
def update_data():
    """API endpoint to trigger data update"""
    try:
        logging.info("Starting funding rate data update...")
        
        common_symbols = get_common_symbols()
        if not common_symbols:
            return jsonify({'error': 'No common symbols found'}), 400

        all_raw_data = []
        for i, symbol in enumerate(common_symbols):
            logging.info(f"Fetching data for {symbol} ({i+1}/{len(common_symbols)})...")
            all_raw_data.extend(fetch_gate_rates(symbol))
            all_raw_data.extend(fetch_bitget_rates(symbol))
            time.sleep(0.2)  # To avoid hitting rate limits

        logging.info("Filtering data to settlement times...")
        filtered_data = filter_to_settlement_times(all_raw_data)
        
        logging.info("Performing analysis for each symbol...")
        analysis_summary = perform_analysis(filtered_data)
        
        # Save analysis summary
        with open(ANALYSIS_JSON, 'w', encoding='utf-8') as f:
            json.dump(analysis_summary, f, indent=4)
        logging.info(f"Saved analysis summary for {len(analysis_summary)} symbols")

        # Save raw data
        filtered_data.sort(key=lambda x: (x['symbol'], x['timestamp']), reverse=True)
        with open(RAW_DATA_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['symbol', 'exchange', 'timestamp', 'funding_rate'])
            writer.writeheader()
            writer.writerows(filtered_data)
        logging.info(f"Saved {len(filtered_data)} funding rate records")
        
        return jsonify({
            'success': True,
            'message': f'Updated data for {len(analysis_summary)} symbols',
            'analysis_count': len(analysis_summary),
            'raw_data_count': len(filtered_data)
        })
        
    except Exception as e:
        logging.error(f"Error updating data: {e}")
        return jsonify({'error': str(e)}), 500

# --- Configuration Management API Endpoints ---
@app.route('/config')
def config_page():
    """提供配置管理頁面"""
    return render_template('config.html')

@app.route('/api/config', methods=['GET'])
def get_config():
    """API endpoint to get current configuration"""
    try:
        config.load_config_from_file()
        config_data = {
            'MIN_FUNDING_RATE_DIFFERENCE': config.MIN_FUNDING_RATE_DIFFERENCE,
            'CLOSE_FUNDING_RATE_DIFFERENCE': config.CLOSE_FUNDING_RATE_DIFFERENCE,
            'MAX_PRICE_SPREAD': config.MAX_PRICE_SPREAD,
            'POSITION_SIZE_USDT': config.POSITION_SIZE_USDT,
            'MAX_TOTAL_EXPOSURE_USDT': config.MAX_TOTAL_EXPOSURE_USDT,
            'STOP_LOSS_USDT': config.STOP_LOSS_USDT,
            'MAX_HOLDING_PRICE_SPREAD': config.MAX_HOLDING_PRICE_SPREAD,
            'MAX_HOLDING_DURATION_HOURS': config.MAX_HOLDING_DURATION_HOURS,
            'MIN_HOLDING_HOURS_FOR_REVERSAL': config.MIN_HOLDING_HOURS_FOR_REVERSAL,
            'LOOP_INTERVAL_SECONDS': config.LOOP_INTERVAL_SECONDS,
            'TEST_MODE': config.TEST_MODE,
            'TRADING_PAIRS': config.TRADING_PAIRS,
            'WEB_SERVER_PORT': config.WEB_SERVER_PORT
        }
        return jsonify(config_data)
    except Exception as e:
        logging.error(f"Error getting config: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/config', methods=['POST'])
def update_config():
    """API endpoint to update configuration"""
    try:
        data = request.get_json()
        # Validate required fields
        required_fields = [
            'MIN_FUNDING_RATE_DIFFERENCE', 'CLOSE_FUNDING_RATE_DIFFERENCE',
            'MAX_PRICE_SPREAD', 'POSITION_SIZE_USDT', 'MAX_TOTAL_EXPOSURE_USDT',
            'STOP_LOSS_USDT', 'MAX_HOLDING_PRICE_SPREAD', 'MAX_HOLDING_DURATION_HOURS',
            'MIN_HOLDING_HOURS_FOR_REVERSAL', 'LOOP_INTERVAL_SECONDS', 'TEST_MODE', 'TRADING_PAIRS', 'WEB_SERVER_PORT'
        ]
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        # Save to config.json
        config.save_config_to_file({
            'MIN_FUNDING_RATE_DIFFERENCE': data['MIN_FUNDING_RATE_DIFFERENCE'],
            'CLOSE_FUNDING_RATE_DIFFERENCE': data['CLOSE_FUNDING_RATE_DIFFERENCE'],
            'MAX_PRICE_SPREAD': data['MAX_PRICE_SPREAD'],
            'POSITION_SIZE_USDT': data['POSITION_SIZE_USDT'],
            'MAX_TOTAL_EXPOSURE_USDT': data['MAX_TOTAL_EXPOSURE_USDT'],
            'STOP_LOSS_USDT': data['STOP_LOSS_USDT'],
            'MAX_HOLDING_PRICE_SPREAD': data['MAX_HOLDING_PRICE_SPREAD'],
            'MAX_HOLDING_DURATION_HOURS': data['MAX_HOLDING_DURATION_HOURS'],
            'MIN_HOLDING_HOURS_FOR_REVERSAL': data['MIN_HOLDING_HOURS_FOR_REVERSAL'],
            'LOOP_INTERVAL_SECONDS': data['LOOP_INTERVAL_SECONDS'],
            'TEST_MODE': data['TEST_MODE'],
            'TRADING_PAIRS': data['TRADING_PAIRS'],
            'WEB_SERVER_PORT': data['WEB_SERVER_PORT']
        })
        # Create a config update notification file
        with open('config_update.timestamp', 'w') as f:
            f.write(str(time.time()))
        # Reload configuration to apply changes (for web server process)
        config.reload_config()
        logging.info("Configuration updated successfully")
        return jsonify({'success': True, 'message': 'Configuration updated successfully'})
    except Exception as e:
        logging.error(f"Error updating config: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Use 0.0.0.0 to make it accessible in a container environment like Zeabur
    # The port is now controlled by the PORT environment variable via Procfile and config.py
    app.run(host='0.0.0.0', port=config.WEB_SERVER_PORT, debug=False) 