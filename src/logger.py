"""
Structured logging system for the trading bot
Provides formatted, timestamped logs with rotation
"""
import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime
from src.config import Config


class BotLogger:
    """Custom logger for the trading bot"""

    def __init__(self, name=__name__):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, Config.LOG_LEVEL))

        # Ensure logs directory exists
        os.makedirs(Config.LOG_DIR, exist_ok=True)

        # Create formatters
        detailed_format = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # File handler with rotation
        if not self.logger.handlers:  # Avoid duplicate handlers
            file_handler = RotatingFileHandler(
                Config.LOG_FILE,
                maxBytes=5*1024*1024,  # 5MB
                backupCount=5
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(detailed_format)
            self.logger.addHandler(file_handler)

            # Console handler for important messages
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_format = logging.Formatter(
                fmt='[%(levelname)s] %(message)s'
            )
            console_handler.setFormatter(console_format)
            self.logger.addHandler(console_handler)

    def log_order_placement(self, order_type, symbol, side, quantity, price=None, **kwargs):
        """Log order placement with details"""
        msg = f"ORDER PLACED | Type: {order_type} | Symbol: {symbol} | Side: {side} | Qty: {quantity}"
        if price:
            msg += f" | Price: {price}"
        for key, value in kwargs.items():
            msg += f" | {key}: {value}"
        self.logger.info(msg)

    def log_order_execution(self, order_id, symbol, side, quantity, executed_price, commission=0):
        """Log successful order execution"""
        msg = f"ORDER EXECUTED | ID: {order_id} | Symbol: {symbol} | Side: {side} | Qty: {quantity} | Price: {executed_price} | Commission: {commission}"
        self.logger.info(msg)

    def log_error(self, error_type, message, **context):
        """Log errors with context"""
        msg = f"ERROR | Type: {error_type} | Message: {message}"
        for key, value in context.items():
            msg += f" | {key}: {value}"
        self.logger.error(msg, exc_info=True)

    def log_trade_summary(self, trades_count, total_profit, win_rate):
        """Log trade summary and statistics"""
        msg = f"TRADE SUMMARY | Total Trades: {trades_count} | Total P&L: {total_profit} | Win Rate: {win_rate:.2%}"
        self.logger.info(msg)

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)


# Global logger instance
bot_logger = BotLogger("BinanceBot")
