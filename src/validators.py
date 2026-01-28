"""
Input validators for trading bot
Validates symbols, quantities, prices, and order parameters
"""
import re
from src.logger import bot_logger
from src.config import Config


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class BotValidator:
    """Validator for trading bot inputs"""

    # Valid Binance symbols pattern (e.g., BTCUSDT, ETHUSDT)
    SYMBOL_PATTERN = re.compile(r'^[A-Z]{2,}USDT$')

    # Valid order sides
    VALID_SIDES = ['BUY', 'SELL']

    # Valid order types
    VALID_ORDER_TYPES = ['MARKET', 'LIMIT', 'STOP_LIMIT', 'OCO', 'TWAP', 'GRID']

    @staticmethod
    def validate_symbol(symbol):
        """
        Validate trading symbol format

        Args:
            symbol (str): Trading pair symbol (e.g., 'BTCUSDT')

        Returns:
            str: Valid symbol (uppercase)

        Raises:
            ValidationError: If symbol is invalid
        """
        if not symbol or not isinstance(symbol, str):
            raise ValidationError("Symbol must be a non-empty string")

        symbol = symbol.upper()
        if not BotValidator.SYMBOL_PATTERN.match(symbol):
            raise ValidationError(
                f"Invalid symbol format: {symbol}. "
                f"Expected format: BTCUSDT (crypto + USDT)"
            )
        return symbol

    @staticmethod
    def validate_quantity(quantity, symbol=''):
        """
        Validate order quantity

        Args:
            quantity (float): Order quantity
            symbol (str): Symbol for context

        Returns:
            float: Valid quantity

        Raises:
            ValidationError: If quantity is invalid
        """
        try:
            qty = float(quantity)
        except (ValueError, TypeError):
            raise ValidationError(f"Quantity must be a number, got: {quantity}")

        if qty <= 0:
            raise ValidationError(f"Quantity must be positive, got: {qty}")

        if qty < Config.MIN_QUANTITY:
            raise ValidationError(
                f"Quantity {qty} is below minimum {Config.MIN_QUANTITY}"
            )

        if qty > Config.MAX_ORDER_SIZE:
            raise ValidationError(
                f"Quantity {qty} exceeds maximum {Config.MAX_ORDER_SIZE}"
            )

        return qty

    @staticmethod
    def validate_price(price, price_type='limit'):
        """
        Validate price

        Args:
            price (float): Price value
            price_type (str): Type of price (limit, stop, tp, sl)

        Returns:
            float: Valid price

        Raises:
            ValidationError: If price is invalid
        """
        try:
            p = float(price)
        except (ValueError, TypeError):
            raise ValidationError(f"Price must be a number, got: {price}")

        if p <= 0:
            raise ValidationError(f"Price must be positive, got: {p}")

        return p

    @staticmethod
    def validate_side(side):
        """
        Validate order side (BUY/SELL)

        Args:
            side (str): Order side

        Returns:
            str: Valid side (uppercase)

        Raises:
            ValidationError: If side is invalid
        """
        if not side or not isinstance(side, str):
            raise ValidationError("Side must be 'BUY' or 'SELL'")

        side = side.upper()
        if side not in BotValidator.VALID_SIDES:
            raise ValidationError(
                f"Invalid side: {side}. Must be one of {BotValidator.VALID_SIDES}"
            )
        return side

    @staticmethod
    def validate_stop_limit_order(stop_price, limit_price, current_price):
        """
        Validate stop-limit order parameters

        Args:
            stop_price (float): Trigger price
            limit_price (float): Limit order price
            current_price (float): Current market price

        Returns:
            tuple: (stop_price, limit_price)

        Raises:
            ValidationError: If parameters are invalid
        """
        stop_price = BotValidator.validate_price(stop_price, 'stop')
        limit_price = BotValidator.validate_price(limit_price, 'limit')
        current_price = BotValidator.validate_price(current_price, 'current')

        # Stop price should be different from limit price
        if abs(stop_price - limit_price) < 0.01:
            raise ValidationError(
                f"Stop price ({stop_price}) and limit price ({limit_price}) "
                f"should be significantly different"
            )

        return stop_price, limit_price

    @staticmethod
    def validate_oco_order(take_profit, stop_loss, current_price):
        """
        Validate OCO (One-Cancels-Other) order parameters

        Args:
            take_profit (float): Take profit price
            stop_loss (float): Stop loss price
            current_price (float): Current market price

        Returns:
            tuple: (take_profit, stop_loss)

        Raises:
            ValidationError: If parameters are invalid
        """
        take_profit = BotValidator.validate_price(take_profit, 'tp')
        stop_loss = BotValidator.validate_price(stop_loss, 'sl')
        current_price = BotValidator.validate_price(current_price, 'current')

        if take_profit <= current_price:
            raise ValidationError(
                f"Take profit ({take_profit}) must be above current price ({current_price})"
            )

        if stop_loss >= current_price:
            raise ValidationError(
                f"Stop loss ({stop_loss}) must be below current price ({current_price})"
            )

        if stop_loss <= 0:
            raise ValidationError(f"Stop loss must be positive, got: {stop_loss}")

        return take_profit, stop_loss

    @staticmethod
    def validate_twap_params(total_quantity, interval_seconds, num_orders):
        """
        Validate TWAP (Time-Weighted Average Price) parameters

        Args:
            total_quantity (float): Total quantity to split
            interval_seconds (int): Seconds between orders
            num_orders (int): Number of orders to place

        Returns:
            tuple: (total_quantity, interval_seconds, num_orders)

        Raises:
            ValidationError: If parameters are invalid
        """
        total_quantity = BotValidator.validate_quantity(total_quantity)

        try:
            interval_seconds = int(interval_seconds)
        except (ValueError, TypeError):
            raise ValidationError(f"Interval must be an integer, got: {interval_seconds}")

        if interval_seconds <= 0:
            raise ValidationError(f"Interval must be positive, got: {interval_seconds}")

        try:
            num_orders = int(num_orders)
        except (ValueError, TypeError):
            raise ValidationError(f"Number of orders must be an integer, got: {num_orders}")

        if num_orders <= 0:
            raise ValidationError(f"Number of orders must be positive, got: {num_orders}")

        per_order_qty = total_quantity / num_orders
        if per_order_qty < Config.MIN_QUANTITY:
            raise ValidationError(
                f"Per-order quantity ({per_order_qty}) would be below minimum "
                f"({Config.MIN_QUANTITY}). Reduce number of orders."
            )

        return total_quantity, interval_seconds, num_orders

    @staticmethod
    def validate_grid_params(lower_price, upper_price, num_grids):
        """
        Validate Grid strategy parameters

        Args:
            lower_price (float): Lower price boundary
            upper_price (float): Upper price boundary
            num_grids (int): Number of grid levels

        Returns:
            tuple: (lower_price, upper_price, num_grids)

        Raises:
            ValidationError: If parameters are invalid
        """
        lower_price = BotValidator.validate_price(lower_price, 'lower')
        upper_price = BotValidator.validate_price(upper_price, 'upper')

        if lower_price >= upper_price:
            raise ValidationError(
                f"Lower price ({lower_price}) must be below upper price ({upper_price})"
            )

        try:
            num_grids = int(num_grids)
        except (ValueError, TypeError):
            raise ValidationError(f"Number of grids must be an integer, got: {num_grids}")

        if num_grids <= 1:
            raise ValidationError(f"Number of grids must be > 1, got: {num_grids}")

        if num_grids > 100:
            raise ValidationError(f"Number of grids too high: {num_grids} (max: 100)")

        return lower_price, upper_price, num_grids
