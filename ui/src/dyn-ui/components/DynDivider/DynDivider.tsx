import { forwardRef, useId } from 'react';
import type { ForwardedRef } from 'react';
import { cn } from '../../utils/classNames';
import {
  DYN_DIVIDER_DEFAULT_PROPS,
  DynDividerProps,
  DynDividerRef,
  DynDividerColor,
  LayoutSpacing,
} from './DynDivider.types';
import styles from './DynDivider.module.css';

const DynDividerComponent = (
  {
    label,
    labelPosition = DYN_DIVIDER_DEFAULT_PROPS.labelPosition,
    direction = DYN_DIVIDER_DEFAULT_PROPS.direction,
    thickness = DYN_DIVIDER_DEFAULT_PROPS.thickness,
    lineStyle = DYN_DIVIDER_DEFAULT_PROPS.lineStyle,
    color = DYN_DIVIDER_DEFAULT_PROPS.color,
    spacing = DYN_DIVIDER_DEFAULT_PROPS.spacing,
    children,
    className,
    id,
    'data-testid': dataTestId = DYN_DIVIDER_DEFAULT_PROPS['data-testid'],
    ...rest
  }: DynDividerProps,
  ref: ForwardedRef<DynDividerRef>
) => {
  const generatedId = useId();
  const orientation = direction === 'vertical' ? 'vertical' : 'horizontal';
  const labelContent = children ?? label;
  const labelId = labelContent ? `${id ?? `dyn-divider-${generatedId}`}-label` : undefined;
  const ariaLabel =
    !labelId && typeof labelContent === 'string' ? labelContent : undefined;

  // Explicit mapping objects for type safety
  const DIRECTION_MAP = {
    horizontal: styles.directionHorizontal,
    vertical: styles.directionVertical,
  };

  const THICKNESS_MAP = {
    thin: styles.thicknessThin,
    medium: styles.thicknessMedium,
    thick: styles.thicknessThick,
  };

  const LINE_STYLE_MAP = {
    solid: styles.lineStyleSolid,
    dashed: styles.lineStyleDashed,
    dotted: styles.lineStyleDotted,
  };

  const COLOR_MAP: Record<DynDividerColor, string | undefined> = {
    default: styles.colorDefault,
    primary: styles.colorPrimary,
    secondary: styles.colorSecondary,
    subtle: styles.colorMuted,
    success: styles.colorSuccess,
    warning: styles.colorWarning,
    danger: styles.colorDanger,
  };

  const SPACING_MAP: Record<LayoutSpacing, string> = {
    none: styles.spacingNone,
    xs: styles.spacingXs,
    sm: styles.spacingSm,
    md: styles.spacingMd,
    lg: styles.spacingLg,
    xl: styles.spacingXl,
  };

  const LABEL_POSITION_MAP = {
    left: styles.labelLeft,
    center: undefined, // default, no class needed
    right: styles.labelRight,
  };

  const dividerClassName = cn(
    styles.root,
    DIRECTION_MAP[orientation],
    THICKNESS_MAP[thickness],
    LINE_STYLE_MAP[lineStyle],
    COLOR_MAP[color ?? 'default'],
    SPACING_MAP[spacing],
    Boolean(labelContent) && styles.withLabel,
    Boolean(labelContent) && LABEL_POSITION_MAP[labelPosition],
    className
  );

  return (
    <div
      ref={ref}
      id={id}
      role="separator"
      aria-orientation={orientation}
      aria-labelledby={labelId}
      aria-label={ariaLabel}
      className={dividerClassName}
      data-testid={dataTestId}
      {...rest}
    >
      <span className={styles.line} aria-hidden="true" />
      {labelContent ? (
        <span className={styles.label} id={labelId}>
          {labelContent}
        </span>
      ) : null}
      <span className={styles.line} aria-hidden="true" />
    </div>
  );
};

const DynDivider = forwardRef<DynDividerRef, DynDividerProps>(DynDividerComponent);

DynDivider.displayName = 'DynDivider';

export { DynDivider };
export default DynDivider;
