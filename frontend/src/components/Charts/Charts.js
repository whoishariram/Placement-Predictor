import React, { useContext } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Bar, Doughnut, Line } from 'react-chartjs-2';
import { ThemeContext } from '../../App';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

// ============================================
// THEME COLORS
// ============================================

const getThemeColors = (darkMode) => ({
  grid: darkMode ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.06)',
  text: darkMode ? '#9ca3af' : '#6b7280',
  tooltipBg: darkMode ? '#1f2937' : '#ffffff',
  tooltipBorder: darkMode ? '#374151' : '#e5e7eb',
  tooltipText: darkMode ? '#f3f4f6' : '#111827',
});

const chartColors = {
  blue: '#3b82f6',
  green: '#22c55e',
  purple: '#9333ea',
  orange: '#f97316',
  red: '#ef4444',
  teal: '#14b8a6',
  pink: '#ec4899',
  yellow: '#eab308',
  indigo: '#6366f1',
  cyan: '#06b6d4',
};

const chartColorArray = [
  chartColors.blue, chartColors.green, chartColors.purple,
  chartColors.orange, chartColors.teal, chartColors.pink,
  chartColors.yellow, chartColors.indigo, chartColors.cyan, chartColors.red,
];

// ============================================
// DEFAULT OPTIONS
// ============================================

const getDefaultOptions = (darkMode, custom = {}) => {
  const colors = getThemeColors(darkMode);

  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          color: colors.text,
          font: { family: 'Inter, sans-serif', size: 12 },
          padding: 16,
          usePointStyle: true,
          pointStyle: 'circle',
        },
      },
      tooltip: {
        backgroundColor: colors.tooltipBg,
        titleColor: colors.tooltipText,
        bodyColor: colors.tooltipText,
        borderColor: colors.tooltipBorder,
        borderWidth: 1,
        cornerRadius: 8,
        padding: 12,
        titleFont: { family: 'Inter, sans-serif', size: 13, weight: '600' },
        bodyFont: { family: 'Inter, sans-serif', size: 12 },
      },
    },
    scales: {
      x: {
        grid: { color: colors.grid, drawBorder: false },
        ticks: { color: colors.text, font: { family: 'Inter, sans-serif', size: 11 } },
      },
      y: {
        grid: { color: colors.grid, drawBorder: false },
        ticks: { color: colors.text, font: { family: 'Inter, sans-serif', size: 11 } },
        beginAtZero: true,
      },
    },
    ...custom,
  };
};

// ============================================
// VERTICAL BAR CHART
// ============================================

export const BarChart = ({ labels, datasets, height = 300, title, options }) => {
  const { darkMode } = useContext(ThemeContext);

  const data = {
    labels,
    datasets: datasets.map((ds, i) => ({
      label: ds.label || '',
      data: ds.data,
      backgroundColor: Array.isArray(ds.backgroundColor)
        ? ds.backgroundColor
        : (ds.backgroundColor || chartColorArray[i % chartColorArray.length]),
      borderColor: ds.borderColor || chartColorArray[i % chartColorArray.length],
      borderWidth: ds.borderWidth || 0,
      borderRadius: ds.borderRadius || 6,
      barPercentage: ds.barPercentage || 0.7,
      categoryPercentage: ds.categoryPercentage || 0.8,
      ...ds,
    })),
  };

  const base = getDefaultOptions(darkMode);
  const defaultOpts = {
    ...base,
    plugins: {
      ...base.plugins,
      legend: { ...base.plugins.legend, display: datasets.length > 1 },
    },
    ...options,
  };

  if (title) {
    defaultOpts.plugins.title = {
      display: true,
      text: title,
      color: darkMode ? '#f3f4f6' : '#111827',
      font: { family: 'Inter, sans-serif', size: 14, weight: '600' },
      padding: { bottom: 16 },
    };
  }

  return (
    <div style={{ height }}>
      <Bar data={data} options={defaultOpts} />
    </div>
  );
};

// ============================================
// HORIZONTAL BAR CHART
// ============================================

