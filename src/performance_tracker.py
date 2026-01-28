"""
Performance tracking and trade statistics
Monitors P&L, win rate, and trading metrics
"""
import json
from datetime import datetime
from src.logger import bot_logger


class PerformanceTracker:
    """Tracks trading performance and statistics"""

    def __init__(self):
        """Initialize performance tracker"""
        self.trades = []
        self.total_profit = 0
        self.total_loss = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_commission = 0

    def record_trade(self, symbol, side, entry_price, exit_price, quantity, commission=0):
        """
        Record a completed trade

        Args:
            symbol (str): Trading pair
            side (str): BUY or SELL
            entry_price (float): Entry price
            exit_price (float): Exit price
            quantity (float): Trade quantity
            commission (float): Fees paid
        """
        # Calculate P&L
        if side == 'BUY':
            pnl = (exit_price - entry_price) * quantity - commission
        else:
            pnl = (entry_price - exit_price) * quantity - commission

        trade_record = {
            'symbol': symbol,
            'side': side,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'quantity': quantity,
            'pnl': pnl,
            'commission': commission,
            'roi': (pnl / (entry_price * quantity)) * 100 if entry_price * quantity > 0 else 0,
            'timestamp': datetime.now().isoformat()
        }

        self.trades.append(trade_record)
        self.total_commission += commission

        if pnl > 0:
            self.total_profit += pnl
            self.winning_trades += 1
        else:
            self.total_loss += abs(pnl)
            self.losing_trades += 1

        bot_logger.log_trade_summary(
            len(self.trades),
            self.get_total_pnl(),
            self.get_win_rate()
        )

    def get_total_pnl(self):
        """Get total profit/loss"""
        return self.total_profit - self.total_loss

    def get_win_rate(self):
        """Get win rate percentage"""
        total_trades = self.winning_trades + self.losing_trades
        return (self.winning_trades / total_trades) if total_trades > 0 else 0

    def get_average_win(self):
        """Get average winning trade size"""
        return (self.total_profit / self.winning_trades) if self.winning_trades > 0 else 0

    def get_average_loss(self):
        """Get average losing trade size"""
        return (self.total_loss / self.losing_trades) if self.losing_trades > 0 else 0

    def get_profit_factor(self):
        """Get profit factor (gross profit / gross loss)"""
        return (self.total_profit / self.total_loss) if self.total_loss > 0 else 0

    def get_summary(self):
        """Get complete performance summary"""
        return {
            'total_trades': len(self.trades),
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': f"{self.get_win_rate():.2%}",
            'total_pnl': f"${self.get_total_pnl():.2f}",
            'total_commission': f"${self.total_commission:.2f}",
            'average_win': f"${self.get_average_win():.2f}",
            'average_loss': f"${self.get_average_loss():.2f}",
            'profit_factor': f"{self.get_profit_factor():.2f}",
            'trades': self.trades
        }

    def export_report(self, filepath='trades_report.json'):
        """Export trade report to JSON"""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.get_summary(), f, indent=2)
            bot_logger.info(f"Trade report exported to {filepath}")
            return filepath
        except Exception as e:
            bot_logger.error(f"Failed to export report: {e}")
            raise


# Global performance tracker
performance_tracker = PerformanceTracker()
