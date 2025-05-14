from fastapi import FastAPI, WebSocket, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging
from typing import List, Dict, Any
import json

from core.trading_system import TradingSystem
from api.routes import router as api_router
from database.session import init_db
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create trading_system instance with proper configuration
async def get_trading_system() -> TradingSystem:
    # Singleton pattern - create or return existing instance
    if not hasattr(get_trading_system, "instance"):
        logger.info("Initializing TradingSystem")
        config = {
            'exchange': {
                'name': settings.EXCHANGE_NAME,
                'api_key': settings.EXCHANGE_API_KEY,
                'api_secret': settings.EXCHANGE_API_SECRET,
                'testnet': settings.USE_TESTNET
            },
            'risk': {
                'max_position_size': settings.MAX_POSITION_SIZE,
                'max_drawdown': settings.MAX_DRAWDOWN
            }
        }
        # Create a single trading system instance
        get_trading_system.instance = TradingSystem(config)
        await get_trading_system.instance.initialize()
    return get_trading_system.instance

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    # Pre-initialize the trading system
    trading_system = await get_trading_system()
    logger.info("Trading system initialized successfully")
    yield
    # Shutdown
    logger.info("Shutting down trading system")
    await trading_system.shutdown()

app = FastAPI(
    title="Crypto Trading Tool API",
    description="Professional-grade cryptocurrency trading API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict[str, Any]):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, trading_system: TradingSystem = Depends(get_trading_system)):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            # Process received data
            response = await trading_system.process_ws_message(data)
            if response:
                await websocket.send_json(response)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
