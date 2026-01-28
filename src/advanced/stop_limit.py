"""
Stop-Limit Order implementation
Triggers a limit order when stop price is hit
"""
from src.api_client import BinanceAPIClient
from src.validators import BotValidator, ValidationError
from src.logger import bot_logger


class StopLimitOrder:
    """Stop-Limit order implementation"""

    def __init__(self):
        """Initialize stop-limit order handler"""
        self.client = BinanceAPIClient()

    def place_order(self, symbol, side, quantity, stop_price, limit_price, **kwargs):
        """
        Place a stop-limit order

        Order will be placed as a LIMIT order when price reaches the STOP_PRICE

        Args:
            symbol (str): Trading pair
            side (str): 'BUY' or 'SELL'
            quantity (float): Order quantity
            stop_price (float): Trigger/stop price
            limit_price (float): Limit price when triggered
            **kwargs: Additional parameters

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
            current_price = self.client.get_current_price(symbol)

            # Validate stop and limit prices
            stop_price, limit_price = BotValidator.validate_stop_limit_order(
                stop_price, limit_price, current_price
            )

            # Logic validation: for BUY order, stop should be above current
            if side == 'BUY' and stop_price < current_price:
                raise ValidationError(
                    f"For BUY order, stop price ({stop_price}) should be >= current price ({current_price})"
                )

            # Logic validation: for SELL order, stop should be below current
            if side == 'SELL' and stop_price > current_price:
                raise ValidationError(
                    f"For SELL order, stop price ({stop_price}) should be <= current price ({current_price})"
                )

            # Check balance for BUY orders
            if side == 'BUY':
                available_balance = self.client.get_available_balance()
                required_balance = limit_price * quantity
                if required_balance > available_balance:
                    raise ValidationError(
                        f"Insufficient balance. Required: {required_balance}, "
                        f"Available: {available_balance}"
                    )

            # Log order placement
            bot_logger.log_order_placement(
                order_type='STOP_LIMIT',
                symbol=symbol,
                side=side,
                quantity=quantity,
                stop_price=stop_price,
                limit_price=limit_price,
                current_price=current_price
            )

            # Place stop-limit order
            if 'timeInForce' not in kwargs:
                kwargs['timeInForce'] = 'GTC'  # Good Till Cancel

            order = self.client.client.futures_create_order(
                price=limit_price,
                stopPrice=stop_price,
                **kwargs
            )

            # Log successful placement
            bot_logger.info(
                f"Stop-Limit order placed | ID: {order.get('orderId')} | "
                f"Stop: {stop_price} | Limit: {limit_price} | Status: {order.get('status')}"
            )

            return {
                'success': True,
                'order_id': order.get('orderId'),
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'stop_price': stop_price,
                'limit_price': limit_price,
                'status': order.get('status'),
                'timestamp': order.get('time')
            }

        except ValidationError as e:
            bot_logger.error(f"Validation error in stop-limit order: {e}")
            raise
        except Exception as e:
            bot_logger.log_error(
                error_type='StopLimitOrderError',
                message=str(e),
                symbol=symbol,
                side=side,
                quantity=quantity,
                stop_price=stop_price,
                limit_price=limit_price
            )
            raise


def place_stop_limit_order(symbol, side, quantity, stop_price, limit_price):
    """
    Standalone function to place a stop-limit order

    Args:
        symbol (str): Trading pair
        side (str): BUY or SELL
        quantity (float): Order quantity
        stop_price (float): Trigger price
        limit_price (float): Limit price

    Returns:
        dict: Order result
    """
    order = StopLimitOrder()
    return order.place_order(symbol, side, quantity, stop_price, limit_price)
