import React from 'react';
import { formatNumber } from '../utils/format';

interface OrderBookProps {
  symbol: string;
  bids: [number, number][];
  asks: [number, number][];
}

export const OrderBook: React.FC<OrderBookProps> = ({ symbol, bids, asks }) => {
  // Calculate the spread (difference between lowest ask and highest bid)
  const highestBid = bids.length > 0 ? bids[0][0] : 0;
  const lowestAsk = asks.length > 0 ? asks[0][0] : 0;
  const spread = lowestAsk - highestBid;
  const spreadPercentage = highestBid > 0 ? (spread / highestBid) * 100 : 0;

  return (
    <div className="grid grid-cols-2 gap-4 p-4 bg-gray-800 rounded-lg">
      {/* Display the spread information */}
      <div className="col-span-2 mb-2 text-center">
        <span className="text-gray-400 mr-2">Spread:</span>
        <span className="text-white" data-testid="spread">
          {formatNumber(spread)} ({formatNumber(spreadPercentage, 2)}%)
        </span>
      </div>
      
      <div>
        <h3 className="text-green-500 font-semibold mb-2">Bids</h3>
        <div className="space-y-1">
          {bids.map(([price, quantity]) => (
            <div key={price} className="flex justify-between">
              <span className="text-green-400">
                {formatNumber(price)}
              </span>
              <span className="text-gray-300">
                {formatNumber(quantity)}
              </span>
            </div>
          ))}
        </div>
      </div>
      
      <div>
        <h3 className="text-red-500 font-semibold mb-2">Asks</h3>
        <div className="space-y-1">
          {asks.map(([price, quantity]) => (
            <div key={price} className="flex justify-between">
              <span className="text-red-400">
                {formatNumber(price)}
              </span>
              <span className="text-gray-300">
                {formatNumber(quantity)}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
