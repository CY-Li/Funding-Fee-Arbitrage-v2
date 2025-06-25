import time
import logging
import ccxt
import os
import pandas as pd

import config
from utils import trade_logger
from exchanges.base_api import get_market_data

# --- Configuration Monitoring ---
last_config_check = 0
config_check_interval = 30  # Check for config updates every 30 seconds

def check_config_updates():
    """Check if configuration has been updated and reload if necessary."""
    global last_config_check
    
    current_time = time.time()
    if current_time - last_config_check < config_check_interval:
        return
    
    last_config_check = current_time
    
    try:
        config_file = 'config_update.timestamp'
        if os.path.exists(config_file):
            logging.info("Configuration update detected, reloading config...")
            config.reload_config()
            logging.info(f"Config reloaded. New MAX_HOLDING_DURATION_HOURS: {config.MAX_HOLDING_DURATION_HOURS}")
            
            # Remove the notification file
            os.remove(config_file)
                
    except Exception as e:
        logging.error(f"Error checking config updates: {e}")

# --- Position Management ---
# A simple dictionary to track our open positions.
# In a more advanced system, this would be a class or persisted to a database.
# Format: { 'SNT/USDT': {'short_on': 'gateio', 'long_on': 'bitget'} }
open_positions = {}

def rebuild_state_from_history():
    """
    Rebuilds the in-memory 'open_positions' state from the trade history file
    on startup. This makes the bot resilient to restarts.
    """
    global open_positions
    trade_history_file = 'trading_history.csv'
    try:
        if not os.path.exists(trade_history_file):
            logging.info("No trading history file found. Starting with a clean state.")
            return

        df = pd.read_csv(trade_history_file)
        if df.empty:
            logging.info("Trading history is empty. Starting with a clean state.")
            return

        logging.info("Rebuilding state from trading history...")
        if 'trade_id' not in df.columns or 'action' not in df.columns:
            logging.warning("History file is missing 'trade_id' or 'action' column. Cannot rebuild state.")
            return
        
        trades_by_id = df.dropna(subset=['trade_id']).groupby('trade_id')
        rebuilt_count = 0
        for trade_id, group in trades_by_id:
            # If a trade_id group does not contain a 'CLOSE' action, it's considered open.
            is_open = 'CLOSE' not in group['action'].values
            
            if is_open and 'OPEN' in group['action'].values:
                open_trade = group[group['action'] == 'OPEN'].iloc[-1]
                pair = open_trade['pair']
                
                open_positions[pair] = {
                    'short_on': open_trade['short_exchange'],
                    'long_on': open_trade['long_exchange'],
                    'size': float(open_trade['size_usdt']),
                    'open_short_price': float(open_trade['short_price']),
                    'open_long_price': float(open_trade['long_price']),
                    'trade_id': trade_id,
                    'open_timestamp': pd.to_datetime(open_trade['timestamp_utc']).timestamp(),
                    'initial_rate_difference': float(open_trade['funding_rate_diff_annualized_percent']) / 100.0
                }
                rebuilt_count += 1
                logging.info(f"Rebuilt open position for {pair} with trade_id {trade_id}")
        
        if rebuilt_count > 0:
            logging.info(f"Successfully rebuilt {rebuilt_count} open positions. Current state: {list(open_positions.keys())}")
        else:
            logging.info("No open positions to rebuild from history.")

    except Exception as e:
        logging.error(f"CRITICAL: Failed to rebuild state from history: {e}", exc_info=True)
        open_positions = {}
        logging.info("State has been reset due to an error during rebuild.")

def execute_trade(action, exchange_name, pair, position_size):
    """A centralized function to handle trade execution logging."""
    if config.TEST_MODE:
        logging.info(f"TEST MODE: Would {action.upper()} {pair} on {exchange_name} for {position_size} USDT.")
        return True
    else:
        logging.warning(f"LIVE MODE: Executing {action.upper()} {pair} on {exchange_name}.")
        # TODO: Add real order execution logic here using the exchange clients.
        return False # Placeholder

