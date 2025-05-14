from dataclasses import dataclass
from decimal import Decimal
import logging
from typing import Dict, List, Optional
from datetime import datetime

@dataclass
class Position:
    symbol: str
    amount: Decimal
    entry_price: Decimal
    current_price: Decimal
    unrealized_pnl: Decimal
    realized_pnl: Decimal
    timestamp: datetime

class Portfolio:
    def __init__(self, initial_balance: Decimal = Decimal('0')):
        self.logger = logging.getLogger(__name__)
        self.balance = initial_balance
        self.positions: Dict[str, Position] = {}
        self.trades_history: List[Dict] = []
        self.total_pnl = Decimal('0')
        self.max_drawdown = Decimal('0')
        self.peak_value = initial_balance

    def update_position(
        self,
        symbol: str,
        amount: Decimal,
        price: Decimal,
        timestamp: datetime
    ) -> Position:
        """Update or create a position"""
        try:
            if symbol in self.positions:
                current_pos = self.positions[symbol]
                new_amount = current_pos.amount + amount
                
                if new_amount == 0:
                    # Position closed
                    realized_pnl = (price - current_pos.entry_price) * abs(amount)
                    self.total_pnl += realized_pnl
                    self.balance += realized_pnl
                    del self.positions[symbol]
                    self._update_metrics()
                    return Position(
                        symbol=symbol,
                        amount=Decimal('0'),
                        entry_price=Decimal('0'),
                        current_price=price,
                        unrealized_pnl=Decimal('0'),
                        realized_pnl=realized_pnl,
                        timestamp=timestamp
                    )
                else:
                    # Update existing position
                    entry_price = (
                        (current_pos.entry_price * current_pos.amount) +
                        (price * amount)
                    ) / new_amount
                    
                    position = Position(
                        symbol=symbol,
                        amount=new_amount,
                        entry_price=entry_price,
                        current_price=price,
                        unrealized_pnl=Decimal('0'),
                        realized_pnl=Decimal('0'),
                        timestamp=timestamp
                    )
                    self.positions[symbol] = position
                    return position
            else:
                # New position
                position = Position(
                    symbol=symbol,
                    amount=amount,
                    entry_price=price,
                    current_price=price,
                    unrealized_pnl=Decimal('0'),
                    realized_pnl=Decimal('0'),
                    timestamp=timestamp
                )
                self.positions[symbol] = position
                return position
                
        except Exception as e:
            self.logger.error(f"Error updating position: {e}")
            raise

    def update_prices(self, prices: Dict[str, Decimal]) -> None:
        """Update current prices and unrealized P&L"""
        try:
            total_value = self.balance
            
            for symbol, position in self.positions.items():
                if symbol in prices:
                    current_price = prices[symbol]
                    position.current_price = current_price
                    position.unrealized_pnl = (
                        current_price - position.entry_price
                    ) * position.amount
                    total_value += position.unrealized_pnl
            
            self._update_metrics(total_value)
            
        except Exception as e:
            self.logger.error(f"Error updating prices: {e}")
            raise

    def _update_metrics(self, current_value: Optional[Decimal] = None) -> None:
        """Update portfolio metrics"""
        try:
            if current_value is not None:
                if current_value > self.peak_value:
                    self.peak_value = current_value
                
                drawdown = (self.peak_value - current_value) / self.peak_value
                if drawdown > self.max_drawdown:
                    self.max_drawdown = drawdown
        
        except Exception as e:
            self.logger.error(f"Error updating metrics: {e}")

    def get_position_value(self, symbol: str) -> Decimal:
        """Get current value of a position"""
        try:
            position = self.positions.get(symbol)
            if position:
                return position.amount * position.current_price
            return Decimal('0')
        except Exception as e:
            self.logger.error(f"Error calculating position value: {e}")
            return Decimal('0')

    def get_total_value(self) -> Decimal:
        """Get total portfolio value including unrealized P&L"""
        try:
            positions_value = sum(
                pos.amount * pos.current_price
                for pos in self.positions.values()
            )
            return self.balance + positions_value
        except Exception as e:
            self.logger.error(f"Error calculating total value: {e}")
            return self.balance

    def record_trade(self, trade: Dict) -> None:
        """Record a trade in history"""
        try:
            self.trades_history.append({
                **trade,
                'portfolio_value': self.get_total_value(),
                'timestamp': datetime.now()
            })
        except Exception as e:
            self.logger.error(f"Error recording trade: {e}")

    def get_position_summary(self) -> Dict[str, Dict]:
        """Get summary of all positions"""
        return {
            symbol: {
                'amount': pos.amount,
                'entry_price': pos.entry_price,
                'current_price': pos.current_price,
                'unrealized_pnl': pos.unrealized_pnl,
                'value': self.get_position_value(symbol)
            }
            for symbol, pos in self.positions.items()
        }

    def get_metrics(self) -> Dict:
        """Get portfolio metrics"""
        return {
            'total_value': self.get_total_value(),
            'balance': self.balance,
            'total_pnl': self.total_pnl,
            'max_drawdown': self.max_drawdown,
            'peak_value': self.peak_value,
            'open_positions': len(self.positions),
            'total_trades': len(self.trades_history)
        }