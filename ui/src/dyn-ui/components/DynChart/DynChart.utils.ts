import type {
  ChartAxis,
  ChartDataPoint,
  ChartSeries,
  DynChartData,
  DynChartLegendItem,
  NormalizedChartSeries,
} from './DynChart.types';

export interface ChartDimensions {
  padding: { top: number; right: number; bottom: number; left: number };
  chartWidth: number;
  chartHeight: number;
  totalWidth: number;
  totalHeight: number;
}

export interface DataRanges {
  minX: number;
  maxX: number;
  minY: number;
  maxY: number;
}

const DEFAULT_PADDING = { top: 20, right: 20, bottom: 60, left: 60 } as const;

const FALLBACK_COLORS = ['#0066cc', '#00b248', '#f44336', '#ff9800', '#9c27b0'];

export const EMPTY_DATA_RANGES: DataRanges = {
  minX: 0,
  maxX: 0,
  minY: 0,
  maxY: 1,
};

export function isSeriesCollection(data?: DynChartData): data is ChartSeries[] {
  return Array.isArray(data) && data.length > 0 && typeof data[0] === 'object' && 'name' in (data[0] as ChartSeries);
}

export function normalizeSeries(
  data: DynChartData | undefined,
  palette: string[] = FALLBACK_COLORS
): NormalizedChartSeries[] {
  if (!data || data.length === 0) {
    return [];
  }

  if (isSeriesCollection(data)) {
    return data.map((series, index) => ({
      ...series,
      color: series.color ?? palette[index % palette.length] ?? FALLBACK_COLORS[index % FALLBACK_COLORS.length],
    } as NormalizedChartSeries));
  }

  const fallbackColor = palette[0] ?? FALLBACK_COLORS[0];

  return [
    {
      name: 'Series 1',
      data: data as ChartDataPoint[],
      color: fallbackColor!,
    },
  ];
}

export function calculateChartDimensions(width: number, height: number): ChartDimensions {
  const chartWidth = Math.max(0, width - (DEFAULT_PADDING.left + DEFAULT_PADDING.right));
  const chartHeight = Math.max(0, height - (DEFAULT_PADDING.top + DEFAULT_PADDING.bottom));

  return {
    padding: { ...DEFAULT_PADDING },
    chartWidth,
    chartHeight,
    totalWidth: width,
    totalHeight: height,
  };
}

export function calculateDataRanges(
  seriesCollection: NormalizedChartSeries[],
  axis?: ChartAxis
): DataRanges {
  if (seriesCollection.length === 0) {
    if (axis?.min !== undefined && axis?.max !== undefined) {
      return { minX: 0, maxX: 0, minY: axis.min, maxY: axis.max };
    }

    return EMPTY_DATA_RANGES;
  }

  let minY = axis?.min ?? Number.POSITIVE_INFINITY;
  let maxY = axis?.max ?? Number.NEGATIVE_INFINITY;
  let maxX = 0;

  seriesCollection.forEach(series => {
    series.data.forEach((point, index) => {
      maxX = Math.max(maxX, index);

      if (axis?.min === undefined) {
        minY = Math.min(minY, point.value);
      }

      if (axis?.max === undefined) {
        maxY = Math.max(maxY, point.value);
      }
    });
  });

  if (!Number.isFinite(minY) || !Number.isFinite(maxY)) {
    return { ...EMPTY_DATA_RANGES, maxX };
  }

  if (axis?.min === undefined) {
    minY = Math.min(minY, 0);
  }

  if (axis?.max === undefined) {
    maxY = maxY === minY ? minY + 1 : maxY;
  }

  return {
    minX: 0,
    maxX,
    minY,
    maxY,
  };
}

export function buildLegendItems(seriesCollection: NormalizedChartSeries[]): DynChartLegendItem[] {
  return seriesCollection.map((series, index) => ({
    id: `${series.name}-${index}`,
    label: series.name,
    color: series.color,
    seriesIndex: index,
  }));
}

export function getEmptyStateMessage(seriesCollection: NormalizedChartSeries[]): string {
  if (seriesCollection.length === 0) {
    return 'No chart data available';
  }

  const totalValues = seriesCollection.reduce((total, series) => {
    return total + series.data.reduce((sum, point) => sum + Math.abs(point.value), 0);
  }, 0);

  return totalValues === 0 ? 'Chart data contains no measurable values' : '';
}
