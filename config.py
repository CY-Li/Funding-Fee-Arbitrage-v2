import os
import json

# ------------------ API Keys ------------------
# IMPORTANT: Load API keys from environment variables for security.
# On Zeabur, you will set these in the service's "Variables" section.

GATEIO_API_KEY = os.environ.get("GATEIO_API_KEY")
GATEIO_SECRET_KEY = os.environ.get("GATEIO_SECRET_KEY")

BITGET_API_KEY = os.environ.get("BITGET_API_KEY")
BITGET_SECRET_KEY = os.environ.get("BITGET_SECRET_KEY")
BITGET_API_PASSPHRASE = os.environ.get("BITGET_API_PASSPHRASE")

CONFIG_FILE = 'config.json'

# 預設參數
DEFAULT_CONFIG = {
    "TRADING_PAIRS": [
        "FUN/USDT", "SNT/USDT", "RSS3/USDT", "FU/USDT", "BADGER/USDT",
        "JST/USDT", "CTK/USDT", "TLM/USDT", "CVC/USDT", "BLAST/USDT"
    ],
    "MIN_FUNDING_RATE_DIFFERENCE": 0.10,
    "MAX_PRICE_SPREAD": 0.005,
    "CLOSE_FUNDING_RATE_DIFFERENCE": 0.02,
    "POSITION_SIZE_USDT": 100.0,
    "TEST_MODE": True,
    "LOOP_INTERVAL_SECONDS": 60,
    "MAX_TOTAL_EXPOSURE_USDT": 1000.0,
    "WEB_SERVER_PORT": 8080,
    "MIN_HOLDING_HOURS_FOR_REVERSAL": 4.0,
    "STOP_LOSS_USDT": -2.0,
    "MAX_HOLDING_PRICE_SPREAD": 0.01,
    "MAX_HOLDING_DURATION_HOURS": 168
}

def get_env_value(key, default_value, value_type=str):
    """從環境變數獲取值，支持不同數據類型"""
    env_value = os.environ.get(key)
    if env_value is None:
        return default_value
    
    try:
        if value_type == bool:
            return env_value.lower() in ('true', '1', 'yes', 'on')
        elif value_type == list:
            # 對於列表類型，假設是 JSON 格式的字符串
            return json.loads(env_value)
        else:
            return value_type(env_value)
    except (ValueError, json.JSONDecodeError):
        print(f"Warning: Invalid environment variable {key}={env_value}, using default: {default_value}")
        return default_value

# 參數全域變數（初始化為預設值）
for k, v in DEFAULT_CONFIG.items():
    globals()[k] = v