def open_arbitrage_position(pair, short_exchange_name, long_exchange_name, position_size, gate_data, bitget_data, rate_difference):
    """Opens a new arbitrage position and logs the event."""
    logging.info(f"Attempting to OPEN position for {pair}...")
    
    short_success = execute_trade('short', short_exchange_name, pair, position_size)
    long_success = execute_trade('long', long_exchange_name, pair, position_size)

    if short_success and long_success:
        logging.info(f"Successfully OPENED position for {pair}.")
        
        short_price = gate_data['mark_price']
        long_price = bitget_data['mark_price'] if long_exchange_name.lower() == 'bitget' else gate_data['mark_price']
        
        trade_id = f"{pair}_{int(time.time())}"
        
        open_positions[pair] = {
            'short_on': short_exchange_name,
            'long_on': long_exchange_name,
            'size': position_size,
            'open_short_price': short_price,
            'open_long_price': long_price,
            'trade_id': trade_id,
            'open_timestamp': time.time(),
            'initial_rate_difference': rate_difference
        }
        
        trade_logger.log_trade(
            pair=pair, action='OPEN', short_exchange=short_exchange_name, 
            long_exchange=long_exchange_name, size_usdt=position_size, 
            short_price=short_price, long_price=long_price, 
            rate_diff=rate_difference, trade_id=trade_id
        )
        return True
    else:
        logging.error(f"Failed to fully open position for {pair}. Manual intervention may be required.")
        return False

def close_arbitrage_position(pair, reason, close_short_price, close_long_price, realized_pnl, funding_fee_profit):
    """Closes an open position and logs the trade."""
    if pair not in open_positions:
        logging.error(f"Attempted to close a position that does not exist: {pair}")
        return

    position = open_positions[pair]
    logging.info(f"Closing position for {pair}. Reason: {reason}. PnL: ${realized_pnl:.2f}. Funding Profit: ${funding_fee_profit:.2f}")

    # Log the closing trade
    trade_logger.log_trade(
        pair=pair,
        action='CLOSE',
        short_exchange=position['short_on'],
        long_exchange=position['long_on'],
        size_usdt=position['size'],
        short_price=close_short_price,
        long_price=close_long_price,
        rate_diff=position['initial_rate_difference'],
        close_reason=reason,
        realized_pnl=realized_pnl,
        funding_fee_profit=funding_fee_profit,
        trade_id=position['trade_id']
    )

    # Remove from open positions
    del open_positions[pair]

def count_funding_events(open_timestamp, close_timestamp):
    """
    Counts the number of funding settlement events (00, 08, 16 UTC) between two timestamps.
    """
    # The number of 8-hour intervals since the epoch.
    start_event_num = open_timestamp // (8 * 3600)
    end_event_num = close_timestamp // (8 * 3600)

    # The actual timestamp of the first funding event *at or after* the position opened.
    first_event_ts = (start_event_num + 1) * (8 * 3600)
    
    # If the closing time is before the very first settlement time, no fees were paid.
    if close_timestamp < first_event_ts:
        return 0
        
    return int(end_event_num - start_event_num)

def calculate_funding_fee_profit(position, current_annual_rate_diff, close_timestamp):
    """
    Calculates the estimated profit from funding fees more accurately.
    - Counts the actual number of funding events.
    - Averages the funding rate between the start and end of the trade.
    - Uses the arbitrage rate (short - long) for profit calculation.
    """
    # 1. Count the number of funding fee settlement events
    num_events = count_funding_events(position['open_timestamp'], close_timestamp)

    if num_events == 0:
        return 0.0

    # 2. Calculate current arbitrage rate based on position direction
    # position['initial_rate_difference'] is already the arbitrage rate (short - long)
    # We need to calculate current arbitrage rate in the same direction
    if position['short_on'] == 'Gate.io':
        # Short Gate.io, Long Bitget: arbitrage_rate = Gate.io_rate - Bitget_rate
        current_arbitrage_rate = current_annual_rate_diff
    else:
        # Short Bitget, Long Gate.io: arbitrage_rate = Bitget_rate - Gate.io_rate = -(Gate.io_rate - Bitget_rate)
        current_arbitrage_rate = -current_annual_rate_diff

    # 3. Average the start and end arbitrage rates for a better estimate
    avg_arbitrage_rate = (position['initial_rate_difference'] + current_arbitrage_rate) / 2

    # 4. De-annualize the rate to get the rate per 8-hour event
    rate_per_event = avg_arbitrage_rate / (365 * 3)

    # 5. Calculate total profit
    funding_fee_profit = position['size'] * rate_per_event * num_events
    
    return funding_fee_profit

