# Add to TradingSystem class
def __init__(self, ...):
    # ... existing initialization ...
    self.market_maker = MarketMaker(self)
    self.arbitrage = Arbitrage(exchange_configs)
    self.smart_router = SmartOrderRouter(self)
    self.risk_engine = AdvancedRiskEngine()