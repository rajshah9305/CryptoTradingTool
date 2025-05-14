from decimal import Decimal
import logging
import asyncio
from typing import Dict, List, Optional
from datetime import datetime

from .exchange import Exchange, ExchangeConfig
from .portfolio import Portfolio
from .risk import RiskManager

# Import advanced features
from .advanced_features.market_maker import MarketMaker
from .advanced_features.arbitrage import Arbitrage
from .advanced_features.smart_order_router import SmartOrderRouter
from .advanced_features.risk_engine import AdvancedRiskEngine

class TradingSystem:
    """Main trading system that coordinates all components"""
    
    def __init__(
        self,
        exchange_config: ExchangeConfig,
        initial_balance: Decimal = Decimal('0'),
        exchange_configs: List[Dict] = None
    ):
        self.logger = logging.getLogger(__name__)
        self.exchange = Exchange(exchange_config)
        self.portfolio = Portfolio(initial_balance)
        self.risk_manager = RiskManager(
            max_position_size=Decimal('0.2'),  # 20% of portfolio
            max_drawdown=Decimal('0.1')        # 10% max drawdown
        )
        
        # Initialize advanced features
        self.market_maker = MarketMaker(self)
        
        # If multiple exchange configs provided, initialize arbitrage
        if exchange_configs:
            self.arbitrage = Arbitrage(exchange_configs)
        else:
            self.arbitrage = None
            
        self.smart_router = SmartOrderRouter(self)
        self.risk_engine = AdvancedRiskEngine()
        
        # Trading state
        self.active_orders: Dict[str, Dict] = {}
        self.running: bool = False
        self.symbols: List[str] = []
    
    async def initialize(self):
        """Initialize the trading system"""
        try:
            self.logger.info("Initializing trading system...")
            await self.exchange.initialize()
            self.logger.info("Trading system initialized")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize trading system: {e}")
            return False
    
    async def shutdown(self):
        """Shutdown the trading system"""
        try:
            self.logger.info("Shutting down trading system...")
            
            # Cancel all active orders
            for order_id, order in self.active_orders.items():
                try:
                    await self.exchange.cancel_order(order_id, order['symbol'])
                except Exception as e:
                    self.logger.error(f"Error cancelling order {order_id}: {e}")
            
            # Close exchange connection
            await self.exchange.close()
            
            self.logger.info("Trading system shutdown complete")
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
    
    async def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        amount: Decimal,
        price: Optional[Decimal] = None,
        params: Dict = {}
    ) -> Optional[Dict]:
        """Place an order through the exchange"""
        try:
            # Check risk limits
            portfolio_value = self.portfolio.get_total_value()
            position_value = amount * (
                price or await self._get_current_price(symbol)
            )
            
            # Calculate position size as percentage of portfolio
            position_size = position_value / portfolio_value
            current_drawdown = self.portfolio.max_drawdown
            
            if not self.risk_manager.check_risk_limits(
                symbol, position_size, current_drawdown
            ):
                self.logger.warning(
                    f"Order rejected: Risk limits exceeded for {symbol}"
                )
                return None
            
            # Place order through the exchange
            order = await self.exchange.create_order(
                symbol, order_type, side, amount, price, params
            )
            
            # Save to active orders if not market order
            if order_type != 'market':
                self.active_orders[order['id']] = order
            
            # Update portfolio for market orders (assume instant execution)
            if order_type == 'market':
                exec_price = price or await self._get_current_price(symbol)
                order_amount = amount
                if side == 'sell':
                    order_amount = -order_amount
                
                self.portfolio.update_position(
                    symbol,
                    order_amount,
                    exec_price,
                    datetime.now()
                )
                
                # Record the trade
                self.portfolio.record_trade({
                    'symbol': symbol,
                    'side': side,
                    'price': exec_price,
                    'amount': amount,
                    'type': order_type
                })
                
            return order
            
        except Exception as e:
            self.logger.error(f"Error placing order: {e}")
            return None
    
    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel an existing order"""
        try:
            result = await self.exchange.cancel_order(order_id, symbol)
            if order_id in self.active_orders:
                del self.active_orders[order_id]
            return True
        except Exception as e:
            self.logger.error(f"Error cancelling order: {e}")
            return False
    
    async def start_trading(self, symbols: List[str]):
        """Start automated trading on the specified symbols"""
        try:
            if self.running:
                self.logger.warning("Trading already started")
                return
            
            self.symbols = symbols
            self.running = True
            
            # Start the main trading loop
            asyncio.create_task(self._trading_loop())
            
            self.logger.info(f"Started trading on symbols: {symbols}")
            
        except Exception as e:
            self.logger.error(f"Error starting trading: {e}")
            self.running = False
    
    async def stop_trading(self):
        """Stop automated trading"""
        self.running = False
        self.logger.info("Trading stopped")
    
    async def _trading_loop(self):
        """Main trading loop"""
        try:
            while self.running:
                # Update prices and positions
                await self._update_market_data()
                
                # Check for order updates
                await self._check_order_status()
                
                # Update portfolio and risk metrics
                await self._update_portfolio()
                
                # Sleep to avoid API rate limits
                await asyncio.sleep(1)
                
        except Exception as e:
            self.logger.error(f"Error in trading loop: {e}")
            self.running = False
    
    async def _update_market_data(self):
        """Update market data for all tracked symbols"""
        try:
            # Get latest prices
            await self.exchange.update_prices(self.symbols)
            
            # Update portfolio with new prices
            prices = {
                symbol: self.exchange.last_prices.get(symbol, Decimal('0'))
                for symbol in self.symbols
            }
            self.portfolio.update_prices(prices)
            
        except Exception as e:
            self.logger.error(f"Error updating market data: {e}")
    
    async def _check_order_status(self):
        """Check status of active orders"""
        try:
            for order_id, order in list(self.active_orders.items()):
                try:
                    # Get updated order status
                    updated_order = await self.exchange.exchange.fetch_order(
                        order_id, order['symbol']
                    )
                    
                    # If order is filled, update portfolio
                    if updated_order['status'] == 'closed':
                        symbol = order['symbol']
                        amount = Decimal(str(updated_order['filled']))
                        price = Decimal(str(updated_order['price']))
                        
                        if updated_order['side'] == 'sell':
                            amount = -amount
                            
                        # Update portfolio
                        self.portfolio.update_position(
                            symbol, amount, price, datetime.now()
                        )
                        
                        # Record the trade
                        self.portfolio.record_trade({
                            'symbol': symbol,
                            'side': updated_order['side'],
                            'price': price,
                            'amount': abs(amount),
                            'type': updated_order['type']
                        })
                        
                        # Remove from active orders
                        del self.active_orders[order_id]
                        
                except Exception as e:
                    self.logger.error(
                        f"Error checking order {order_id}: {e}"
                    )
                    
        except Exception as e:
            self.logger.error(f"Error checking order status: {e}")
    
    async def _update_portfolio(self):
        """Update portfolio metrics and risk calculations"""
        try:
            # Get historical data for risk calculations
            returns = {}
            market_returns = []
            
            for symbol in self.symbols:
                ohlcv = await self.exchange.get_ohlcv(
                    symbol, timeframe='1d', limit=30
                )
                
                if ohlcv:
                    # Calculate daily returns
                    closes = [Decimal(str(candle[4])) for candle in ohlcv]
                    symbol_returns = [
                        (closes[i] / closes[i-1]) - Decimal('1')
                        for i in range(1, len(closes))
                    ]
                    returns[symbol] = symbol_returns
                    
                    # Use BTC as market proxy
                    if symbol.endswith('BTC'):
                        market_returns = symbol_returns
            
            # Calculate risk metrics for each position
            for symbol, position in self.portfolio.positions.items():
                if symbol in returns:
                    # Update risk metrics
                    self.risk_manager.calculate_metrics(
                        returns[symbol], market_returns
                    )
                    
                    # Calculate safe position size
                    volatility = self.risk_manager.get_latest_metrics().volatility
                    self.risk_manager.calculate_position_size(
                        symbol,
                        position.current_price,
                        volatility,
                        self.portfolio.get_total_value()
                    )
            
            # Use advanced risk engine for portfolio-level risk
            portfolio_returns = {}
            for symbol, symbol_returns in returns.items():
                if self.portfolio.positions.get(symbol):
                    portfolio_returns[symbol] = symbol_returns
                    
            if portfolio_returns:
                self.risk_engine.calculate_portfolio_risk(
                    {s: self.portfolio.get_position_value(s) 
                     for s in portfolio_returns.keys()},
                    portfolio_returns
                )
                
        except Exception as e:
            self.logger.error(f"Error updating portfolio metrics: {e}")
    
    async def _get_current_price(self, symbol: str) -> Decimal:
        """Get current price for a symbol"""
        try:
            # Use cached price if available
            if symbol in self.exchange.last_prices:
                return self.exchange.last_prices[symbol]
                
            # Otherwise fetch latest price
            ticker = await self.exchange.exchange.fetch_ticker(symbol)
            price = Decimal(str(ticker['last']))
            self.exchange.last_prices[symbol] = price
            return price
            
        except Exception as e:
            self.logger.error(f"Error getting price for {symbol}: {e}")
            raise

    async def execute_arbitrage(self, symbols: List[str]):
        """Find and execute arbitrage opportunities"""
        if not self.arbitrage:
            self.logger.warning("Arbitrage not initialized")
            return []
            
        opportunities = []
        for symbol in symbols:
            symbol_opps = await self.arbitrage.find_arbitrage_opportunities(symbol)
            opportunities.extend(symbol_opps)
            
        return opportunities
        
    async def start_market_making(self, symbol: str, base_quantity: Decimal):
        """Start market making for a symbol"""
        await self.market_maker.start_market_making(symbol, base_quantity)
        
    async def execute_smart_order(
        self,
        symbol: str,
        side: str,
        total_quantity: Decimal,
        algorithm: str = 'twap',
        params: Dict = {}
    ):
        """Execute an order using smart order routing"""
        await self.smart_router.execute_smart_order(
            symbol, side, total_quantity, algorithm, params
        )
