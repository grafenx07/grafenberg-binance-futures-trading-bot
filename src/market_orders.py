"""
Market Order implementation
Buy/Sell at market price with instant execution
"""
from src.api_client import BinanceAPIClient
from src.validators import BotValidator, ValidationError
from src.logger import bot_logger


class MarketOrder:
    """Market order implementation"""

    def __init__(self):
        """Initialize market order handler"""
        self.client = BinanceAPIClient()

    def place_order(self, symbol, side, quantity, **kwargs):
        """
        Place a market order

        Args:
            symbol (str): Trading pair (e.g., 'BTCUSDT')
            side (str): 'BUY' or 'SELL'
            quantity (float): Order quantity
            **kwargs: Additional parameters (positionSide, etc.)

        Returns:
            dict: Order response

        Raises:
            ValidationError: If inputs are invalid
        """
        try:
            # Validate inputs
            symbol = BotValidator.validate_symbol(symbol)
            side = BotValidator.validate_side(side)
            quantity = BotValidator.validate_quantity(quantity, symbol)

            # Get current price for reference
            current_price = self.client.get_current_price(symbol)

            # Check available balance for BUY orders
            if side == 'BUY':
                available_balance = self.client.get_available_balance()
                required_balance = current_price * quantity
                if required_balance > available_balance:
                    raise ValidationError(
                        f"Insufficient balance. Required: {required_balance}, "
                        f"Available: {available_balance}"
                    )

            # Log order placement
            bot_logger.log_order_placement(
                order_type='MARKET',
                symbol=symbol,
                side=side,
                quantity=quantity,
                current_price=current_price
            )

            # Place order
            order = self.client.client.new_order(
                symbol=symbol,
                side=side,
                type='MARKET',
                quantity=quantity,
                **kwargs
            )

            # Log execution
            executed_price = float(order.get('avgPrice', current_price))
            bot_logger.log_order_execution(
                order_id=order.get('orderId'),
                symbol=symbol,
                side=side,
                quantity=quantity,
                executed_price=executed_price,
                commission=float(order.get('commission', 0))
            )

            return {
                'success': True,
                'order_id': order.get('orderId'),
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'executed_price': executed_price,
                'status': order.get('status'),
                'timestamp': order.get('time')
            }

        except ValidationError as e:
            bot_logger.error(f"Validation error in market order: {e}")
            raise
        except Exception as e:
            bot_logger.log_error(
                error_type='MarketOrderError',
                message=str(e),
                symbol=symbol,
                side=side,
                quantity=quantity
            )
            raise


def place_market_order(symbol, side, quantity):
    """
    Standalone function to place a market order

    Args:
        symbol (str): Trading pair
        side (str): BUY or SELL
        quantity (float): Order quantity

    Returns:
        dict: Order result
    """
    order = MarketOrder()
    return order.place_order(symbol, side, quantity)
