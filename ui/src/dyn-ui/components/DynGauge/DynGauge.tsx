import {
  forwardRef,
  useCallback,
  useEffect,
  useId,
  useMemo,
  useRef,
} from 'react';

import { cn } from '../../utils/classNames';
import {
  DYN_GAUGE_DEFAULT_PROPS,
  DynGaugeProps,
  GaugeRange,
  GaugeSize,
  GaugeType,
} from './DynGauge.types';
import styles from './DynGauge.module.css';

const gaugeDimensionsMap: Record<GaugeSize, { width: number; height: number }> = {
  sm: { width: 120, height: 120 },
  md: { width: 200, height: 200 },
  lg: { width: 280, height: 280 },
};

const sizeClassNameMap: Partial<Record<GaugeSize, string | undefined>> = {
  sm: styles['sizeSm'],
  md: styles['sizeMd'],
  lg: styles['sizeLg'],
};

const typeClassNameMap: Partial<Record<GaugeType, string | undefined>> = {
  arc: styles.typeArc,
  circle: styles.typeCircle,
  line: styles.typeLine,
};

const clampGaugeValue = (value: number, min: number, max: number): number => {
  if (!Number.isFinite(value)) {
    return min;
  }

  if (max <= min) {
    return min;
  }

  return Math.min(max, Math.max(min, value));
};

const findRangeForValue = (ranges: GaugeRange[], value: number) =>
  ranges.find(range => value >= range.from && value <= range.to);

