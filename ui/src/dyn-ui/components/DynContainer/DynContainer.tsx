import { forwardRef, useMemo } from 'react';
import type { CSSProperties, ForwardedRef } from 'react';
import { cn } from '../../utils/classNames';
import {
  DYN_CONTAINER_DEFAULT_PROPS,
  DynContainerProps,
  DynContainerRef,
} from './DynContainer.types';
import styles from './DynContainer.module.css';

const toPascalCase = (value: string) => {
  if (value.match(/^\d/)) return value; // 2xs -> 2xs (lowercase start for numbers)
  return value.charAt(0).toUpperCase() + value.slice(1);
};

const SPACING_TOKENS: Record<string, string> = {
  none: '0',
  '2xs': 'var(--dyn-spacing-2xs)',
  xs: 'var(--dyn-spacing-xs)',
  sm: 'var(--dyn-spacing-sm)',
  md: 'var(--dyn-spacing-md)',
  lg: 'var(--dyn-spacing-lg)',
  xl: 'var(--dyn-spacing-xl)',
  '2xl': 'var(--dyn-spacing-2xl)',
  '3xl': 'var(--dyn-spacing-3xl)',
  '4xl': 'var(--dyn-spacing-4xl)',
};

const MAX_WIDTH_TOKENS: Record<string, string> = {
  xs: 'var(--dyn-container-max-width-xs)',
  sm: 'var(--dyn-container-max-width-sm)',
  md: 'var(--dyn-container-max-width-md)',
  lg: 'var(--dyn-container-max-width-lg)',
  xl: 'var(--dyn-container-max-width-xl)',
  full: '100%',
};

const SHADOW_TOKENS = ['none', 'low', 'medium', 'high', 'default'];
const BG_TOKENS = ['none', 'surface', 'card'];


type CSSVarProperties = CSSProperties & Record<string, string | number | undefined>;

const resolveTokenValue = (value: string | number | undefined, tokenMap: Record<string, string>): string | undefined => {
  if (value === undefined) return undefined;
  if (typeof value === 'number') return value === 0 ? '0' : `${value}px`;
  const valStr = String(value).trim();
  if (valStr in tokenMap) return tokenMap[valStr];
  // If value is a numeric string (e.g. "500"), append px
  if (/^\d+$/.test(valStr)) return `${valStr}px`;
  return valStr;
};

const DynContainerComponent = (
  {
    as: Component = 'div',
    title,
    subtitle,
    direction,
    align,
    justify,
    spacing,
    size,
    bordered,
    shadow,
    background,
    height,
    maxWidth,
    layout,
    padding,
    margin,
    noBorder,
    noPadding,
    className,
    children,
    style,
    'data-testid': dataTestId = 'dyn-container',
    ...rest
  }: DynContainerProps,
  ref: ForwardedRef<DynContainerRef>
) => {
  const effectiveDirection = direction ?? DYN_CONTAINER_DEFAULT_PROPS.direction;
  const effectiveSpacing = spacing ?? DYN_CONTAINER_DEFAULT_PROPS.spacing;
  const effectiveSize = size ?? DYN_CONTAINER_DEFAULT_PROPS.size;
  const effectiveBackground = background ?? DYN_CONTAINER_DEFAULT_PROPS.background;
  const effectiveBordered = bordered ?? DYN_CONTAINER_DEFAULT_PROPS.bordered;
  const effectiveShadow = shadow ?? DYN_CONTAINER_DEFAULT_PROPS.shadow;
  const effectiveLayout = layout ?? DYN_CONTAINER_DEFAULT_PROPS.layout;

  const resolvedBordered = noBorder ? false : effectiveBordered;
  const hasTitleContent = Boolean(title || subtitle);

  const containerStyle = useMemo<CSSProperties | undefined>(() => {
    const next: CSSVarProperties = { ...(style as CSSVarProperties) };

    if (height !== undefined) {
      next.height = typeof height === 'number' ? `${height}px` : height;
    }

    const resolvedMaxWidth = resolveTokenValue(maxWidth, MAX_WIDTH_TOKENS);
    if (resolvedMaxWidth !== undefined) {
      next.maxWidth = resolvedMaxWidth.startsWith('var') ? `min(100%, ${resolvedMaxWidth})` : resolvedMaxWidth;
      next['--dyn-container-max-width'] = next.maxWidth as string;
    }

    const resolvedPadding = noPadding ? '0' : resolveTokenValue(padding, SPACING_TOKENS);
    if (resolvedPadding !== undefined) {
      next['--dyn-container-padding'] = resolvedPadding;
    }

    const resolvedMargin = resolveTokenValue(margin, SPACING_TOKENS);
    if (resolvedMargin !== undefined) {
      next['--dyn-container-margin'] = resolvedMargin;
    }

    const resolvedGap = resolveTokenValue(spacing, SPACING_TOKENS);
    if (resolvedGap !== undefined) {
      next['--dyn-container-gap'] = resolvedGap;
    }

    return Object.keys(next).length > 0 ? next : undefined;
  }, [height, maxWidth, padding, margin, spacing, style, noPadding]);

  // Dynamic Class Mappings 
  const directionClass = styles[`direction${toPascalCase(effectiveDirection)}` as keyof typeof styles];

  const sizeClass = effectiveSize ? styles[`size${toPascalCase(effectiveSize)}` as keyof typeof styles] : undefined;

  const backgroundClass = effectiveBackground && BG_TOKENS.includes(effectiveBackground)
    ? styles[`background${toPascalCase(effectiveBackground)}` as keyof typeof styles]
    : undefined;

  const alignClass = align ? styles[`align${toPascalCase(align)}` as keyof typeof styles] : undefined;
  const justifyClass = justify ? styles[`justify${toPascalCase(justify)}` as keyof typeof styles] : undefined;

  const spacingClass = effectiveSpacing && typeof effectiveSpacing === 'string' && SPACING_TOKENS[effectiveSpacing]
    ? styles[`spacing${toPascalCase(effectiveSpacing)}` as keyof typeof styles]
    : undefined;

  const containerClassName = cn(
    styles.root,
    directionClass,
    spacingClass,
    sizeClass,
    backgroundClass,
    alignClass,
    justifyClass,
    effectiveLayout === 'fixed' && styles.layoutFixed,
    resolvedBordered && styles.bordered,
    effectiveShadow && (SHADOW_TOKENS.includes(String(effectiveShadow)) ? styles[`shadow${toPascalCase(String(effectiveShadow))}` as keyof typeof styles] : styles.shadow),
    noPadding && styles.noPadding,
    hasTitleContent && styles.withTitle,
    className
  );

  return (
    <Component
      ref={ref}
      className={containerClassName}
      style={containerStyle}
      data-testid={dataTestId}
      {...rest}
    >
      {hasTitleContent && (
        <div className={styles.header}>
          {title && <h2 className={styles.title}>{title}</h2>}
          {subtitle && <p className={styles.subtitle}>{subtitle}</p>}
        </div>
      )}
      <div className={styles.content}>{children}</div>
    </Component>
  );
};

const DynContainer = forwardRef<DynContainerRef, DynContainerProps>(DynContainerComponent);

DynContainer.displayName = 'DynContainer';

export { DynContainer };
export default DynContainer;

