import React from 'react';
import { render, screen } from '@testing-library/react';
import { OrderBook } from '../OrderBook';

describe('OrderBook Component', () => {
    const mockData = {
        symbol: 'BTC/USDT',
        bids: [[40000, 1.5], [39900, 2.0]],
        asks: [[40100, 1.0], [40200, 2.5]]
    };

    it('renders orderbook correctly', () => {
        render(<OrderBook {...mockData} />);
        expect(screen.getByText('40,000.00')).toBeInTheDocument();
        expect(screen.getByText('1.50')).toBeInTheDocument();
    });

    it('shows spread', () => {
        render(<OrderBook {...mockData} />);
        const spread = screen.getByTestId('spread');
        expect(spread).toHaveTextContent('100.00 (0.25%)');
    });

    it('updates on new data', () => {
        const { rerender } = render(<OrderBook {...mockData} />);
        const newData = {
            ...mockData,
            bids: [[39000, 1.5]],
            asks: [[39100, 1.0]]
        };
        rerender(<OrderBook {...newData} />);
        expect(screen.getByText('39,000.00')).toBeInTheDocument();
    });
});