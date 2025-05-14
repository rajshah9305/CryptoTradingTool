import hmac
import time
import hashlib
from typing import Dict, List, Optional
from decimal import Decimal
import aiohttp
import json
import websockets
import logging
from .base import ExchangeConnector

class BinanceConnector(ExchangeConnector):
    def __init__(self, api_key: str, api_secret: str, testnet: bool = False):
        super().__init__(api_key, api_secret, testnet)
        self.base_url = "https://testnet.binance.vision/api" if testnet else "https://api.binance.com/api"
        self.ws_url = "wss://testnet.binance.vision/ws" if testnet else "wss://stream.binance.com:9443/ws"
        self.session = None

    async def initialize(self) -> None:
        self.session = aiohttp.ClientSession()
        self.logger.info("Binance connector initialized")

    async def _get(self, endpoint: str, params: Dict = None) -> Dict:
        async with self.session.get(f"{self.base_url}{endpoint}", params=params) as response:
            return await response.json()

    async def _post(self, endpoint: str, params: Dict = None) -> Dict:
        timestamp = int(time.time() * 1000)
        params = params or {}
        params['timestamp'] = timestamp
        
        # Create signature
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        params['signature'] = signature
        headers = {'X-MBX-APIKEY': self.api_key}
        
        async with self.session.post(
            f"{self.base_url}{endpoint}",
            params=params,
            headers=headers
        ) as response:
            return await response.json()

    async def get_ticker(self, symbol: str) -> Dict:
        return await self._get('/v3/ticker/24hr', {'symbol': symbol})

    async def get_orderbook(self, symbol: str, limit: int = 100) -> Dict:
        return await self._get('/v3/depth', {'symbol': symbol, 'limit': limit})

    async def place_order(self, symbol: str, side: str, 
                         order_type: str, quantity: Decimal,
                         price: Optional[Decimal] = None) -> Dict:
        params = {
            'symbol': symbol,
            'side': side.upper(),
            'type': order_type.upper(),
            'quantity': str(quantity)
        }
        
        if price:
            params['price'] = str(price)
            
        return await self._post('/v3/order', params)

    async def cancel_order(self, symbol: str, order_id: str) -> Dict:
        return await self._post('/v3/order', {
            'symbol': symbol,
            'orderId': order_id
        })

    async def get_balance(self) -> Dict[str, Decimal]:
        response = await self._get('/v3/account')
        return {
            balance['asset']: Decimal(balance['free'])
            for balance in response['balances']
            if float(balance['free']) > 0
        }

    async def subscribe_to_ticker(self, symbol: str, callback) -> None:
        stream = f"{symbol.lower()}@ticker"
        if stream not in self.subscriptions:
            self.subscriptions.add(stream)
            asyncio.create_task(self._handle_websocket(stream, callback))

    async def subscribe_to_orderbook(self, symbol: str, callback) -> None:
        stream = f"{symbol.lower()}@depth"
        if stream not in self.subscriptions:
            self.subscriptions.add(stream)
            asyncio.create_task(self._handle_websocket(stream, callback))

    async def _handle_websocket(self, stream: str, callback) -> None:
        while True:
            try:
                async with websockets.connect(f"{self.ws_url}/{stream}") as ws:
                    self.logger.info(f"Connected to stream: {stream}")
                    async for message in ws:
                        await callback(json.loads(message))
            except Exception as e:
                self.logger.error(f"WebSocket error: {e}")
                await asyncio.sleep(5)  # Reconnection delay