"""
Main CLI interface for Binance Futures Trading Bot
Provides command-line access to all order types and strategies
"""
import sys
import argparse
from src.config import Config
from src.logger import bot_logger
from src.validators import ValidationError
from src.market_orders import place_market_order
from src.limit_orders import place_limit_order
from src.advanced.stop_limit import place_stop_limit_order
from src.advanced.oco import place_oco_order
from src.advanced.twap import place_twap_order
from src.advanced.grid import place_grid_order
from src.performance_tracker import performance_tracker


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Binance Futures Trading Bot - CLI Interface',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Market Order
  python bot.py market --symbol BTCUSDT --side BUY --quantity 0.01

  # Limit Order
  python bot.py limit --symbol BTCUSDT --side BUY --quantity 0.01 --price 40000

  # Stop-Limit Order
  python bot.py stop-limit --symbol BTCUSDT --side SELL --quantity 0.01 --stop 38000 --limit 37500

  # OCO Order
  python bot.py oco --symbol BTCUSDT --side BUY --quantity 0.01 --take-profit 42000 --stop-loss 38000

  # TWAP Strategy
  python bot.py twap --symbol BTCUSDT --side BUY --quantity 1.0 --orders 5 --interval 60

  # Grid Strategy
  python bot.py grid --symbol BTCUSDT --lower 40000 --upper 42000 --grids 10 --investment 1000
        '''
    )

    subparsers = parser.add_subparsers(dest='command', help='Order type')

    # Market Order
    market_parser = subparsers.add_parser('market', help='Place a market order')
    market_parser.add_argument('--symbol', required=True, help='Trading pair (e.g., BTCUSDT)')
    market_parser.add_argument('--side', required=True, choices=['BUY', 'SELL'], help='Order side')
    market_parser.add_argument('--quantity', required=True, type=float, help='Order quantity')

    # Limit Order
    limit_parser = subparsers.add_parser('limit', help='Place a limit order')
    limit_parser.add_argument('--symbol', required=True, help='Trading pair')
    limit_parser.add_argument('--side', required=True, choices=['BUY', 'SELL'], help='Order side')
    limit_parser.add_argument('--quantity', required=True, type=float, help='Order quantity')
    limit_parser.add_argument('--price', required=True, type=float, help='Limit price')

    # Stop-Limit Order
    stop_limit_parser = subparsers.add_parser('stop-limit', help='Place a stop-limit order')
    stop_limit_parser.add_argument('--symbol', required=True, help='Trading pair')
    stop_limit_parser.add_argument('--side', required=True, choices=['BUY', 'SELL'], help='Order side')
    stop_limit_parser.add_argument('--quantity', required=True, type=float, help='Order quantity')
    stop_limit_parser.add_argument('--stop', required=True, type=float, help='Stop trigger price')
    stop_limit_parser.add_argument('--limit', required=True, type=float, help='Limit price')

    # OCO Order
    oco_parser = subparsers.add_parser('oco', help='Place an OCO (One-Cancels-Other) order')
    oco_parser.add_argument('--symbol', required=True, help='Trading pair')
    oco_parser.add_argument('--side', required=True, choices=['BUY', 'SELL'], help='Order side')
    oco_parser.add_argument('--quantity', required=True, type=float, help='Order quantity')
    oco_parser.add_argument('--take-profit', required=True, type=float, help='Take profit price')
    oco_parser.add_argument('--stop-loss', required=True, type=float, help='Stop loss price')

    # TWAP Strategy
    twap_parser = subparsers.add_parser('twap', help='Execute TWAP (Time-Weighted Avg Price) strategy')
    twap_parser.add_argument('--symbol', required=True, help='Trading pair')
    twap_parser.add_argument('--side', required=True, choices=['BUY', 'SELL'], help='Order side')
    twap_parser.add_argument('--quantity', required=True, type=float, help='Total quantity')
    twap_parser.add_argument('--orders', required=True, type=int, help='Number of orders')
    twap_parser.add_argument('--interval', required=True, type=int, help='Seconds between orders')

    # Grid Strategy
    grid_parser = subparsers.add_parser('grid', help='Execute Grid trading strategy')
    grid_parser.add_argument('--symbol', required=True, help='Trading pair')
    grid_parser.add_argument('--lower', required=True, type=float, help='Lower price boundary')
    grid_parser.add_argument('--upper', required=True, type=float, help='Upper price boundary')
    grid_parser.add_argument('--grids', required=True, type=int, help='Number of grid levels')
    grid_parser.add_argument('--investment', required=True, type=float, help='Investment amount (USDT)')

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == 'market':
            result = place_market_order(args.symbol, args.side, args.quantity)
            print_success("Market Order Placed Successfully", result)

        elif args.command == 'limit':
            result = place_limit_order(args.symbol, args.side, args.quantity, args.price)
            print_success("Limit Order Placed Successfully", result)

        elif args.command == 'stop-limit':
            result = place_stop_limit_order(
                args.symbol, args.side, args.quantity, args.stop, args.limit
            )
            print_success("Stop-Limit Order Placed Successfully", result)

        elif args.command == 'oco':
            result = place_oco_order(
                args.symbol, args.side, args.quantity, args.take_profit, args.stop_loss
            )
            print_success("OCO Order Placed Successfully", result)

        elif args.command == 'twap':
            result = place_twap_order(
                args.symbol, args.side, args.quantity, args.orders, args.interval
            )
            print_success("TWAP Strategy Executed Successfully", result)

        elif args.command == 'grid':
            result = place_grid_order(
                args.symbol, args.lower, args.upper, args.grids, args.investment
            )
            print_success("Grid Strategy Placed Successfully", result)

    except ValidationError as e:
        print_error(f"Validation Error: {e}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error: {e}")
        sys.exit(1)


def print_success(title, data):
    """Print success message with formatted data"""
    print("\n" + "="*60)
    print(f"✓ {title}")
    print("="*60)
    for key, value in data.items():
        if not isinstance(value, (dict, list)):
            print(f"  {key.replace('_', ' ').title()}: {value}")
    print("="*60 + "\n")


def print_error(message):
    """Print error message"""
    print("\n" + "="*60)
    print(f"✗ Error")
    print("="*60)
    print(f"  {message}")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
