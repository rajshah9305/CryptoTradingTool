from decimal import Decimal
import asyncio
import logging
from typing import List, Dict, Tuple
from datetime import datetime

from ..exchange import Exchange, ExchangeConfig

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
            
    def _calculate_arbitrage_profit(
        self, 
        buy_orderbook: Dict, 
        sell_orderbook: Dict
    ) -> Decimal:
        """Calculate potential profit from arbitrage between exchanges"""
        try:
            # Get best bid and ask prices
            best_ask = Decimal(str(buy_orderbook['asks'][0][0]))
            best_bid = Decimal(str(sell_orderbook['bids'][0][0]))
            
            # Calculate profit percentage
            profit_percentage = (best_bid / best_ask) - Decimal('1')
            
            # Subtract estimated fees (e.g., 0.1% per trade)
            fee_rate = Decimal('0.001')  # 0.1% fee
            total_fee = fee_rate * Decimal('2')  # Two trades: buy and sell
            profit_percentage -= total_fee
            
            return profit_percentage
        except (IndexError, KeyError) as e:
            self.logger.error(f"Error calculating arbitrage profit: {e}")
            return Decimal('-1')  # Return negative profit on error
            
    async def execute_arbitrage(
        self, 
        opportunity: Dict, 
        amount: Decimal
    ) -> bool:
        """Execute an arbitrage opportunity"""
        try:
            symbol = opportunity['symbol']
            buy_exchange_name = opportunity['buy_exchange']
            sell_exchange_name = opportunity['sell_exchange']
            
            # Find exchange objects
            buy_exchange = next(
                (ex for ex in self.exchanges if ex.config.name == buy_exchange_name),
                None
            )
            sell_exchange = next(
                (ex for ex in self.exchanges if ex.config.name == sell_exchange_name),
                None
            )
            
            if not buy_exchange or not sell_exchange:
                self.logger.error("Exchange not found")
                return False
                
            # Execute buy order
            buy_order = await buy_exchange.create_order(
                symbol, 'market', 'buy', amount
            )
            
            if not buy_order:
                self.logger.error("Failed to execute buy order")
                return False
                
            # Execute sell order
            sell_order = await sell_exchange.create_order(
                symbol, 'market', 'sell', amount
            )
            
            if not sell_order:
                self.logger.error("Failed to execute sell order")
                return False
                
            self.logger.info(
                f"Executed arbitrage: Buy {amount} {symbol} at "
                f"{buy_exchange_name}, Sell at {sell_exchange_name}"
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error executing arbitrage: {e}")
            return False
