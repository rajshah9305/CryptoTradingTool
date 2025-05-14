import create from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { MarketData, Order, Position, Strategy } from '../types';

interface Store {
  // Market Data
  marketData: Record<string, MarketData>;
  setMarketData: (symbol: string, data: MarketData) => void;

  // Orders
  orders: Order[];
  addOrder: (order: Order) => void;
  updateOrder: (orderId: string, updates: Partial<Order>) => void;
  
  // Positions
  positions: Position[];
  updatePositions: (positions: Position[]) => void;
  
  // Strategies
  strategies: Strategy[];
  addStrategy: (strategy: Strategy) => void;
  updateStrategy: (strategyId: string, updates: Partial<Strategy>) => void;
  removeStrategy: (strategyId: string) => void;
  
  // User Settings
  settings: {
    theme: 'light' | 'dark';
    orderConfirmation: boolean;
    notifications: boolean;
  };
  updateSettings: (updates: Partial<Store['settings']>) => void;
}

export const useStore = create<Store>()(
  devtools(
    persist(
      (set) => ({
        // Initial state
        marketData: {},
        orders: [],
        positions: [],
        strategies: [],
        settings: {
          theme: 'dark',
          orderConfirmation: true,
          notifications: true,
        },

        // Actions
        setMarketData: (symbol, data) =>
          set((state) => ({
            marketData: { ...state.marketData, [symbol]: data },
          })),

        addOrder: (order) =>
          set((state) => ({
            orders: [order, ...state.orders],
          })),

        updateOrder: (orderId, updates) =>
          set((state) => ({
            orders: state.orders.map((order) =>
              order.id === orderId ? { ...order, ...updates } : order
            ),
          })),

        updatePositions: (positions) =>
          set({ positions }),

        addStrategy: (strategy) =>
          set((state) => ({
            strategies: [...state.strategies, strategy],
          })),

        updateStrategy: (strategyId, updates) =>
          set((state) => ({
            strategies: state.strategies.map((strategy) =>
              strategy.id === strategyId
                ? { ...strategy, ...updates }
                : strategy
            ),
          })),

        removeStrategy: (strategyId) =>
          set((state) => ({
            strategies: state.strategies.filter(
              (strategy) => strategy.id !== strategyId
            ),
          })),

        updateSettings: (updates) =>
          set((state) => ({
            settings: { ...state.settings, ...updates },
          })),
      }),
      {
        name: 'crypto-trading-store',
      }
    )
  )
);