"""
Grid Trading Strategy
Automated buy-low/sell-high within a price range
"""
from src.api_client import BinanceAPIClient
from src.validators import BotValidator, ValidationError
from src.logger import bot_logger


class GridStrategy:
    """Grid trading strategy implementation"""

    def __init__(self):
        """Initialize grid strategy handler"""
        self.client = BinanceAPIClient()
        self.active_grids = {}

    def place_order(self, symbol, lower_price, upper_price, num_grids, investment_amount, **kwargs):
        """
        Place grid trading orders

        Creates a grid of buy and sell orders within price range
        Use case: Profit from price oscillations within a range

        Args:
            symbol (str): Trading pair
            lower_price (float): Lower boundary price
            upper_price (float): Upper boundary price
            num_grids (int): Number of grid levels
            investment_amount (float): Total USDT to invest
            **kwargs: Additional parameters

        Returns:
            dict: Grid strategy result

        Raises:
            ValidationError: If inputs are invalid
        """
        try:
            # Validate inputs
            symbol = BotValidator.validate_symbol(symbol)
            lower_price, upper_price, num_grids = BotValidator.validate_grid_params(
                lower_price, upper_price, num_grids
            )

            # Validate investment amount
            try:
                investment_amount = float(investment_amount)
            except (ValueError, TypeError):
                raise ValidationError(f"Investment amount must be a number, got: {investment_amount}")

            if investment_amount <= 0:
                raise ValidationError(f"Investment amount must be positive, got: {investment_amount}")

            # Check available balance
            available_balance = self.client.get_available_balance()
            if investment_amount > available_balance:
                raise ValidationError(
                    f"Insufficient balance. Required: {investment_amount}, "
                    f"Available: {available_balance}"
                )

            current_price = self.client.get_current_price(symbol)

            # Validate current price is within range
            if not (lower_price <= current_price <= upper_price):
                bot_logger.warning(
                    f"Current price {current_price} is outside grid range "
                    f"[{lower_price}, {upper_price}]. Grid may not execute immediately."
                )

            # Log grid placement
            bot_logger.log_order_placement(
                order_type='GRID',
                symbol=symbol,
                lower_price=lower_price,
                upper_price=upper_price,
                num_grids=num_grids,
                investment_amount=investment_amount,
                current_price=current_price
            )

            # Calculate grid parameters
            price_range = upper_price - lower_price
            grid_step = price_range / (num_grids - 1)
            per_grid_investment = investment_amount / num_grids

            # Generate grid levels and orders
            grid_orders = []

            for i in range(num_grids):
                grid_price = lower_price + (i * grid_step)

                # Buy orders at lower half, sell orders at upper half
                if grid_price < current_price:
                    # Buy order (lower side)
                    quantity = per_grid_investment / grid_price
                    side = 'BUY'
                    order_type = 'LIMIT'

                    try:
                        order = self.client.client.new_order(
                            symbol=symbol,
                            side=side,
                            type=order_type,
                            quantity=quantity,
                            price=grid_price,
                            timeInForce='GTC',
                            **kwargs
                        )

                        grid_orders.append({
                            'grid_level': i + 1,
                            'side': side,
                            'price': grid_price,
                            'quantity': quantity,
                            'order_id': order.get('orderId'),
                            'status': order.get('status')
                        })

                        bot_logger.info(
                            f"Grid {i+1} BUY | Price: {grid_price} | Qty: {quantity:.6f} | "
                            f"Order ID: {order.get('orderId')}"
                        )

                    except Exception as e:
                        bot_logger.warning(f"Failed to place grid buy order at {grid_price}: {e}")
                        continue

                elif grid_price > current_price:
                    # Sell order (upper side) - requires holding position
                    quantity = per_grid_investment / grid_price
                    side = 'SELL'
                    order_type = 'LIMIT'

                    try:
                        order = self.client.client.new_order(
                            symbol=symbol,
                            side=side,
                            type=order_type,
                            quantity=quantity,
                            price=grid_price,
                            timeInForce='GTC',
                            **kwargs
                        )

                        grid_orders.append({
                            'grid_level': i + 1,
                            'side': side,
                            'price': grid_price,
                            'quantity': quantity,
                            'order_id': order.get('orderId'),
                            'status': order.get('status')
                        })

                        bot_logger.info(
                            f"Grid {i+1} SELL | Price: {grid_price} | Qty: {quantity:.6f} | "
                            f"Order ID: {order.get('orderId')}"
                        )

                    except Exception as e:
                        bot_logger.warning(f"Failed to place grid sell order at {grid_price}: {e}")
                        continue

            self.active_grids[symbol] = {
                'lower_price': lower_price,
                'upper_price': upper_price,
                'orders': grid_orders,
                'grid_count': len(grid_orders)
            }

            return {
                'success': True,
                'symbol': symbol,
                'strategy': 'GRID',
                'lower_price': lower_price,
                'upper_price': upper_price,
                'grid_step': grid_step,
                'total_grids': num_grids,
                'active_orders': len(grid_orders),
                'investment_amount': investment_amount,
                'orders': grid_orders
            }

        except ValidationError as e:
            bot_logger.error(f"Validation error in grid strategy: {e}")
            raise
        except Exception as e:
            bot_logger.log_error(
                error_type='GridStrategyError',
                message=str(e),
                symbol=symbol,
                lower_price=lower_price,
                upper_price=upper_price,
                num_grids=num_grids
            )
            raise

    def cancel_grid(self, symbol):
        """
        Cancel all grid orders for a symbol

        Args:
            symbol (str): Trading pair

        Returns:
            dict: Cancellation result
        """
        try:
            if symbol not in self.active_grids:
                raise ValidationError(f"No active grid found for {symbol}")

            grid_info = self.active_grids[symbol]
            cancelled_count = 0

            for order in grid_info['orders']:
                try:
                    self.client.cancel_order(symbol, order['order_id'])
                    cancelled_count += 1
                except Exception as e:
                    bot_logger.warning(f"Failed to cancel grid order {order['order_id']}: {e}")

            del self.active_grids[symbol]
            bot_logger.info(f"Cancelled {cancelled_count} grid orders for {symbol}")

            return {
                'success': True,
                'symbol': symbol,
                'cancelled_orders': cancelled_count
            }

        except Exception as e:
            bot_logger.error(f"Failed to cancel grid: {e}")
            raise


def place_grid_order(symbol, lower_price, upper_price, num_grids, investment_amount):
    """
    Standalone function to place grid strategy orders

    Args:
        symbol (str): Trading pair
        lower_price (float): Lower price boundary
        upper_price (float): Upper price boundary
        num_grids (int): Number of grid levels
        investment_amount (float): Total investment USDT

    Returns:
        dict: Strategy result
    """
    strategy = GridStrategy()
    return strategy.place_order(symbol, lower_price, upper_price, num_grids, investment_amount)
