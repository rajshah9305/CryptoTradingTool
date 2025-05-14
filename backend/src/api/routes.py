from fastapi import APIRouter, Depends, HTTPException
from typing import List
from .schemas import (
    OrderCreate, OrderResponse, 
    StrategyCreate, StrategyResponse,
    UserCreate, UserResponse
)
from .dependencies import get_current_user
from core.trading_system import TradingSystem

router = APIRouter()

@router.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate):
    """Create new user"""
    return await UserService.create_user(user)

@router.get("/market/ticker/{symbol}")
async def get_ticker(symbol: str):
    """Get current ticker data"""
    return await TradingSystem.get_ticker(symbol)

@router.get("/market/orderbook/{symbol}")
async def get_orderbook(symbol: str, limit: int = 100):
    """Get orderbook data"""
    return await TradingSystem.get_orderbook(symbol, limit)

@router.post("/orders", response_model=OrderResponse)
async def create_order(
    order: OrderCreate,
    current_user = Depends(get_current_user)
):
    """Place new order"""
    return await TradingSystem.place_order(order, current_user)

@router.get("/orders", response_model=List[OrderResponse])
async def get_orders(
    current_user = Depends(get_current_user)
):
    """Get user's orders"""
    return await TradingSystem.get_orders(current_user)

@router.post("/strategies", response_model=StrategyResponse)
async def create_strategy(
    strategy: StrategyCreate,
    current_user = Depends(get_current_user)
):
    """Create new trading strategy"""
    return await TradingSystem.create_strategy(strategy, current_user)

@router.get("/strategies", response_model=List[StrategyResponse])
async def get_strategies(
    current_user = Depends(get_current_user)
):
    """Get user's strategies"""
    return await TradingSystem.get_strategies(current_user)

@router.post("/strategies/{strategy_id}/start")
async def start_strategy(
    strategy_id: int,
    current_user = Depends(get_current_user)
):
    """Start trading strategy"""
    return await TradingSystem.start_strategy(strategy_id, current_user)

@router.post("/strategies/{strategy_id}/stop")
async def stop_strategy(
    strategy_id: int,
    current_user = Depends(get_current_user)
):
    """Stop trading strategy"""
    return await TradingSystem.stop_strategy(strategy_id, current_user)