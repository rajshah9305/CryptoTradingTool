from decimal import Decimal
import asyncio
import logging
from typing import Dict, List

class MarketMaker:
    """Advanced market making strategy"""
    def __init__(self, trading_system, spread_percentage: Decimal = Decimal('0.002')):
        self.trading_system = trading_system
        self.spread_percentage = spread_percentage
        self.logger = logging.getLogger(__name__)
        self.active_orders: Dict[str, List[str]] = {}

    async def start_market_making(self, symbol: str, base_quantity: Decimal):
        """Start market making for a symbol"""
        try:
            while True:
                orderbook = await self.trading_system.exchange.get_orderbook(symbol)
                mid_price = self._calculate_mid_price(orderbook)
                
                # Calculate bid and ask prices
                bid_price = mid_price * (1 - self.spread_percentage)
                ask_price = mid_price * (1 + self.spread_percentage)

                # Place orders
                await self._place_market_making_orders(
                    symbol, bid_price, ask_price, base_quantity
                )
                
                await asyncio.sleep(5)  # Update every 5 seconds

        except Exception as e:
            self.logger.error(f"Market making error: {e}")

    def _calculate_mid_price(self, orderbook: Dict) -> Decimal:
        """Calculate mid price from orderbook"""
        best_bid = Decimal(str(orderbook['bids'][0][0]))
        best_ask = Decimal(str(orderbook['asks'][0][0]))
        return (best_bid + best_ask) / 2