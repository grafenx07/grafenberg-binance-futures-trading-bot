"""
Binance Futures Trading Bot
A professional CLI-based trading bot with support for multiple order types
and advanced strategies like TWAP, OCO, and Grid Trading.
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__license__ = "MIT"

from src.config import Config
from src.logger import bot_logger
from src.validators import BotValidator, ValidationError
from src.api_client import BinanceAPIClient

__all__ = [
    'Config',
    'bot_logger',
    'BotValidator',
    'ValidationError',
    'BinanceAPIClient'
]
