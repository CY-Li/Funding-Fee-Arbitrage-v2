import logging
import ccxt

def get_market_data(api_client, symbol):
    """
    Fetches market data (ticker and funding rate) for a given symbol from a CCXT-compatible exchange.
    
    Args:
        api_client: An initialized CCXT API client instance.
        symbol: The contract symbol in CCXT format (e.g., 'SNT/USDT:USDT').

    Returns:
        A dictionary containing all relevant market data, or None if an error occurs.
    """
    if not api_client:
        logging.error(f"API client for {symbol} not initialized.")
        return None
        
    try:
        # The symbol format (e.g., SNT/USDT:USDT) should tell CCXT it's a swap market.
        ticker_data = api_client.fetch_ticker(symbol)
        funding_rate_data = api_client.fetch_funding_rate(symbol)
        
        market_data = {
            "funding_rate": funding_rate_data.get('fundingRate'),
            "mark_price": ticker_data.get('markPrice'),
            "last_price": ticker_data.get('last'),
            "index_price": ticker_data.get('indexPrice')
        }

        # 如果 mark_price 為 None，使用 last_price 作為備用
        if market_data["mark_price"] is None and market_data["last_price"] is not None:
            market_data["mark_price"] = market_data["last_price"]
            logging.info(f"Using last_price as mark_price for {api_client.name} {symbol}: {market_data['mark_price']}")

        # Validate that we got the essential data
        if market_data["funding_rate"] is None or market_data["mark_price"] is None:
            logging.warning(f"Incomplete data received from {api_client.name} for {symbol}. Data: {market_data}")
            return None

        return market_data
        
    except ccxt.NetworkError as e:
        logging.error(f"CCXT NetworkError for {api_client.name} on {symbol}: {e}")
        return None
    except ccxt.ExchangeError as e:
        logging.error(f"CCXT ExchangeError for {api_client.name} on {symbol}: {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred while fetching data from {api_client.name} for {symbol}: {e}", exc_info=True)
        return None 