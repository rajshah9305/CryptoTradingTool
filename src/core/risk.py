from dataclasses import dataclass
from decimal import Decimal
import logging
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta

@dataclass
class RiskMetrics:
    var_95: Decimal
    var_99: Decimal
    expected_shortfall: Decimal
    sharpe_ratio: Decimal
    max_drawdown: Decimal
    volatility: Decimal
    beta: Decimal
    timestamp: datetime

class RiskManager:
    def __init__(
        self,
        max_position_size: Decimal,
        max_drawdown: Decimal,
        var_confidence: float = 0.95,
        risk_free_rate: float = 0.02
    ):
        self.logger = logging.getLogger(__name__)
        self.max_position_size = max_position_size
        self.max_drawdown = max_drawdown
        self.var_confidence = var_confidence
        self.risk_free_rate = risk_free_rate
        self.position_limits: Dict[str, Decimal] = {}
        self.metrics_history: List[RiskMetrics] = []
        
    def calculate_position_size(
        self,
        symbol: str,
        price: Decimal,
        volatility: Decimal,
        portfolio_value: Decimal
    ) -> Decimal:
        """Calculate safe position size based on risk metrics"""
        try:
            # Kelly Criterion with safety factor
            kelly_fraction = Decimal('0.5')  # Half-Kelly for safety
            
            # Calculate position limit based on volatility and portfolio value
            vol_adjusted_size = portfolio_value / (volatility * Decimal('10'))
            
            # Apply maximum position size constraint
            position_size = min(
                vol_adjusted_size * kelly_fraction,
                portfolio_value * self.max_position_size
            )
            
            # Store limit for symbol
            self.position_limits[symbol] = position_size
            
            return position_size
            
        except Exception as e:
            self.logger.error(f"Error calculating position size: {e}")
            return Decimal('0')

    def calculate_var(
        self,
        returns: List[Decimal],
        confidence_level: float
    ) -> Decimal:
        """Calculate Value at Risk"""
        try:
            if not returns:
                return Decimal('0')
            
            returns_array = np.array([float(r) for r in returns])
            var = np.percentile(returns_array, (1 - confidence_level) * 100)
            return Decimal(str(abs(var)))
            
        except Exception as e:
            self.logger.error(f"Error calculating VaR: {e}")
            return Decimal('0')

    def calculate_expected_shortfall(
        self,
        returns: List[Decimal],
        var: Decimal
    ) -> Decimal:
        """Calculate Expected Shortfall (CVaR)"""
        try:
            if not returns:
                return Decimal('0')
            
            returns_array = np.array([float(r) for r in returns])
            losses = returns_array[returns_array < float(var)]
            
            if len(losses) > 0:
                es = np.mean(losses)
                return Decimal(str(abs(es)))
            return var
            
        except Exception as e:
            self.logger.error(f"Error calculating Expected Shortfall: {e}")
            return var

    def calculate_metrics(
        self,
        returns: List[Decimal],
        market_returns: Optional[List[Decimal]] = None
    ) -> RiskMetrics:
        """Calculate comprehensive risk metrics"""
        try:
            if not returns:
                return RiskMetrics(
                    var_95=Decimal('0'),
                    var_99=Decimal('0'),
                    expected_shortfall=Decimal('0'),
                    sharpe_ratio=Decimal('0'),
                    max_drawdown=Decimal('0'),
                    volatility=Decimal('0'),
                    beta=Decimal('1'),
                    timestamp=datetime.now()
                )

            # Convert returns to numpy array
            returns_array = np.array([float(r) for r in returns])
            
            # Calculate VaR at different confidence levels
            var_95 = self.calculate_var(returns, 0.95)
            var_99 = self.calculate_var(returns, 0.99)
            
            # Expected Shortfall
            es = self.calculate_expected_shortfall(returns, var_95)
            
            # Volatility
            volatility = Decimal(str(np.std(returns_array)))
            
            # Maximum Drawdown
            cumulative = np.maximum.accumulate(1 + np.cumsum(returns_array))
            drawdowns = 1 - (1 + np.cumsum(returns_array)) / cumulative
            max_drawdown = Decimal(str(np.max(drawdowns)))
            
            # Sharpe Ratio
            excess_returns = np.mean(returns_array) - self.risk_free_rate
            sharpe = Decimal(str(excess_returns / float(volatility)))
            
            # Beta (if market returns provided)
            beta = Decimal('1')
            if market_returns:
                market_array = np.array([float(r) for r in market_returns])
                covariance = np.cov(returns_array, market_array)[0][1]
                market_variance = np.var(market_array)
                if market_variance != 0:
                    beta = Decimal(str(covariance / market_variance))
            
            metrics = RiskMetrics(
                var_95=var_95,
                var_99=var_99,
                expected_shortfall=es,
                sharpe_ratio=sharpe,
                max_drawdown=max_drawdown,
                volatility=volatility,
                beta=beta,
                timestamp=datetime.now()
            )
            
            self.metrics_history.append(metrics)
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating risk metrics: {e}")
            raise

    def check_risk_limits(
        self,
        symbol: str,
        position_size: Decimal,
        current_drawdown: Decimal
    ) -> bool:
        """Check if position meets risk limits"""
        try:
            # Check position size limit
            if symbol in self.position_limits:
                if position_size > self.position_limits[symbol]:
                    self.logger.warning(
                        f"Position size {position_size} exceeds limit "
                        f"{self.position_limits[symbol]} for {symbol}"
                    )
                    return False
            
            # Check drawdown limit
            if current_drawdown > self.max_drawdown:
                self.logger.warning(
                    f"Current drawdown {current_drawdown} exceeds "
                    f"limit {self.max_drawdown}"
                )
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking risk limits: {e}")
            return False

    def get_metrics_history(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[RiskMetrics]:
        """Get historical risk metrics within time range"""
        try:
            if not start_time:
                start_time = datetime.now() - timedelta(days=30)
            if not end_time:
                end_time = datetime.now()
                
            return [
                metrics for metrics in self.metrics_history
                if start_time <= metrics.timestamp <= end_time
            ]
            
        except Exception as e:
            self.logger.error(f"Error retrieving metrics history: {e}")
            return []

    def get_latest_metrics(self) -> Optional[RiskMetrics]:
        """Get most recent risk metrics"""
        try:
            if self.metrics_history:
                return self.metrics_history[-1]
            return None
            
        except Exception as e:
            self.logger.error(f"Error retrieving latest metrics: {e}")
            return None