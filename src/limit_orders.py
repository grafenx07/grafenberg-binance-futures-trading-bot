"""
Limit Order implementation
Buy/Sell at specific price (pending execution)
"""
from src.api_client import BinanceAPIClient
from src.validators import BotValidator, ValidationError
from src.logger import bot_logger


class LimitOrder:
    """Limit order implementation"""

    def __init__(self):
        """Initialize limit order handler"""
        self.client = BinanceAPIClient()

    def place_order(self, symbol, side, quantity, price, **kwargs):
        """
        Place a limit order

        Args:
            symbol (str): Trading pair (e.g., 'BTCUSDT')
            side (str): 'BUY' or 'SELL'
            quantity (float): Order quantity
            price (float): Limit price
            **kwargs: Additional parameters (timeInForce, etc.)

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
            price = BotValidator.validate_price(price, 'limit')

            # Get current price for reference
            current_price = self.client.get_current_price(symbol)

            # Validate price is reasonable (within variance threshold)
            price_variance = abs(price - current_price) / current_price
            if price_variance > Config.MAX_PRICE_VARIANCE:
                bot_logger.warning(
                    f"Limit price variance ({price_variance:.2%}) exceeds "
                    f"recommended threshold ({Config.MAX_PRICE_VARIANCE:.2%})"
                )

            # Check available balance for BUY orders
            if side == 'BUY':
                available_balance = self.client.get_available_balance()
                required_balance = price * quantity
                if required_balance > available_balance:
                    raise ValidationError(
                        f"Insufficient balance. Required: {required_balance}, "
                        f"Available: {available_balance}"
                    )

            # Log order placement
            bot_logger.log_order_placement(
                order_type='LIMIT',
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=price,
                current_price=current_price
            )

            # Set default timeInForce if not provided
            if 'timeInForce' not in kwargs:
                kwargs['timeInForce'] = 'GTC'  # Good Till Cancel

            # Place order
            order = self.client.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='LIMIT',
                quantity=quantity,
                price=price,
                **kwargs
            )

            # Log order creation
            bot_logger.info(
                f"Limit order created | ID: {order.get('orderId')} | "
                f"Status: {order.get('status')}"
            )

            return {
                'success': True,
                'order_id': order.get('orderId'),
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'price': price,
                'status': order.get('status'),
                'timestamp': order.get('time')
            }

        except ValidationError as e:
            bot_logger.error(f"Validation error in limit order: {e}")
            raise
        except Exception as e:
            bot_logger.log_error(
                error_type='LimitOrderError',
                message=str(e),
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=price
            )
            raise


def place_limit_order(symbol, side, quantity, price):
    """
    Standalone function to place a limit order

    Args:
        symbol (str): Trading pair
        side (str): BUY or SELL
        quantity (float): Order quantity
        price (float): Limit price

    Returns:
        dict: Order result
    """
    order = LimitOrder()
    return order.place_order(symbol, side, quantity, price)


# Import Config for validation
from src.config import Config
