import React from 'react';
import { usePortfolio } from '../hooks/usePortfolio';
import { useActiveStrategies } from '../hooks/useStrategies';
import { PortfolioChart } from '../components/PortfolioChart';
import { PositionsTable } from '../components/PositionsTable';
import { ActiveStrategies } from '../components/ActiveStrategies';
import { RecentTrades } from '../components/RecentTrades';

export const Dashboard: React.FC = () => {
  const { portfolio, isLoading: isPortfolioLoading } = usePortfolio();
  const { strategies, isLoading: isStrategiesLoading } = useActiveStrategies();

  if (isPortfolioLoading || isStrategiesLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="p-6 space-y-6">
      {/* Portfolio Summary */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-gray-800 p-4 rounded-lg">
          <h3 className="text-gray-400">Total Balance</h3>
          <p className="text-2xl font-bold">
            ${portfolio.totalBalance.toFixed(2)}
          </p>
        </div>
        <div className="bg-gray-800 p-4 rounded-lg">
          <h3 className="text-gray-400">24h PnL</h3>
          <p className={`text-2xl font-bold ${
            portfolio.dailyPnL >= 0 ? 'text-green-500' : 'text-red-500'
          }`}>
            {portfolio.dailyPnL >= 0 ? '+' : ''}
            ${portfolio.dailyPnL.toFixed(2)}
          </p>
        </div>
        <div className="bg-gray-800 p-4 rounded-lg">
          <h3 className="text-gray-400">Active Positions</h3>
          <p className="text-2xl font-bold">
            {portfolio.positions.length}
          </p>
        </div>
        <div className="bg-gray-800 p-4 rounded-lg">
          <h3 className="text-gray-400">Active Strategies</h3>
          <p className="text-2xl font-bold">
            {strategies.length}
          </p>
        </div>
      </div>

      {/* Portfolio Chart */}
      <div className="bg-gray-800 p-4 rounded-lg">
        <h2 className="text-xl font-bold mb-4">Portfolio Performance</h2>
        <PortfolioChart data={portfolio.history} />
      </div>

      {/* Positions and Strategies */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-gray-800 p-4 rounded-lg">
          <h2 className="text-xl font-bold mb-4">Active Positions</h2>
          <PositionsTable positions={portfolio.positions} />
        </div>
        <div className="bg-gray-800 p-4 rounded-lg">
          <h2 className="text-xl font-bold mb-4">Active Strategies</h2>
          <ActiveStrategies strategies={strategies} />
        </div>
      </div>

      {/* Recent Trades */}
      <div className="bg-gray-800 p-4 rounded-lg">
        <h2 className="text-xl font-bold mb-4">Recent Trades</h2>
        <RecentTrades trades={portfolio.recentTrades} />
      </div>
    </div>
  );
};