export const HorizontalBarChart = ({ labels, datasets, height = 300, title }) => {
  const { darkMode } = useContext(ThemeContext);

  const data = {
    labels,
    datasets: datasets.map((ds, i) => ({
      label: ds.label || '',
      data: ds.data,
      backgroundColor: ds.backgroundColor || chartColorArray[i % chartColorArray.length],
      borderColor: ds.borderColor || chartColorArray[i % chartColorArray.length],
      borderWidth: 0,
      borderRadius: 6,
      barPercentage: 0.6,
    })),
  };

  const base = getDefaultOptions(darkMode);
  const options = {
    ...base,
    indexAxis: 'y',
    plugins: {
      ...base.plugins,
      legend: { display: false },
      title: title ? {
        display: true, text: title,
        color: darkMode ? '#f3f4f6' : '#111827',
        font: { family: 'Inter, sans-serif', size: 14, weight: '600' },
        padding: { bottom: 16 },
      } : undefined,
    },
  };

  return (
    <div style={{ height }}>
      <Bar data={data} options={options} />
    </div>
  );
};

// ============================================
// STACKED BAR CHART
// ============================================

export const StackedBarChart = ({ labels, datasets, height = 300, title }) => {
  const { darkMode } = useContext(ThemeContext);

  const data = {
    labels,
    datasets: datasets.map((ds, i) => ({
      label: ds.label || '',
      data: ds.data,
      backgroundColor: ds.backgroundColor || chartColorArray[i % chartColorArray.length],
      borderWidth: 0,
      borderRadius: 2,
    })),
  };

  const base = getDefaultOptions(darkMode);
  const options = {
    ...base,
    scales: {
      x: { stacked: true, grid: base.scales.x.grid, ticks: base.scales.x.ticks },
      y: { stacked: true, grid: base.scales.y.grid, ticks: base.scales.y.ticks, beginAtZero: true },
    },
    plugins: {
      ...base.plugins,
      title: title ? {
        display: true, text: title,
        color: darkMode ? '#f3f4f6' : '#111827',
        font: { family: 'Inter, sans-serif', size: 14, weight: '600' },
        padding: { bottom: 16 },
      } : undefined,
    },
  };

  return (
    <div style={{ height }}>
      <Bar data={data} options={options} />
    </div>
  );
};

// ============================================
// DOUGHNUT CHART
// ============================================

export const DoughnutChart = ({ labels, data: dataValues, colors, height = 300, title, cutout = '70%' }) => {
  const { darkMode } = useContext(ThemeContext);

  const bgColors = colors || dataValues.map((_, i) => chartColorArray[i % chartColorArray.length]);

  const data = {
    labels,
    datasets: [{
      data: dataValues,
      backgroundColor: bgColors,
      borderColor: darkMode ? '#1f2937' : '#ffffff',
      borderWidth: 3,
      hoverOffset: 8,
    }],
  };

  const base = getDefaultOptions(darkMode);
  const options = {
    ...base,
    cutout,
    plugins: {
      ...base.plugins,
      legend: {
        position: 'bottom',
        labels: {
          color: darkMode ? '#9ca3af' : '#6b7280',
          font: { family: 'Inter, sans-serif', size: 11 },
          padding: 12, usePointStyle: true, pointStyle: 'circle',
        },
      },
      title: title ? {
        display: true, text: title,
        color: darkMode ? '#f3f4f6' : '#111827',
        font: { family: 'Inter, sans-serif', size: 14, weight: '600' },
        padding: { bottom: 16 },
      } : undefined,
    },
  };

  return (
    <div style={{ height }}>
      <Doughnut data={data} options={options} />
    </div>
  );
};

// ============================================
// PIE CHART
// ============================================

export const PieChart = ({ labels, data: dataValues, colors, height = 300, title }) => {
  return (
    <DoughnutChart
      labels={labels}
      data={dataValues}
      colors={colors}
      height={height}
      title={title}
      cutout="30%"
    />
  );
};