export const DynGauge = forwardRef<HTMLDivElement, DynGaugeProps>((props, ref) => {
  const {
    value,
    min = DYN_GAUGE_DEFAULT_PROPS.min,
    max = DYN_GAUGE_DEFAULT_PROPS.max,
    title,
    label,
    subtitle,
    type = DYN_GAUGE_DEFAULT_PROPS.type,
    unit = DYN_GAUGE_DEFAULT_PROPS.unit,
    ranges = DYN_GAUGE_DEFAULT_PROPS.ranges,
    showValue = DYN_GAUGE_DEFAULT_PROPS.showValue,
    showRanges = DYN_GAUGE_DEFAULT_PROPS.showRanges,
    size = DYN_GAUGE_DEFAULT_PROPS.size,
    thickness = DYN_GAUGE_DEFAULT_PROPS.thickness,
    rounded = DYN_GAUGE_DEFAULT_PROPS.rounded,
    animated = DYN_GAUGE_DEFAULT_PROPS.animated,
    color,
    backgroundColor = DYN_GAUGE_DEFAULT_PROPS.backgroundColor,
    className,
    format,
    id,
    'data-testid': dataTestId,
    ...rest
  } = props;

  const instanceId = useId();
  const componentId = id ?? instanceId;
  const titleId = title || label ? `${componentId}-title` : undefined;
  const subtitleId = subtitle ? `${componentId}-subtitle` : undefined;

  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationFrameRef = useRef<number | undefined>(undefined);
  const currentValueRef = useRef<number>(clampGaugeValue(value, min, max));

  const gaugeDimensions = gaugeDimensionsMap[size] ?? gaugeDimensionsMap.md;
  const resolvedTitle = title ?? label;
  const safeValue = clampGaugeValue(value, min, max);

  const numberFormatter = useMemo(
    () =>
      new Intl.NumberFormat(undefined, {
        maximumFractionDigits: 1,
      }),
    []
  );

  const formatValue = useCallback(
    (val: number): string => {
      if (typeof format === 'function') {
        return format(val);
      }

      const formattedNumber = numberFormatter.format(val);

      if (!unit) {
        return formattedNumber;
      }

      const trimmedUnit = unit.trim();
      const shouldJoin = trimmedUnit.startsWith('%') || trimmedUnit.startsWith('°');

      return shouldJoin
        ? `${formattedNumber}${trimmedUnit}`
        : `${formattedNumber} ${trimmedUnit}`;
    },
    [format, numberFormatter, unit]
  );

  const getColorForValue = useCallback(
    (val: number) => {
      if (typeof color === 'string' && color.length > 0) {
        return color;
      }

      return findRangeForValue(ranges, val)?.color ?? '#0066cc';
    },
    [color, ranges]
  );

  // Read theme colors from CSS variables
  const getThemeColors = useCallback(() => {
    const defaultColors = {
      track: '#e0e0e0',
      ticks: '#666',
      text: '#666',
      needle: '#0f172a',
      needleCenter: '#ffffff',
      fontSizeSm: '10px',
      fontSizeMd: '12px',
      fontSizeLg: '14px',
      duration: 800,
    };

    if (typeof window === 'undefined' || !canvasRef.current) return defaultColors;

    const style = getComputedStyle(canvasRef.current);
    return {
      track: style.getPropertyValue('--dyn-gauge-track') || defaultColors.track,
      ticks: style.getPropertyValue('--dyn-gauge-ticks') || defaultColors.ticks,
      text: style.getPropertyValue('--dyn-gauge-text-secondary') || defaultColors.text,
      needle: style.getPropertyValue('--dyn-gauge-needle-color') || defaultColors.needle,
      needleCenter: style.getPropertyValue('--dyn-gauge-needle-center') || defaultColors.needleCenter,
      fontSizeSm: style.getPropertyValue('--dyn-gauge-font-size-sm') || defaultColors.fontSizeSm,
      fontSizeMd: style.getPropertyValue('--dyn-gauge-font-size-md') || defaultColors.fontSizeMd,
      fontSizeLg: style.getPropertyValue('--dyn-gauge-font-size-lg') || defaultColors.fontSizeLg,
      duration: parseFloat(style.getPropertyValue('--dyn-gauge-animation-duration')) || defaultColors.duration,
    };
  }, []);

  const drawGauge = useCallback(
    (displayValue: number) => {
      const canvas = canvasRef.current;
      if (!canvas) {
        return;
      }

      const context = canvas.getContext('2d');
      if (!context) {
        return;
      }

      const { width, height } = gaugeDimensions;
      const centerX = width / 2;
      const centerY = height / 2;
      const radius = Math.min(width, height) / 2 - thickness / 2 - 10;
      const startAngle = -Math.PI * 0.75;
      const sweepAngle = Math.PI * 1.5;
      const span = Math.max(max - min, Number.EPSILON);
      const normalizedValue = (clampGaugeValue(displayValue, min, max) - min) / span;
      const currentColor = getColorForValue(displayValue) || '#0066cc';

      const colors = getThemeColors();
      const resolvedBackgroundColor = backgroundColor || colors.track || '#e0e0e0';

      canvas.width = width;
      canvas.height = height;

      context.clearRect(0, 0, width, height);

      context.beginPath();
      context.arc(centerX, centerY, radius, startAngle, startAngle + sweepAngle);
      context.strokeStyle = resolvedBackgroundColor;
      context.lineWidth = thickness;
      context.lineCap = rounded ? 'round' : 'butt';
      context.stroke();

      if (showRanges && ranges.length > 0) {
        for (const range of ranges) {
          const rangeStart = startAngle + ((range.from - min) / span) * sweepAngle;
          const rangeEnd = startAngle + ((range.to - min) / span) * sweepAngle;

          context.beginPath();
          context.arc(centerX, centerY, radius, rangeStart, rangeEnd);
          context.strokeStyle = range.color;
          context.lineWidth = thickness * 0.3;
          context.lineCap = rounded ? 'round' : 'butt';
          context.stroke();
        }
      }

      if (normalizedValue > 0) {
        const endAngle = startAngle + normalizedValue * sweepAngle;

        context.beginPath();
        context.arc(centerX, centerY, radius, startAngle, endAngle);
        context.strokeStyle = currentColor || '#0066cc';
        context.lineWidth = thickness;
        context.lineCap = rounded ? 'round' : 'butt';
        context.stroke();
      }

      const tickCount = 11;
      for (let index = 0; index < tickCount; index += 1) {
        const angle = startAngle + (index / (tickCount - 1)) * sweepAngle;
        const isMajorTick = index % 2 === 0;
        const tickLength = isMajorTick ? 15 : 8;
        const tickWidth = isMajorTick ? 2 : 1;

        const outerRadius = radius + thickness / 2 + 5;
        const innerRadius = outerRadius + tickLength;

        const startX = centerX + Math.cos(angle) * outerRadius;
        const startY = centerY + Math.sin(angle) * outerRadius;
        const endX = centerX + Math.cos(angle) * innerRadius;
        const endY = centerY + Math.sin(angle) * innerRadius;

        context.beginPath();
        context.moveTo(startX, startY);
        context.lineTo(endX, endY);
        context.strokeStyle = colors.ticks || '#666';
        context.lineWidth = tickWidth;
        context.lineCap = 'round';
        context.stroke();

        if (isMajorTick) {
          const labelRadius = innerRadius + 15;
          const labelX = centerX + Math.cos(angle) * labelRadius;
          const labelY = centerY + Math.sin(angle) * labelRadius;
          const tickValue = min + (index / (tickCount - 1)) * span;

          context.fillStyle = colors.text || '#666';
          const fontSize =
            (size === 'sm'
              ? colors.fontSizeSm
              : size === 'lg'
                ? colors.fontSizeLg
                : colors.fontSizeMd) || '12px';

          context.font = `${fontSize} Arial`;
          context.textAlign = 'center';
          context.textBaseline = 'middle';
          context.fillText(numberFormatter.format(tickValue), labelX, labelY);
        }
      }

      const needleAngle = startAngle + normalizedValue * sweepAngle;
      const needleLength = radius - 20;
      const needleX = centerX + Math.cos(needleAngle) * needleLength;
      const needleY = centerY + Math.sin(needleAngle) * needleLength;

      context.beginPath();
      context.arc(centerX, centerY, 8, 0, Math.PI * 2);
      context.fillStyle = currentColor || '#0066cc';
      context.fill();

      context.beginPath();
      context.moveTo(centerX, centerY);
      context.lineTo(needleX, needleY);
      context.strokeStyle = currentColor || '#0066cc';
      context.lineWidth = 3;
      context.lineCap = 'round';
      context.stroke();

      context.beginPath();
      context.arc(centerX, centerY, 4, 0, Math.PI * 2);
      context.fillStyle = colors.needleCenter || '#ffffff';
      context.shadowBlur = 2;
      context.shadowColor = 'rgba(0,0,0,0.5)';
      context.fill();
      context.shadowBlur = 0;
      context.strokeStyle = currentColor || '#0066cc';
      context.lineWidth = 2;
      context.stroke();
    },
    [
      backgroundColor,
      gaugeDimensions,
      getColorForValue,
      max,
      min,
      numberFormatter,
      ranges,
      rounded,
      showRanges,
      size,
      thickness,
    ]
  );

  const animateToValue = useCallback(
    (target: number) => {
      const clampedTarget = clampGaugeValue(target, min, max);

      if (!animated) {
        currentValueRef.current = clampedTarget;
        drawGauge(clampedTarget);
        return;
      }

      const startValue = currentValueRef.current;
      const distance = clampedTarget - startValue;

      if (Math.abs(distance) <= 0.001) {
        currentValueRef.current = clampedTarget;
        drawGauge(clampedTarget);
        return;
      }

      let startTime: number | null = null;
      const themeConfig = getThemeColors();
      const duration = themeConfig.duration ?? 800; // Provide fallback if undefined

      const step = (timestamp: number) => {
        if (startTime === null) {
          startTime = timestamp;
        }

        const elapsed = timestamp - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const easedProgress = 1 - Math.pow(1 - progress, 3);
        const nextValue = startValue + distance * easedProgress;

        currentValueRef.current = nextValue;
        drawGauge(nextValue);

        if (progress < 1) {
          animationFrameRef.current = requestAnimationFrame(step);
        } else {
          currentValueRef.current = clampedTarget;
          drawGauge(clampedTarget);
        }
      };

      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }

      animationFrameRef.current = requestAnimationFrame(step);
    },
    [animated, drawGauge, max, min]
  );

  useEffect(() => {
    animateToValue(value);

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [animateToValue, value]);

  useEffect(() => {
    drawGauge(currentValueRef.current);
  }, [drawGauge]);

  const currentRange = useMemo(
    () => findRangeForValue(ranges, safeValue),
    [ranges, safeValue]
  );

  const rootClassName = cn(
    styles.root,
    sizeClassNameMap[size] ?? styles.sizeMd,
    typeClassNameMap[type],
    animated && styles.animated,
    rounded && styles.rounded,
    className
  );

  return (
    <div
      ref={ref}
      id={componentId}
      role="progressbar"
      aria-valuemin={min}
      aria-valuemax={max}
      aria-valuenow={safeValue}
      aria-labelledby={titleId}
      aria-describedby={subtitleId}
      data-testid={dataTestId ?? 'dyn-gauge'}
      data-size={size}
      data-type={type}
      className={rootClassName}
      {...rest}
    >
      <figure className={styles.figure}>
        {(resolvedTitle || subtitle) && (
          <header className={styles.header}>
            {resolvedTitle ? (
              <h3 id={titleId} className={styles.title}>
                {resolvedTitle}
              </h3>
            ) : null}
            {subtitle ? (
              <p id={subtitleId} className={styles.subtitle}>
                {subtitle}
              </p>
            ) : null}
          </header>
        )}

        <div className={styles.content}>
          <div className={styles.canvasContainer}>
            <canvas
              ref={canvasRef}
              className={styles.canvas}
              style={{
                width: gaugeDimensions.width,
                height: gaugeDimensions.height,
              }}
            />

            {showValue ? (
              <div className={styles.value}>
                <span className={styles.valueText}>{formatValue(safeValue)}</span>
                {currentRange?.label ? (
                  <span className={styles.valueLabel}>{currentRange.label}</span>
                ) : null}
              </div>
            ) : null}
          </div>
        </div>

        {showRanges && ranges.length > 0 ? (
          <figcaption className={styles.legend}>
            {ranges.map((range, index) => (
              <div
                key={`${range.from}-${range.to}-${index}`}
                className={styles.legendItem}
              >
                <span
                  className={styles.legendColor}
                  style={{ backgroundColor: range.color }}
                  aria-hidden="true"
                />
                <span className={styles.legendLabel}>
                  {range.label ?? `${formatValue(range.from)} - ${formatValue(range.to)}`}
                </span>
              </div>
            ))}
          </figcaption>
        ) : null}
      </figure>
    </div>
  );
});

DynGauge.displayName = 'DynGauge';

export default DynGauge;
