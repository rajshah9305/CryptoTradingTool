import pytest
from decimal import Decimal
from datetime import datetime
from src.strategies.grid_trading import GridTradingStrategy
from src.core.trading_system import TradingSystem

class TestGridTradingStrategy:
    @pytest.fixture
    def strategy(self):
        config = {
            'symbol': 'BTC/USDT',
            'upper_price': Decimal('45000'),
            'lower_price': Decimal('35000'),
            'grid_levels': 10,
            'quantity': Decimal('0.001')
        }
        return GridTradingStrategy(TradingSystem(), config)

    @pytest.mark.asyncio
    async def test_grid_calculation(self, strategy):
        grid_levels = strategy._calculate_grid_levels()
        assert len(grid_levels) == 10
        assert grid_levels[0] == Decimal('35000')
        assert grid_levels[-1] == Decimal('45000')

    @pytest.mark.asyncio
    async def test_signal_generation(self, strategy):
        market_data = {'price': '40000'}
        signals = await strategy.analyze(market_data)
        assert len(signals['signals']) > 0
        assert all(s['type'] in ['BUY', 'SELL'] for s in signals['signals'])

    @pytest.mark.asyncio
    async def test_risk_management(self, strategy):
        # Test position size limits
        large_order = {
            'type': 'BUY',
            'price': Decimal('40000'),
            'quantity': Decimal('1.0')  # Too large
        }
        with pytest.raises(ValueError):
            await strategy.execute(large_order)