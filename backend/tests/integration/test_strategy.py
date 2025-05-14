import pytest
from decimal import Decimal
from datetime import datetime
import asyncio
from src.strategies.grid_trading import GridTradingStrategy
from src.core.trading_system import TradingSystem

class MockTradingSystem:
    """Mock trading system for testing"""
    
    async def place_order(self, symbol, side, order_type, quantity, price=None):
        # Mock risk validation
        if quantity > Decimal('0.1'):
            raise ValueError("Order exceeds position size limit")
            
        return {
            'symbol': symbol,
            'side': side,
            'order_type': order_type,
            'quantity': quantity,
            'price': price,
            'status': 'NEW',
            'order_id': '12345'
        }
        
    async def get_ticker(self, symbol):
        return {'price': '40000', 'volume': '100', 'timestamp': datetime.now().timestamp()}

class TestGridTradingStrategy:
    @pytest.fixture
    def mock_trading_system(self):
        return MockTradingSystem()
    
    @pytest.fixture
    def strategy(self, mock_trading_system):
        config = {
            'symbol': 'BTC/USDT',
            'upper_price': '45000',
            'lower_price': '35000',
            'num_grids': 10,
            'order_quantity': '0.001'
        }
        return GridTradingStrategy(mock_trading_system, config)

    @pytest.mark.asyncio
    async def test_grid_calculation(self, strategy):
        grid_levels = strategy._calculate_grid_levels()
        assert len(grid_levels) == 10
        assert grid_levels[0] == Decimal('35000')
        assert grid_levels[-1] == Decimal('45000')

    @pytest.mark.asyncio
    async def test_signal_generation(self, strategy):
        # Activate the strategy
        await strategy.start()
        
        market_data = {'price': '40000'}
        signals = await strategy.analyze(market_data)
        
        assert 'signals' in signals
        assert len(signals['signals']) > 0
        assert all(s['type'] in ['BUY', 'SELL'] for s in signals['signals'])

    @pytest.mark.asyncio
    async def test_risk_management(self, strategy, mock_trading_system):
        # Test position size limits
        large_order = {
            'type': 'BUY',
            'price': Decimal('40000'),
            'quantity': Decimal('1.0')  # Too large
        }
        
        with pytest.raises(ValueError):
            await strategy.execute(large_order)