def check_and_manage_positions(pair, gate_data, bitget_data):
    """Checks if an open position should be closed, or if a new one should be opened."""
    
    gate_annual_rate = gate_data['funding_rate'] * 3 * 365
    bitget_annual_rate = bitget_data['funding_rate'] * 3 * 365
    rate_difference = gate_annual_rate - bitget_annual_rate
    
    current_short_price = gate_data['mark_price']
    current_long_price = bitget_data['mark_price']

    # --- Step 1: Manage existing positions ---
    if pair in open_positions:
        position = open_positions[pair]
        logging.info(f"Managing existing position for {pair}.")
        
        # Pre-calculate metrics for closing checks
        unrealized_pnl = trade_logger.calculate_realized_pnl(
            position['open_short_price'], position['open_long_price'],
            current_short_price, current_long_price, position['size']
        )
        
        holding_duration_hours = (time.time() - position['open_timestamp']) / 3600
        current_price_spread = abs(current_short_price - current_long_price) / current_short_price

        # Check if the sign of the rate difference has flipped
        # 由於現在記錄的是套利費率（總是正值），需要根據持倉方向來判斷反轉
        if position['short_on'] == 'Gate.io':
            # 原本做空 Gate.io，做多 Bitget
            # 如果現在 Gate.io 費率 < Bitget 費率，表示反轉了
            rate_reversal = rate_difference < 0
        else:
            # 原本做空 Bitget，做多 Gate.io
            # 如果現在 Bitget 費率 < Gate.io 費率，表示反轉了
            rate_reversal = rate_difference > 0

        close_timestamp = time.time()
        funding_fee_profit = calculate_funding_fee_profit(position, rate_difference, close_timestamp)

        logging.info(f"Position Metrics | Unrealized PnL: ${unrealized_pnl:.2f}, Holding Time: {holding_duration_hours:.2f}h, Price Spread: {current_price_spread:.2%}, Rate Diff: {rate_difference:.2%}, Funding Profit: ${funding_fee_profit:.2f}")
        logging.info(f"Closing Conditions | Max Holding: {config.MAX_HOLDING_DURATION_HOURS}h, Min Reversal: {config.MIN_HOLDING_HOURS_FOR_REVERSAL}h, Stop Loss: ${config.STOP_LOSS_USDT}")

        # Closing Condition Checks (in order of priority)
        if unrealized_pnl <= config.STOP_LOSS_USDT:
            logging.info(f"Closing {pair} due to STOP_LOSS: ${unrealized_pnl:.2f} <= ${config.STOP_LOSS_USDT}")
            close_arbitrage_position(pair, "STOP_LOSS", current_short_price, current_long_price, unrealized_pnl, funding_fee_profit)
            return

        # 檢查當前套利費率是否低於平倉閾值
        current_arbitrage_rate = abs(rate_difference)
        if current_arbitrage_rate <= config.CLOSE_FUNDING_RATE_DIFFERENCE:
            logging.info(f"Closing {pair} due to LOW_ARBITRAGE_RATE: {current_arbitrage_rate:.2%} <= {config.CLOSE_FUNDING_RATE_DIFFERENCE:.2%}")
            close_arbitrage_position(pair, "LOW_ARBITRAGE_RATE", current_short_price, current_long_price, unrealized_pnl, funding_fee_profit)
            return

        # 檢查持倉期間的價格偏差是否超過限制
        if current_price_spread > config.MAX_HOLDING_PRICE_SPREAD:
            logging.info(f"Closing {pair} due to MAX_HOLDING_PRICE_SPREAD: {current_price_spread:.2%} > {config.MAX_HOLDING_PRICE_SPREAD:.2%}")
            close_arbitrage_position(pair, "MAX_HOLDING_PRICE_SPREAD", current_short_price, current_long_price, unrealized_pnl, funding_fee_profit)
            return

        if rate_reversal and holding_duration_hours > config.MIN_HOLDING_HOURS_FOR_REVERSAL:
            logging.info(f"Closing {pair} due to RATE_REVERSAL: {holding_duration_hours:.2f}h > {config.MIN_HOLDING_HOURS_FOR_REVERSAL}h")
            close_arbitrage_position(pair, "RATE_REVERSAL", current_short_price, current_long_price, unrealized_pnl, funding_fee_profit)
            return

        if holding_duration_hours >= config.MAX_HOLDING_DURATION_HOURS:
            logging.info(f"Closing {pair} due to MAX_HOLDING_TIME: {holding_duration_hours:.2f}h >= {config.MAX_HOLDING_DURATION_HOURS}h")
            close_arbitrage_position(pair, "MAX_HOLDING_TIME", current_short_price, current_long_price, unrealized_pnl, funding_fee_profit)
            return
        else:
            logging.info(f"Position {pair} not ready to close: {holding_duration_hours:.2f}h < {config.MAX_HOLDING_DURATION_HOURS}h")

    # --- Step 2: Look for new positions to open ---
    if pair not in open_positions:
        price_spread = abs(gate_data['mark_price'] - bitget_data['mark_price']) / gate_data['mark_price']
        
        logging.info(f"Prices | Gate.io Mark: {current_short_price}, Bitget Mark: {current_long_price}, Spread: {price_spread:.2%}")

        # 檢查總風險敞口是否超過限制
        total_exposure = sum(position['size'] for position in open_positions.values())
        if total_exposure + config.POSITION_SIZE_USDT > config.MAX_TOTAL_EXPOSURE_USDT:
            logging.info(f"Skipping {pair} due to MAX_TOTAL_EXPOSURE: ${total_exposure + config.POSITION_SIZE_USDT:.2f} > ${config.MAX_TOTAL_EXPOSURE_USDT}")
            return

        if abs(rate_difference) >= config.MIN_FUNDING_RATE_DIFFERENCE and price_spread <= config.MAX_PRICE_SPREAD:
            logging.info("!!! NEW ARBITRAGE OPPORTUNITY DETECTED !!!")
            if rate_difference > 0: # Gate rate is higher, short Gate, long Bitget
                # 做空 Gate.io，做多 Bitget：獲得的年化費率差 = Gate.io費率 - Bitget費率 = 正值
                arbitrage_rate = rate_difference
                open_arbitrage_position(pair, "Gate.io", "Bitget", config.POSITION_SIZE_USDT, gate_data, bitget_data, arbitrage_rate)
            else: # Bitget rate is higher, short Bitget, long Gate
                # 做空 Bitget，做多 Gate.io：獲得的年化費率差 = Bitget費率 - Gate.io費率 = 正值
                arbitrage_rate = -rate_difference
                open_arbitrage_position(pair, "Bitget", "Gate.io", config.POSITION_SIZE_USDT, gate_data, bitget_data, arbitrage_rate)
        else:
            logging.info("No profitable arbitrage opportunity found.")

