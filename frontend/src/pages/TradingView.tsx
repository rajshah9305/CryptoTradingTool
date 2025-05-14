import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { TradingChart } from '../components/TradingChart';
import { OrderBook } from '../components/OrderBook';
import { OrderForm } from '../components/OrderForm';
import { useMarketData } from '../hooks/useMarketData';
import { useOrders } from '../hooks/useOrders';
import { useWebSocket } from '../hooks/useWebSocket';

export const TradingView: React.FC = () => {
  const { symbol } = useParams<{ symbol: string }>();
  const { marketData, isLoading: isMarketDataLoading } = useMarketData(symbol);
  const { orders, createOrder } = useOrders();
  const [interval, setInterval] = useState('1m');
  
  const ws = useWebSocket();

  useEffect(() => {
    if (ws) {
      ws.subscribe(`${symbol}@ticker`);
      ws.subscribe(`${symbol}@depth`);
      
      return () => {
        ws.unsubscribe(`${symbol}@ticker`);
        ws.unsubscribe(`${symbol}@depth`);
      };
    }
  }, [ws, symbol]);

  const handleOrderSubmit = async (orderData) => {
    try {
      await createOrder({
        symbol,
        ...orderData
      });
    } catch (error) {
      console.error('Order submission failed:', error);
    }
  };

  if (isMarketDataLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="grid grid-cols-12 gap-4 p-4">
      <div className="col-span-9">
        <TradingChart
          symbol={symbol}
          interval={interval}
          data={marketData.candles}
        />
        <div className="flex space-x-2 mt-4">
          {['1m', '5m', '15m', '1h', '4h', '1d'].map((i) => (
            <button
              key={i}
              className={`px-3 py-1 rounded ${
                interval === i ? 'bg-blue-500' : 'bg-gray-700'
              }`}
              onClick={() => setInterval(i)}
            >
              {i}
            </button>
          ))}
        </div>
      </div>
      
      <div className="col-span-3 space-y-4">
        <OrderBook
          symbol={symbol}
          bids={marketData.orderbook.bids}
          asks={marketData.orderbook.asks}
        />
        <OrderForm onSubmit={handleOrderSubmit} />
      </div>
    </div>
  );
};