def load_config_from_file():
    """從 config.json 讀取所有參數，若不存在則用預設值"""
    global TRADING_PAIRS, MIN_FUNDING_RATE_DIFFERENCE, CLOSE_FUNDING_RATE_DIFFERENCE
    global MAX_PRICE_SPREAD, POSITION_SIZE_USDT, MAX_TOTAL_EXPOSURE_USDT
    global STOP_LOSS_USDT, MAX_HOLDING_PRICE_SPREAD, MAX_HOLDING_DURATION_HOURS
    global MIN_HOLDING_HOURS_FOR_REVERSAL, LOOP_INTERVAL_SECONDS, TEST_MODE
    global WEB_SERVER_PORT
    
    if not os.path.exists(CONFIG_FILE):
        save_config_to_file(DEFAULT_CONFIG)
        config = DEFAULT_CONFIG.copy()
    else:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
    
    # 設定全域變數，優先使用環境變數
    TRADING_PAIRS = get_env_value("TRADING_PAIRS", config.get("TRADING_PAIRS", DEFAULT_CONFIG["TRADING_PAIRS"]), list)
    MIN_FUNDING_RATE_DIFFERENCE = get_env_value("MIN_FUNDING_RATE_DIFFERENCE", float(config.get("MIN_FUNDING_RATE_DIFFERENCE", DEFAULT_CONFIG["MIN_FUNDING_RATE_DIFFERENCE"])), float)
    CLOSE_FUNDING_RATE_DIFFERENCE = get_env_value("CLOSE_FUNDING_RATE_DIFFERENCE", float(config.get("CLOSE_FUNDING_RATE_DIFFERENCE", DEFAULT_CONFIG["CLOSE_FUNDING_RATE_DIFFERENCE"])), float)
    MAX_PRICE_SPREAD = get_env_value("MAX_PRICE_SPREAD", float(config.get("MAX_PRICE_SPREAD", DEFAULT_CONFIG["MAX_PRICE_SPREAD"])), float)
    POSITION_SIZE_USDT = get_env_value("POSITION_SIZE_USDT", float(config.get("POSITION_SIZE_USDT", DEFAULT_CONFIG["POSITION_SIZE_USDT"])), float)
    MAX_TOTAL_EXPOSURE_USDT = get_env_value("MAX_TOTAL_EXPOSURE_USDT", float(config.get("MAX_TOTAL_EXPOSURE_USDT", DEFAULT_CONFIG["MAX_TOTAL_EXPOSURE_USDT"])), float)
    STOP_LOSS_USDT = get_env_value("STOP_LOSS_USDT", float(config.get("STOP_LOSS_USDT", DEFAULT_CONFIG["STOP_LOSS_USDT"])), float)
    MAX_HOLDING_PRICE_SPREAD = get_env_value("MAX_HOLDING_PRICE_SPREAD", float(config.get("MAX_HOLDING_PRICE_SPREAD", DEFAULT_CONFIG["MAX_HOLDING_PRICE_SPREAD"])), float)
    MAX_HOLDING_DURATION_HOURS = get_env_value("MAX_HOLDING_DURATION_HOURS", int(config.get("MAX_HOLDING_DURATION_HOURS", DEFAULT_CONFIG["MAX_HOLDING_DURATION_HOURS"])), int)
    MIN_HOLDING_HOURS_FOR_REVERSAL = get_env_value("MIN_HOLDING_HOURS_FOR_REVERSAL", float(config.get("MIN_HOLDING_HOURS_FOR_REVERSAL", DEFAULT_CONFIG["MIN_HOLDING_HOURS_FOR_REVERSAL"])), float)
    LOOP_INTERVAL_SECONDS = get_env_value("LOOP_INTERVAL_SECONDS", int(config.get("LOOP_INTERVAL_SECONDS", DEFAULT_CONFIG["LOOP_INTERVAL_SECONDS"])), int)
    TEST_MODE = get_env_value("TEST_MODE", bool(config.get("TEST_MODE", DEFAULT_CONFIG["TEST_MODE"])), bool)
    WEB_SERVER_PORT = get_env_value("WEB_SERVER_PORT", int(config.get("WEB_SERVER_PORT", DEFAULT_CONFIG["WEB_SERVER_PORT"])), int)

def save_config_to_file(config_dict=None):
    """將目前全域參數或指定 dict 寫入 config.json"""
    if config_dict is None:
        config_dict = {
            "TRADING_PAIRS": TRADING_PAIRS,
            "MIN_FUNDING_RATE_DIFFERENCE": MIN_FUNDING_RATE_DIFFERENCE,
            "CLOSE_FUNDING_RATE_DIFFERENCE": CLOSE_FUNDING_RATE_DIFFERENCE,
            "MAX_PRICE_SPREAD": MAX_PRICE_SPREAD,
            "POSITION_SIZE_USDT": POSITION_SIZE_USDT,
            "MAX_TOTAL_EXPOSURE_USDT": MAX_TOTAL_EXPOSURE_USDT,
            "STOP_LOSS_USDT": STOP_LOSS_USDT,
            "MAX_HOLDING_PRICE_SPREAD": MAX_HOLDING_PRICE_SPREAD,
            "MAX_HOLDING_DURATION_HOURS": MAX_HOLDING_DURATION_HOURS,
            "MIN_HOLDING_HOURS_FOR_REVERSAL": MIN_HOLDING_HOURS_FOR_REVERSAL,
            "LOOP_INTERVAL_SECONDS": LOOP_INTERVAL_SECONDS,
            "TEST_MODE": TEST_MODE,
            "WEB_SERVER_PORT": WEB_SERVER_PORT
        }
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config_dict, f, indent=4)

def reload_config():
    load_config_from_file()

# 初始化時加載配置
try:
    load_config_from_file()
except Exception as e:
    print(f"Warning: Could not load config from file: {e}")
    # 使用預設配置
    pass 