def main():
    """The main function to run the trading bot."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("Starting trading bot...")

    # Load config
    config.reload_config()

    # Initialize trade log file
    trade_logger.initialize_trade_log()

    # Rebuild state from history before doing anything else
    rebuild_state_from_history()

    # Initialize exchanges
    gateio_exchange = getattr(ccxt, 'gateio')({
        'apiKey': config.GATEIO_API_KEY,
        'secret': config.GATEIO_SECRET_KEY,
        'options': {
            'defaultType': 'swap',
            'adjustForTimeDifference': True,
        },
    })

    bitget_exchange = getattr(ccxt, 'bitget')({
        'apiKey': config.BITGET_API_KEY,
        'secret': config.BITGET_SECRET_KEY,
        'password': config.BITGET_API_PASSPHRASE,
        'options': {
            'defaultType': 'swap',
            'adjustForTimeDifference': True,
        },
    })

    # Load markets to ensure all symbols are available
    try:
        logging.info("Loading markets for all exchanges...")
        gateio_exchange.load_markets()
        bitget_exchange.load_markets()
        logging.info("Markets loaded successfully.")
    except ccxt.BaseError as e:
        logging.error(f"Failed to load markets: {e}")
        return

    while True:
        try:
            # Check for configuration updates
            check_config_updates()
            
            logging.info("--- New iteration ---")
            for pair in config.TRADING_PAIRS:
                logging.info(f"----- Checking pair: {pair} -----")
                ccxt_swap_symbol = f"{pair}:USDT"
                gate_market_data = get_market_data(gateio_exchange, ccxt_swap_symbol)
                bitget_market_data = get_market_data(bitget_exchange, ccxt_swap_symbol)
                if not gate_market_data or not bitget_market_data:
                    logging.warning(f"Incomplete data for {pair}, skipping management for this cycle.")
                    continue
                check_and_manage_positions(pair, gate_market_data, bitget_market_data)
            logging.info(f"--- Iteration complete. Sleeping for {config.LOOP_INTERVAL_SECONDS} seconds... ---")
            time.sleep(config.LOOP_INTERVAL_SECONDS)
        except KeyboardInterrupt:
            logging.info("Trading bot stopped by user.")
            break
        except Exception as e:
            logging.error(f"An unexpected error occurred in the main loop: {e}", exc_info=True)
            time.sleep(60)

if __name__ == '__main__':
    main() 