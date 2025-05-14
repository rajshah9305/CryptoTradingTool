import React, { useState } from 'react';
import { useStore } from '../store';
import { StrategyForm } from '../components/StrategyForm';
import { StrategyBacktest } from '../components/StrategyBacktest';
import { StrategyParameters } from '../types/strategy';

export const StrategyConfiguration: React.FC = () => {
  const [selectedStrategy, setSelectedStrategy] = useState<string>('GRID');
  const [backtestResults, setBacktestResults] = useState<any>(null);
  const { createStrategy } = useStore();

  const strategyTemplates = {
    GRID: {
      name: 'Grid Trading',
      parameters: {
        symbol: 'BTC/USDT',
        upperPrice: 40000,
        lowerPrice: 30000,
        gridLevels: 10,
        quantity: 0.001,
      },
      description: 'Automated buying and selling at predefined price levels'
    },
    DCA: {
      name: 'Dollar Cost Averaging',
      parameters: {
        symbol: 'BTC/USDT',
        interval: '1d',
        amount: 100,
        duration: 30,
      },
      description: 'Regular purchases at fixed intervals'
    },
    MOMENTUM: {
      name: 'Momentum Trading',
      parameters: {
        symbol: 'BTC/USDT',
        lookbackPeriod: 14,
        threshold: 0.5,
        stopLoss: 2,
        takeProfit: 4,
      },
      description: 'Trading based on price momentum indicators'
    }
  };

  const handleStrategySubmit = async (parameters: StrategyParameters) => {
    try {
      await createStrategy({
        type: selectedStrategy,
        parameters,
        active: false
      });
    } catch (error) {
      console.error('Failed to create strategy:', error);
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="grid grid-cols-12 gap-6">
        {/* Strategy Selection */}
        <div className="col-span-3">
          <div className="bg-gray-800 rounded-lg p-4">
            <h2 className="text-xl font-bold mb-4">Strategy Templates</h2>
            <div className="space-y-2">
              {Object.entries(strategyTemplates).map(([key, strategy]) => (
                <button
                  key={key}
                  className={`w-full p-3 rounded-lg text-left ${
                    selectedStrategy === key
                      ? 'bg-blue-600'
                      : 'bg-gray-700 hover:bg-gray-600'
                  }`}
                  onClick={() => setSelectedStrategy(key)}
                >
                  <div className="font-semibold">{strategy.name}</div>
                  <div className="text-sm text-gray-400">
                    {strategy.description}
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Strategy Configuration */}
        <div className="col-span-9">
          <div className="bg-gray-800 rounded-lg p-6">
            <h2 className="text-xl font-bold mb-4">
              Configure {strategyTemplates[selectedStrategy].name}
            </h2>
            
            <StrategyForm
              template={strategyTemplates[selectedStrategy]}
              onSubmit={handleStrategySubmit}
            />

            {/* Backtesting Section */}
            <div className="mt-6">
              <h3 className="text-lg font-semibold mb-4">Backtest Strategy</h3>
              <StrategyBacktest
                strategy={selectedStrategy}
                parameters={strategyTemplates[selectedStrategy].parameters}
                onResults={setBacktestResults}
              />
            </div>

            {/* Backtest Results */}
            {backtestResults && (
              <div className="mt-6">
                <h3 className="text-lg font-semibold mb-4">Backtest Results</h3>
                <div className="grid grid-cols-3 gap-4">
                  <div className="bg-gray-700 p-4 rounded-lg">
                    <div className="text-gray-400">Total Return</div>
                    <div className="text-2xl font-bold">
                      {backtestResults.totalReturn.toFixed(2)}%
                    </div>
                  </div>
                  <div className="bg-gray-700 p-4 rounded-lg">
                    <div className="text-gray-400">Sharpe Ratio</div>
                    <div className="text-2xl font-bold">
                      {backtestResults.sharpeRatio.toFixed(2)}
                    </div>
                  </div>
                  <div className="bg-gray-700 p-4 rounded-lg">
                    <div className="text-gray-400">Max Drawdown</div>
                    <div className="text-2xl font-bold">
                      {backtestResults.maxDrawdown.toFixed(2)}%
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};