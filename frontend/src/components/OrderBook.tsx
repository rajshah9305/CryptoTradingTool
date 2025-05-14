import React from 'react';
import { formatNumber } from '../utils/format';

interface OrderBookProps {
  symbol: string;
  bids: [number, number][];
  asks: [number, number][];
}

export const OrderBook: React.FC<OrderBookProps> = ({ symbol, bids, asks }) => {
  return (
    <div className="grid grid-cols-2 gap-4 p-4 bg-gray-800 rounded-lg">
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