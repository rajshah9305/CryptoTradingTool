import React, { useState } from 'react';
import { usePerformanceData } from '../hooks/usePerformanceData';
import { PerformanceChart } from '../components/PerformanceChart';
import { MetricsCard } from '../components/MetricsCard';
import { DateRangePicker } from '../components/DateRangePicker';
import { TradeList } from '../components/TradeList';
import { formatCurrency, formatPercentage } from '../utils/format';

export const PerformanceAnalytics: React.FC = () => {
  const [dateRange, setDateRange] = useState({
    start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
    end: new Date()
  });

  const { data, isLoading } = usePerformanceData(dateRange);

  if (isLoading) {
    return <div>Loading performance data...</div>;
  }

  return (
    <div className="p-6">
      {/* Date Range Selection */}
      <div className="mb-6 flex justify-between items-center">
        <h1 className="text-2xl font-bold">Performance Analytics</h1>
        <DateRangePicker
          startDate={dateRange.start}
          endDate={dateRange.end}
          onChange={setDateRange}
        />
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <MetricsCard
          title="Total Return"
          value={formatPercentage(data.totalReturn)}
          trend={data.totalReturn >= 0 ? 'up' : 'down'}
        />
        <MetricsCard
          title="Win Rate"
          value={formatPercentage(data.winRate)}
          subtext={`${data.winningTrades}/${data.totalTrades} trades`}
        />
        <MetricsCard
          title="Profit Factor"
          value={data.profitFactor.toFixed(2)}
        />
        <MetricsCard
          title="Sharpe Ratio"
          value={data.sharpeRatio.toFixed(2)}
        />
      </div>

      {/* Performance Chart */}
      <div className="bg-gray-800 rounded-lg p-6 mb-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">Equity Curve</h2>
          <div className="flex space-x-2">
            <button className="px-3 py-1 rounded bg-gray-700">Daily</button>
            <button className="px-3 py-1 rounded bg-gray-700">Weekly</button>
            <button className="px-3 py-1 rounded bg-gray-700">Monthly</button>
          </div>
        </div>
        <PerformanceChart data={data.equityCurve} />
      </div>

      {/* Detailed Metrics */}
      <div className="grid grid-cols-2 gap-6 mb-6">
        {/* Returns Analysis */}
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-bold mb-4">Returns Analysis</h2>
          <div className="space-y-4">
            <div className="flex justify-between">
              <span>Average Trade Return</span>
              <span>{formatPercentage(data.avgTradeReturn)}</span>
            </div>
            <div className="flex justify-between">
              <span>Best Trade</span>
              <span className="text-green-500">
                {formatPercentage(data.bestTrade)}
              </span>
            </div>
            <div className="flex justify-between">
              <span>Worst Trade</span>
              <span className="text-red-500">
                {formatPercentage(data.worstTrade)}
              </span>
            </div>
            <div className="flex justify-between">
              <span>Maximum Drawdown</span>
              <span className="text-red-500">
                {formatPercentage(data.maxDrawdown)}
              </span>
            </div>
          </div>
        </div>

        {/* Risk Metrics */}
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-bold mb-4">Risk Metrics</h2>
          <div className="space-y-4">
            <div className="flex justify-between">
              <span>Value at Risk (95%)</span>
              <span>{formatCurrency(data.valueAtRisk)}</span>
            </div>
            <div className="flex justify-between">
              <span>Beta</span>
              <span>{data.beta.toFixed(2)}</span>
            </div>
            <div className="flex justify-between">
              <span>Sortino Ratio</span>
              <span>{data.sortinoRatio.toFixed(2)}</span>
            </div>
            <div className="flex justify-between">
              <span>Max Leverage Used</span>
              <span>{data.maxLeverage.toFixed(2)}x</span>
            </div>
          </div>
        </div>
      </div>

      {/* Trade History */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-xl font-bold mb-4">Trade History</h2>
        <TradeList trades={data.trades} />
      </div>
    </div>
  );
};