// ============================================
// LINE CHART
// ============================================

export const LineChart = ({ labels, datasets, height = 300, title, fill = false, smooth = true }) => {
  const { darkMode } = useContext(ThemeContext);

  const data = {
    labels,
    datasets: datasets.map((ds, i) => ({
      label: ds.label || '',
      data: ds.data,
      borderColor: ds.borderColor || chartColorArray[i % chartColorArray.length],
      backgroundColor: ds.backgroundColor || (fill ? chartColorArray[i % chartColorArray.length].replace('1)', '0.1)') : 'transparent'),
      pointBackgroundColor: ds.pointColor || chartColorArray[i % chartColorArray.length],
      pointBorderColor: darkMode ? '#1f2937' : '#ffffff',
      pointBorderWidth: 2,
      pointRadius: ds.pointRadius ?? 4,
      pointHoverRadius: 6,
      borderWidth: ds.borderWidth || 2.5,
      fill: fill,
      tension: smooth ? 0.4 : 0,
      spanGaps: true,
      ...ds,
    })),
  };

  const base = getDefaultOptions(darkMode);
  const options = {
    ...base,
    elements: { line: { tension: smooth ? 0.4 : 0 } },
    plugins: {
      ...base.plugins,
      legend: { ...base.plugins.legend, display: datasets.length > 1 },
      filler: { propagate: true },
      title: title ? {
        display: true, text: title,
        color: darkMode ? '#f3f4f6' : '#111827',
        font: { family: 'Inter, sans-serif', size: 14, weight: '600' },
        padding: { bottom: 16 },
      } : undefined,
    },
  };

  return (
    <div style={{ height }}>
      <Line data={data} options={options} />
    </div>
  );
};

// ============================================
// MIXED CHART (Bar + Line)
// ============================================

export const MixedChart = ({ labels, barDatasets, lineDatasets, height = 300, title }) => {
  const { darkMode } = useContext(ThemeContext);

  const data = {
    labels,
    datasets: [
      ...barDatasets.map((ds, i) => ({
        type: 'bar',
        label: ds.label || '',
        data: ds.data,
        backgroundColor: ds.backgroundColor || chartColorArray[i % chartColorArray.length],
        borderColor: ds.borderColor || chartColorArray[i % chartColorArray.length],
        borderWidth: 0,
        borderRadius: 6,
        barPercentage: 0.6,
        order: 2,
        yAxisID: ds.yAxisID || 'y',
      })),
      ...lineDatasets.map((ds, i) => ({
        type: 'line',
        label: ds.label || '',
        data: ds.data,
        borderColor: ds.borderColor || chartColors.red,
        backgroundColor: 'transparent',
        pointBackgroundColor: ds.borderColor || chartColors.red,
        pointBorderColor: darkMode ? '#1f2937' : '#ffffff',
        pointBorderWidth: 2,
        pointRadius: 4,
        borderWidth: 2.5,
        tension: 0.4,
        order: 1,
        yAxisID: ds.yAxisID || 'y1',
        fill: false,
      })),
    ],
  };

  const base = getDefaultOptions(darkMode);
  const options = {
    ...base,
    plugins: {
      ...base.plugins,
      title: title ? {
        display: true, text: title,
        color: darkMode ? '#f3f4f6' : '#111827',
        font: { family: 'Inter, sans-serif', size: 14, weight: '600' },
        padding: { bottom: 16 },
      } : undefined,
    },
    scales: {
      x: { grid: base.scales.x.grid, ticks: base.scales.x.ticks },
      y: { position: 'left', grid: base.scales.y.grid, ticks: base.scales.y.ticks, beginAtZero: true },
      y1: { position: 'right', grid: { display: false }, ticks: base.scales.y.ticks, beginAtZero: true },
    },
  };

  return (
    <div style={{ height }}>
      <Bar data={data} options={options} />
    </div>
  );
};

export default { BarChart, HorizontalBarChart, StackedBarChart, DoughnutChart, PieChart, LineChart, MixedChart };
