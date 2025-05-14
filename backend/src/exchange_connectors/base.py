from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from decimal import Decimal
import asyncio
import logging
from datetime import datetime

class ExchangeConnector(ABC):
    def __init__(self, api_key: str, api_secret: str, testnet: bool = False):
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self.logger = logging.getLogger(__name__)
        self.ws_connection = None
        self.subscriptions = set()

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize exchange connection"""
        pass

    @abstractmethod
    async def get_ticker(self, symbol: str) -> Dict:
        """Get current ticker data"""
        pass

    @abstractmethod
    async def get_orderbook(self, symbol: str, limit: int = 100) -> Dict:
        """Get orderbook data"""
        pass

    @abstractmethod
    async def place_order(self, symbol: str, side: str, 
                         order_type: str, quantity: Decimal,
                         price: Optional[Decimal] = None) -> Dict:
        """Place a new order"""
        pass

    @abstractmethod
    async def cancel_order(self, symbol: str, order_id: str) -> Dict:
        """Cancel an existing order"""
        pass

    @abstractmethod
    async def get_balance(self) -> Dict[str, Decimal]:
        """Get account balance"""
        pass

    @abstractmethod
    async def subscribe_to_ticker(self, symbol: str, callback) -> None:
        """Subscribe to real-time ticker updates"""
        pass

    @abstractmethod
    async def subscribe_to_orderbook(self, symbol: str, callback) -> None:
        """Subscribe to real-time orderbook updates"""
        pass