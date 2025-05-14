import React, { useEffect, useRef } from 'react';
import { createChart, IChartApi, ColorType } from 'lightweight-charts';
import { useTheme } from '../hooks/useTheme';

interface TradingChartProps {
  symbol: string;
  interval: string;
  data: {
    time: string;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
  }[];
}

export const TradingChart: React.FC<TradingChartProps> = ({
  symbol,
  interval,
  data
}) => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const { isDarkMode } = useTheme();
  const chart = useRef<IChartApi | null>(null);

  useEffect(() => {
    if (chartContainerRef.current) {
      chart.current = createChart(chartContainerRef.current, {
        layout: {
          background: { color: isDarkMode ? '#1A1A1A' : '#FFFFFF' },
          textColor: isDarkMode ? '#D9D9D9' : '#191919',
        },
        grid: {
          vertLines: { color: isDarkMode ? '#333333' : '#E6E6E6' },
          horzLines: { color: isDarkMode ? '#333333' : '#E6E6E6' },
        },
        width: chartContainerRef.current.clientWidth,
        height: 500,
      });

      const candlestickSeries = chart.current.addCandlestickSeries({
        upColor: '#26a69a',
        downColor: '#ef5350',
        borderVisible: false,
        wickUpColor: '#26a69a',
        wickDownColor: '#ef5350',
      });

      const volumeSeries = chart.current.addHistogramSeries({
        color: '#385263',
        priceFormat: { type: 'volume' },
        priceScaleId: '',
        scaleMargins: { top: 0.8, bottom: 0 },
      });

      candlestickSeries.setData(data);
      volumeSeries.setData(data.map(item => ({
        time: item.time,
        value: item.volume,
        color: item.close > item.open ? '#26a69a' : '#ef5350',
      })));

      chart.current.timeScale().fitContent();
    }

    return () => {
      if (chart.current) {
        chart.current.remove();
      }
    };
  }, [data, isDarkMode]);

  return <div ref={chartContainerRef} />;
};