"""
Base API client for Binance Futures
Handles connection, authentication, and common API operations
"""
from binance.client import Client
from src.config import Config
from src.logger import bot_logger
from src.validators import ValidationError


class BinanceAPIClient:
    """Wrapper for Binance API operations"""

    def __init__(self):
        """Initialize Binance API client"""
        try:
            Config.validate()
            self.client = Client(
                api_key=Config.BINANCE_API_KEY,
                api_secret=Config.BINANCE_SECRET_KEY,
                testnet=Config.TESTNET
            )
            bot_logger.info(
                f"Connected to Binance {'Testnet' if Config.TESTNET else 'Production'}"
            )
        except ValueError as e:
            bot_logger.error(f"Failed to initialize API client: {e}")
            raise

    def get_current_price(self, symbol):
        """
        Get current market price for symbol

        Args:
            symbol (str): Trading pair

        Returns:
            float: Current price
        """
        try:
            ticker = self.client.futures_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except Exception as e:
            bot_logger.error(f"Failed to fetch price for {symbol}: {e}")
            raise

    def get_balance(self):
        """
        Get account balance

        Returns:
            dict: Account balance information
        """
        try:
            account = self.client.futures_account()
            return account
        except Exception as e:
            bot_logger.error(f"Failed to fetch account balance: {e}")
            raise

    def get_available_balance(self):
        """Get available USDT balance"""
        try:
            account = self.get_balance()
            return float(account.get('availableBalance', 0))
        except Exception as e:
            bot_logger.error(f"Failed to fetch available balance: {e}")
            raise

    def cancel_order(self, symbol, order_id):
        """
        Cancel an open order

        Args:
            symbol (str): Trading pair
            order_id (int): Order ID to cancel

        Returns:
            dict: Cancellation response
        """
        try:
            response = self.client.futures_cancel_order(symbol=symbol, orderId=order_id)
            bot_logger.info(f"Cancelled order {order_id} for {symbol}")
            return response
        except Exception as e:
            bot_logger.error(f"Failed to cancel order {order_id}: {e}")
            raise

    def get_open_orders(self, symbol=None):
        """
        Get all open orders (optionally filtered by symbol)

        Args:
            symbol (str): Optional symbol filter

        Returns:
            list: Open orders
        """
        try:
            if symbol:
                orders = self.client.futures_get_open_orders(symbol=symbol)
            else:
                orders = self.client.futures_get_open_orders()
            return orders
        except Exception as e:
            bot_logger.error(f"Failed to fetch open orders: {e}")
            raise

    def set_leverage(self, symbol, leverage):
        """
        Set leverage for trading pair

        Args:
            symbol (str): Trading pair
            leverage (int): Leverage level (1-125)

        Returns:
            dict: Response
        """
        try:
            if not 1 <= leverage <= 125:
                raise ValidationError(f"Leverage must be between 1-125, got: {leverage}")

            response = self.client.futures_change_leverage(
                symbol=symbol,
                leverage=leverage
            )
            bot_logger.info(f"Set leverage {leverage}x for {symbol}")
            return response
        except Exception as e:
            bot_logger.error(f"Failed to set leverage: {e}")
            raise
            raise
