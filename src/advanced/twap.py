"""
TWAP (Time-Weighted Average Price) Strategy
Split large orders into smaller chunks over time to minimize price impact
"""
import time
from src.api_client import BinanceAPIClient
from src.validators import BotValidator, ValidationError
from src.logger import bot_logger


class TWAPStrategy:
    """Time-Weighted Average Price (TWAP) strategy implementation"""

    def __init__(self):
        """Initialize TWAP strategy handler"""
        self.client = BinanceAPIClient()
        self.executed_orders = []

    def place_order(self, symbol, side, total_quantity, num_orders, interval_seconds, **kwargs):
        """
        Place orders using TWAP strategy

        Splits a large order into smaller chunks and places them over time
        Use case: Execute large orders without causing significant price movement

        Args:
            symbol (str): Trading pair
            side (str): 'BUY' or 'SELL'
            total_quantity (float): Total quantity to buy/sell
            num_orders (int): Number of smaller orders to place
            interval_seconds (int): Seconds between each order
            **kwargs: Additional parameters

        Returns:
            dict: Strategy execution result

        Raises:
            ValidationError: If inputs are invalid
        """
        try:
            # Validate inputs
            symbol = BotValidator.validate_symbol(symbol)
            side = BotValidator.validate_side(side)
            total_quantity, interval_seconds, num_orders = BotValidator.validate_twap_params(
                total_quantity, interval_seconds, num_orders
            )

            # Calculate per-order quantity
            per_order_quantity = total_quantity / num_orders
            current_price = self.client.get_current_price(symbol)

            # Check balance once
            if side == 'BUY':
                available_balance = self.client.get_available_balance()
                required_balance = current_price * total_quantity
                if required_balance > available_balance:
                    raise ValidationError(
                        f"Insufficient balance. Required: {required_balance}, "
                        f"Available: {available_balance}"
                    )

            # Log TWAP execution
            bot_logger.log_order_placement(
                order_type='TWAP',
                symbol=symbol,
                side=side,
                total_quantity=total_quantity,
                num_orders=num_orders,
                per_order_quantity=per_order_quantity,
                interval_seconds=interval_seconds,
                current_price=current_price
            )

            self.executed_orders = []
            prices = []

            # Execute orders sequentially with timing
            for i in range(num_orders):
                try:
                    # Place market order
                    order = self.client.client.new_order(
                        symbol=symbol,
                        side=side,
                        type='MARKET',
                        quantity=per_order_quantity,
                        **kwargs
                    )

                    executed_price = float(order.get('avgPrice', current_price))
                    prices.append(executed_price)

                    self.executed_orders.append({
                        'order_id': order.get('orderId'),
                        'quantity': per_order_quantity,
                        'price': executed_price,
                        'timestamp': order.get('time')
                    })

                    bot_logger.info(
                        f"TWAP Order {i+1}/{num_orders} | ID: {order.get('orderId')} | "
                        f"Qty: {per_order_quantity} | Price: {executed_price}"
                    )

                    # Wait before next order (except after last order)
                    if i < num_orders - 1:
                        bot_logger.debug(f"Waiting {interval_seconds}s before next TWAP order...")
                        time.sleep(interval_seconds)

                except Exception as e:
                    bot_logger.log_error(
                        error_type='TWAPOrderError',
                        message=f"Failed at order {i+1}/{num_orders}: {str(e)}",
                        symbol=symbol,
                        side=side
                    )
                    # Continue with remaining orders
                    if i < num_orders - 1:
                        continue

            # Calculate TWAP average
            average_price = sum(prices) / len(prices) if prices else current_price
            total_executed = sum(order['quantity'] for order in self.executed_orders)

            bot_logger.log_order_execution(
                order_id='TWAP_BATCH',
                symbol=symbol,
                side=side,
                quantity=total_executed,
                executed_price=average_price
            )

            return {
                'success': True,
                'symbol': symbol,
                'side': side,
                'strategy': 'TWAP',
                'total_quantity': total_quantity,
                'executed_quantity': total_executed,
                'orders_count': len(self.executed_orders),
                'average_price': average_price,
                'orders': self.executed_orders
            }

        except ValidationError as e:
            bot_logger.error(f"Validation error in TWAP strategy: {e}")
            raise
        except Exception as e:
            bot_logger.log_error(
                error_type='TWAPStrategyError',
                message=str(e),
                symbol=symbol,
                side=side,
                total_quantity=total_quantity,
                num_orders=num_orders
            )
            raise


def place_twap_order(symbol, side, total_quantity, num_orders, interval_seconds):
    """
    Standalone function to execute TWAP strategy

    Args:
        symbol (str): Trading pair
        side (str): BUY or SELL
        total_quantity (float): Total quantity to execute
        num_orders (int): Number of sub-orders
        interval_seconds (int): Time between orders

    Returns:
        dict: Strategy execution result
    """
    strategy = TWAPStrategy()
    return strategy.place_order(symbol, side, total_quantity, num_orders, interval_seconds)
