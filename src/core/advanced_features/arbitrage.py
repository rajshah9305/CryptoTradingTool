from decimal import Decimal
import asyncio
import logging
from typing import List, Dict, Tuple

class Arbitrage:
    """Cross-exchange arbitrage strategy"""
    def __init__(self, exchanges: List[Dict]):
        self.exchanges = [Exchange(config) for config in exchanges]
        self.logger = logging.getLogger(__name__)
        self.min_profit_threshold = Decimal('0.001')  # 0.1% minimum profit

    async def find_arbitrage_opportunities(self, symbol: str) -> List[Dict]:
        """Find arbitrage opportunities across exchanges"""
        opportunities = []
        
        try:
            # Get prices from all exchanges
            prices = await asyncio.gather(*[
                exchange.get_orderbook(symbol)
                for exchange in self.exchanges
            ])

            # Find opportunities
            for i, buy_ex in enumerate(self.exchanges):
                for j, sell_ex in enumerate(self.exchanges):
                    if i != j:
                        profit = self._calculate_arbitrage_profit(
                            prices[i], prices[j]
                        )
                        if profit > self.min_profit_threshold:
                            opportunities.append({
                                'buy_exchange': buy_ex.config.name,
                                'sell_exchange': sell_ex.config.name,
                                'symbol': symbol,
                                'profit_percentage': profit,
                                'timestamp': datetime.now()
                            })

            return opportunities

        except Exception as e:
            self.logger.error(f"Arbitrage error: {e}")
            return []