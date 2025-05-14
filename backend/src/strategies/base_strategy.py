from abc import ABC, abstractmethod
from typing import Dict, List
from decimal import Decimal
import logging
from datetime import datetime

class BaseStrategy(ABC):
    def __init__(self, trading_system, config: Dict):
        self.trading_system = trading_system
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.active = False
        self.positions = {}

    @abstractmethod
    async def analyze(self, market_data: Dict) -> Dict:
        """Analyze market data and generate signals"""
        pass

    @abstractmethod
    async def execute(self, signal: Dict) -> Dict:
        """Execute trading signals"""
        pass

    async def start(self) -> None:
        """Start the strategy"""
        self.active = True
        self.logger.info(f"Strategy {self.__class__.__name__} started")

    async def stop(self) -> None:
        """Stop the strategy"""
        self.active = False
        self.logger.info(f"Strategy {self.__class__.__name__} stopped")

    async def update_position(self, symbol: str, position: Dict) -> None:
        """Update strategy position"""
        self.positions[symbol] = position