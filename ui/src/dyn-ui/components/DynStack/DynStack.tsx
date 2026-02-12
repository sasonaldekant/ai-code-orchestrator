import React, { forwardRef } from 'react';
import { cn } from '../../utils/classNames';
import type { DynStackProps } from './DynStack.types';
import { DYN_STACK_DEFAULT_PROPS } from './DynStack.types';
import styles from './DynStack.module.css';

const toCamelCase = (s: string) => s ? s.replace(/-([a-z])/g, (g) => g[1].toUpperCase()) : '';

// Valid token keys from stack.json (approximate list for gap)
const GAP_TOKENS = ['none', '2xs', 'xs', 'sm', 'md', 'lg', 'xl', '2xl', '3xl', '4xl'];
const isToken = (v?: string | number) => v !== undefined && GAP_TOKENS.includes(String(v));

const DIRECTIONS = ['vertical', 'horizontal', 'reverse', 'vertical-reverse', 'horizontal-reverse'];
const ALIGNS = ['start', 'center', 'end', 'stretch', 'baseline'];
const JUSTIFIES = ['start', 'center', 'end', 'between', 'around', 'evenly'];
const WRAPS = ['wrap', 'nowrap', 'wrap-reverse'];

export const DynStack = forwardRef(
    <E extends React.ElementType = 'div'>(
        {
            as,
            direction = DYN_STACK_DEFAULT_PROPS.direction,
            gap = DYN_STACK_DEFAULT_PROPS.gap,
            align = DYN_STACK_DEFAULT_PROPS.align,
            justify = DYN_STACK_DEFAULT_PROPS.justify,
            wrap = DYN_STACK_DEFAULT_PROPS.wrap,
            flex,
            className,
            children,
            style,
            ...rest
        }: DynStackProps<E>,
        ref: React.Ref<any>
    ) => {
        const Component = as || 'div';

        const classes = cn(
            styles.container,

            // Direction mapping
            direction && DIRECTIONS.includes(direction) && styles[toCamelCase(direction === 'reverse' ? 'vertical-reverse' : direction) as keyof typeof styles], // Handle 'reverse' alias

            // Gap mapping (Token based)
            gap && isToken(gap) && styles[`gap${toCamelCase(String(gap)).replace(/^\w/, c => c.toUpperCase())}` as keyof typeof styles],

            // Align mapping
            align && ALIGNS.includes(align) && styles[`align${toCamelCase(align).replace(/^\w/, c => c.toUpperCase())}` as keyof typeof styles],

            // Justify mapping
            justify && JUSTIFIES.includes(justify) && styles[`justify${toCamelCase(justify).replace(/^\w/, c => c.toUpperCase())}` as keyof typeof styles],

            // Wrap mapping
            wrap === true && styles.wrap,
            wrap === false && styles.noWrap,

            // Flex variants (not strictly part of stack.json but supported utility)
            styles.flex1 && flex === 1 && styles.flex1,

            className
        );

        const styleVars: React.CSSProperties = {
            ...(direction && !DIRECTIONS.includes(direction) ? { '--dyn-stack-direction': direction } : {}),
            ...(align && !ALIGNS.includes(align) ? { '--dyn-stack-align-items': align } : {}),
            ...(justify && !JUSTIFIES.includes(justify) ? { '--dyn-stack-justify-content': justify } : {}),
            ...(wrap && typeof wrap === 'string' && !WRAPS.includes(wrap) ? { '--dyn-stack-wrap': wrap } : {}),
            ...(gap && !isToken(gap) ? { '--dyn-stack-gap': typeof gap === 'number' ? `${gap}px` : gap } : {}),
            ...style,
            flex: flex !== undefined ? flex : style?.flex,
        } as React.CSSProperties;

        return (
            <Component ref={ref} className={classes} style={styleVars} {...rest}>
                {children}
            </Component>
        );
    }
);

DynStack.displayName = 'DynStack';
