import pytest
from decimal import Decimal
from src.core.trading_system import TradingSystem
from src.core.exchange import Exchange
from src.core.portfolio import Portfolio

@pytest.fixture
def trading_system():
    config = {
        'exchange': {
            'name': 'binance',
            'api_key': 'test_key',
            'api_secret': 'test_secret',
            'testnet': True
        },
        'risk': {
            'max_position_size': Decimal('0.1'),
            'max_drawdown': Decimal('0.05')
        }
    }
    return TradingSystem(config)

async def test_place_order(trading_system):
    order = await trading_system.place_order(
        symbol='BTC/USDT',
        side='BUY',
        order_type='LIMIT',
        quantity=Decimal('0.01'),
        price=Decimal('40000')
    )
    assert order['symbol'] == 'BTC/USDT'
    assert order['side'] == 'BUY'
    assert order['status'] == 'NEW'

async def test_risk_limits(trading_system):
    # Try to place order exceeding risk limits
    with pytest.raises(ValueError):
        await trading_system.place_order(
            symbol='BTC/USDT',
            side='BUY',
            order_type='LIMIT',
            quantity=Decimal('1.0'),  # Exceeds max position size
            price=Decimal('40000')
        )