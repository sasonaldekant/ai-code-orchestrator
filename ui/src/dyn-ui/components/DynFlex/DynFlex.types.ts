import type { ElementType, ReactNode, ComponentPropsWithoutRef } from 'react';
import type { BaseComponentProps, AccessibilityProps } from '../../types';

export type DynFlexDirection = 'row' | 'column' | 'row-reverse' | 'column-reverse';
export type DynFlexJustify = 'start' | 'center' | 'end' | 'between' | 'around' | 'evenly';
export type DynFlexAlign = 'start' | 'center' | 'end' | 'stretch' | 'baseline';
export type DynFlexWrap = 'nowrap' | 'wrap' | 'wrap-reverse';
export type DynFlexGap = 'none' | '2xs' | 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '3xl' | '4xl';

export interface DynFlexOwnProps extends BaseComponentProps, AccessibilityProps {
    /** Flex direction */
    direction?: DynFlexDirection;

    /** Justify content */
    justify?: DynFlexJustify;

    /** Align items */
    align?: DynFlexAlign;

    /** Flex wrap */
    wrap?: DynFlexWrap;

    /** Gap between items */
    gap?: DynFlexGap;

    /** Display as inline-flex */
    inline?: boolean;

    /** Padding around the container */
    padding?: DynFlexGap;

    /** Children to render */
    children?: ReactNode;
}

type PolymorphicComponentProps<E extends ElementType, P> = P &
    Omit<ComponentPropsWithoutRef<E>, keyof P>;

export type DynFlexProps<E extends ElementType = 'div'> = PolymorphicComponentProps<
    E,
    DynFlexOwnProps
> & {
    as?: E;
};

export type DynFlexRef<E extends ElementType = 'div'> = React.ComponentRef<E>;

export const DYN_FLEX_DEFAULT_PROPS = {
    direction: 'row',
    justify: 'start',
    align: 'stretch',
    wrap: 'nowrap',
    gap: 'md',
    inline: false,
} as const;
