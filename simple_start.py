#!/usr/bin/env python3
import os
import sys
import logging
import threading
import time
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

def update_funding_data():
    """Update funding rate data directly"""
    try:
        from web_server import (
            get_common_symbols, fetch_gate_rates, fetch_bitget_rates,
            filter_to_settlement_times, perform_analysis,
            ANALYSIS_JSON, RAW_DATA_CSV
        )
        import json
        import csv
        
        logging.info("Starting funding rate data update...")
        
        common_symbols = get_common_symbols()
        if not common_symbols:
            logging.error("No common symbols found")
            return False

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
        
        return True
        
    except Exception as e:
        logging.error(f"Error updating funding data: {e}")
        return False

def run_funding_rate_updater():
    """Run funding rate data updater - updates every hour"""
    try:
        time.sleep(10)  # Wait for web server to start
        logging.info("Starting funding rate data updater (hourly updates)")
        
        while True:
            try:
                logging.info("Starting hourly funding rate data update...")
                
                success = update_funding_data()
                if success:
                    logging.info("Hourly funding rate update completed successfully")
                else:
                    logging.error("Hourly funding rate update failed")
                        
            except Exception as e:
                logging.error(f"Error in hourly funding rate update: {e}")
            
            # Wait for 1 hour (3600 seconds) before next update
            logging.info("Waiting 1 hour until next funding rate update...")
            time.sleep(3600)
            
    except Exception as e:
        logging.error(f"Funding rate updater error: {e}")

def main():
    logging.info("Starting application...")
    
    # Start trading bot in background
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Start funding rate updater in background
    updater_thread = threading.Thread(target=run_funding_rate_updater, daemon=True)
    updater_thread.start()
    
    # Run web server in main thread
    run_web()

if __name__ == '__main__':
    main() 