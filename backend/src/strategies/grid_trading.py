from decimal import Decimal
from typing import Dict, List
from .base_strategy import BaseStrategy

class GridTradingStrategy(BaseStrategy):
    def __init__(self, trading_system, config: Dict):
        super().__init__(trading_system, config)
        self.grid_levels = self._calculate_grid_levels()
        self.active_orders = {}

    def _calculate_grid_levels(self) -> List[Decimal]:
        """Calculate price levels for the grid"""
        upper_price = Decimal(str(self.config['upper_price']))
        lower_price = Decimal(str(self.config['lower_price']))
        num_grids = self.config['num_grids']
        
        price_step = (upper_price - lower_price) / (num_grids - 1)
        return [lower_price + (price_step * i) for i in range(num_grids)]

    async def analyze(self, market_data: Dict) -> Dict:
        if not self.active:
            return {}

        current_price = Decimal(str(market_data['price']))
        signals = []

        for level in self.grid_levels:
            if level not in self.active_orders:
                if current_price > level:
                    signals.append({
                        'type': 'SELL',
                        'price': level,
                        'quantity': self.config['order_quantity']
                    })
                else:
                    signals.append({
                        'type': 'BUY',
                        'price': level,
                        'quantity': self.config['order_quantity']
                    })

        return {'signals': signals}

    async def execute(self, signal: Dict) -> Dict:
        try:
            order = await self.trading_system.place_order(
                symbol=self.config['symbol'],
                side=signal['type'],
                order_type='LIMIT',
                quantity=signal['quantity'],
                price=signal['price']
            )
            
            self.active_orders[signal['price']] = order
            return order
        except Exception as e:
            self.logger.error(f"Error executing grid order: {e}")
            return {}