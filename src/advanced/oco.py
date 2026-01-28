"""
OCO (One-Cancels-Other) Order implementation
Place take-profit and stop-loss orders simultaneously
"""
from src.api_client import BinanceAPIClient
from src.validators import BotValidator, ValidationError
from src.logger import bot_logger


class OCOOrder:
    """OCO (One-Cancels-Other) order implementation"""

    def __init__(self):
        """Initialize OCO order handler"""
        self.client = BinanceAPIClient()

    def place_order(self, symbol, side, quantity, take_profit, stop_loss, **kwargs):
        """
        Place an OCO order (One-Cancels-Other)

        When one side executes, the other is automatically cancelled
        Use case: Hedge a position with profit target and stop loss

        Args:
            symbol (str): Trading pair
            side (str): 'BUY' or 'SELL'
            quantity (float): Order quantity
            take_profit (float): Take profit price (sell price if BUY, buy price if SELL)
            stop_loss (float): Stop loss price
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

            # Validate OCO prices
            take_profit, stop_loss = BotValidator.validate_oco_order(
                take_profit, stop_loss, current_price
            )

            # Opposite side for OCO legs
            opposite_side = 'SELL' if side == 'BUY' else 'BUY'

            # Check balance for initial BUY position
            if side == 'BUY':
                available_balance = self.client.get_available_balance()
                required_balance = current_price * quantity
                if required_balance > available_balance:
                    raise ValidationError(
                        f"Insufficient balance. Required: {required_balance}, "
                        f"Available: {available_balance}"
                    )

            # Log OCO placement
            bot_logger.log_order_placement(
                order_type='OCO',
                symbol=symbol,
                side=side,
                quantity=quantity,
                take_profit=take_profit,
                stop_loss=stop_loss,
                current_price=current_price
            )

            # Set default timeInForce if not provided
            if 'timeInForce' not in kwargs:
                kwargs['timeInForce'] = 'GTC'

            # Place OCO order
            order = self.client.client.new_oco_order(
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=take_profit,  # Take profit limit price
                stopPrice=stop_loss,  # Stop loss trigger price
                stopLimitPrice=stop_loss,  # Stop loss limit price (same as stop for OCO)
                **kwargs
            )

            # Log successful placement
            bot_logger.info(
                f"OCO order placed | ID: {order.get('orderListId')} | "
                f"Take Profit: {take_profit} | Stop Loss: {stop_loss}"
            )

            return {
                'success': True,
                'order_list_id': order.get('orderListId'),
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'take_profit': take_profit,
                'stop_loss': stop_loss,
                'status': order.get('listStatusType'),
                'orders': order.get('orders', []),
                'timestamp': order.get('transactionTime')
            }

        except ValidationError as e:
            bot_logger.error(f"Validation error in OCO order: {e}")
            raise
        except Exception as e:
            bot_logger.log_error(
                error_type='OCOOrderError',
                message=str(e),
                symbol=symbol,
                side=side,
                quantity=quantity,
                take_profit=take_profit,
                stop_loss=stop_loss
            )
            raise

    def cancel_oco_order(self, symbol, order_list_id):
        """
        Cancel an OCO order

        Args:
            symbol (str): Trading pair
            order_list_id (int): OCO order list ID

        Returns:
            dict: Cancellation response
        """
        try:
            response = self.client.client.cancel_oco_order(
                symbol=symbol,
                orderListId=order_list_id
            )
            bot_logger.info(f"Cancelled OCO order {order_list_id} for {symbol}")
            return response
        except Exception as e:
            bot_logger.error(f"Failed to cancel OCO order: {e}")
            raise


def place_oco_order(symbol, side, quantity, take_profit, stop_loss):
    """
    Standalone function to place an OCO order

    Args:
        symbol (str): Trading pair
        side (str): BUY or SELL
        quantity (float): Order quantity
        take_profit (float): Take profit price
        stop_loss (float): Stop loss price

    Returns:
        dict: Order result
    """
    order = OCOOrder()
    return order.place_order(symbol, side, quantity, take_profit, stop_loss)
