from dataclasses import dataclass
from decimal import Decimal
import asyncio
import logging
from typing import Dict, List, Optional, Tuple
import ccxt.async_support as ccxt
from datetime import datetime

@dataclass
class ExchangeConfig:
    name: str
    api_key: str
    api_secret: str
    testnet: bool = True
    timeout: int = 30000
    enableRateLimit: bool = True

class Exchange:
    def __init__(self, config: ExchangeConfig):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.exchange: ccxt.Exchange = self._initialize_exchange()
        self.markets: Dict = {}
        self.orderbook_cache: Dict[str, Dict] = {}
        self.last_prices: Dict[str, Decimal] = {}
        
    def _initialize_exchange(self) -> ccxt.Exchange:
        try:
            exchange_class = getattr(ccxt, self.config.name)
            exchange = exchange_class({
                'apiKey': self.config.api_key,
                'secret': self.config.api_secret,
                'timeout': self.config.timeout,
                'enableRateLimit': self.config.enableRateLimit
            })
            
            if self.config.testnet:
                exchange.set_sandbox_mode(True)
            
            return exchange
        except Exception as e:
            self.logger.error(f"Failed to initialize exchange: {e}")
            raise

    async def initialize(self):
        """Initialize exchange connection and load markets"""
        try:
            self.markets = await self.exchange.load_markets()
            self.logger.info(f"Initialized {self.config.name} exchange")
        except Exception as e:
            self.logger.error(f"Failed to load markets: {e}")
            raise

    async def close(self):
        """Close exchange connection"""
        try:
            await self.exchange.close()
            self.logger.info("Exchange connection closed")
        except Exception as e:
            self.logger.error(f"Error closing exchange connection: {e}")

    async def get_orderbook(self, symbol: str, limit: int = 20) -> Dict:
        """Get real-time orderbook for symbol"""
        try:
            orderbook = await self.exchange.fetch_order_book(symbol, limit)
            self.orderbook_cache[symbol] = {
                'bids': orderbook['bids'],
                'asks': orderbook['asks'],
                'timestamp': datetime.now().timestamp()
            }
            return orderbook
        except Exception as e:
            self.logger.error(f"Error fetching orderbook for {symbol}: {e}")
            return self.orderbook_cache.get(symbol, {})

    async def create_order(
        self,
        symbol: str,
        order_type: str,
        side: str,
        amount: Decimal,
        price: Optional[Decimal] = None,
        params: Dict = {}
    ) -> Dict:
        """Create a new order"""
        try:
            order = await self.exchange.create_order(
                symbol,
                order_type,
                side,
                float(amount),
                float(price) if price else None,
                params
            )
            self.logger.info(f"Created {side} order for {amount} {symbol} at {price}")
            return order
        except Exception as e:
            self.logger.error(f"Error creating order: {e}")
            raise

    async def cancel_order(self, order_id: str, symbol: str) -> Dict:
        """Cancel an existing order"""
        try:
            result = await self.exchange.cancel_order(order_id, symbol)
            self.logger.info(f"Cancelled order {order_id} for {symbol}")
            return result
        except Exception as e:
            self.logger.error(f"Error cancelling order: {e}")
            raise

    async def get_balance(self) -> Dict[str, Decimal]:
        """Get account balance"""
        try:
            balance = await self.exchange.fetch_balance()
            return {
                currency: Decimal(str(amount['free']))
                for currency, amount in balance['total'].items()
                if amount['free'] > 0
            }
        except Exception as e:
            self.logger.error(f"Error fetching balance: {e}")
            raise

    async def get_positions(self) -> List[Dict]:
        """Get open positions"""
        try:
            positions = await self.exchange.fetch_positions()
            return [
                position for position in positions
                if float(position['contracts']) > 0
            ]
        except Exception as e:
            self.logger.error(f"Error fetching positions: {e}")
            return []

    async def get_ohlcv(
        self,
        symbol: str,
        timeframe: str = '1m',
        limit: int = 100
    ) -> List[List]:
        """Get OHLCV candle data"""
        try:
            ohlcv = await self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            return ohlcv
        except Exception as e:
            self.logger.error(f"Error fetching OHLCV data: {e}")
            return []

    async def update_prices(self, symbols: List[str]):
        """Update last prices for multiple symbols"""
        try:
            tickers = await self.exchange.fetch_tickers(symbols)
            self.last_prices.update({
                symbol: Decimal(str(ticker['last']))
                for symbol, ticker in tickers.items()
            })
        except Exception as e:
            self.logger.error(f"Error updating prices: {e}")

    def get_market_info(self, symbol: str) -> Dict:
        """Get market information for symbol"""
        try:
            return self.markets[symbol]
        except KeyError:
            self.logger.error(f"Market information not found for {symbol}")
            raise ValueError(f"Invalid symbol: {symbol}")