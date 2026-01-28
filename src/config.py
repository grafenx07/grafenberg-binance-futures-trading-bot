"""
Configuration management for Binance Bot
Handles environment variables and API setup
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for the trading bot"""

    # API Configuration
    BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
    BINANCE_SECRET_KEY = os.getenv('BINANCE_SECRET_KEY')

    # Environment
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'testnet')
    TESTNET = ENVIRONMENT.lower() == 'testnet'

    # Trading Configuration
    DEFAULT_SYMBOL = os.getenv('DEFAULT_SYMBOL', 'BTCUSDT')
    DEFAULT_LEVERAGE = int(os.getenv('DEFAULT_LEVERAGE', '1'))
    MAX_ORDER_SIZE = float(os.getenv('MAX_ORDER_SIZE', '1.0'))

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_DIR = 'logs'
    LOG_FILE = os.path.join(LOG_DIR, 'bot.log')

    # Validation
    MIN_QUANTITY = 0.001
    MAX_PRICE_VARIANCE = 0.05  # 5% price variance allowed

    # Risk Management
    MAX_LOSS_PERCENT = 5  # Stop trading if loss exceeds 5%
    POSITION_SIZE_PERCENT = 2  # Risk 2% per trade

    @classmethod
    def validate(cls):
        """Validate that all required configurations are set"""
        if not cls.BINANCE_API_KEY or not cls.BINANCE_SECRET_KEY:
            raise ValueError(
                "Missing API credentials. Please set BINANCE_API_KEY and "
                "BINANCE_SECRET_KEY in .env file"
            )
        if cls.BINANCE_API_KEY == "your_testnet_api_key_here":
            raise ValueError(
                "Default API credentials detected. "
                "Please update .env with your actual testnet credentials from "
                "https://testnet.binancefuture.com"
            )
        return True

    @classmethod
    def get_api_url(cls):
        """Get appropriate API URL based on environment"""
        if cls.TESTNET:
            return "https://testnet.binancefuture.com"
        return "https://fapi.binance.com"
