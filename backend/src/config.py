import os
from decimal import Decimal
from typing import List

class Settings:
    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/crypto_trading")
    
    # CORS settings
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    
    # Security settings
    JWT_SECRET: str = os.getenv("JWT_SECRET", "")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # Exchange settings
    EXCHANGE_NAME: str = os.getenv("EXCHANGE_NAME", "binance")
    EXCHANGE_API_KEY: str = os.getenv("EXCHANGE_API_KEY", "")
    EXCHANGE_API_SECRET: str = os.getenv("EXCHANGE_API_SECRET", "")
    USE_TESTNET: bool = os.getenv("USE_TESTNET", "True").lower() == "true"
    
    # Risk management settings
    MAX_POSITION_SIZE: Decimal = Decimal(os.getenv("MAX_POSITION_SIZE", "0.1"))
    MAX_DRAWDOWN: Decimal = Decimal(os.getenv("MAX_DRAWDOWN", "0.05"))
    
    # Advanced settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    BACKTESTING_MODE: bool = os.getenv("BACKTESTING_MODE", "False").lower() == "true"

settings = Settings()
