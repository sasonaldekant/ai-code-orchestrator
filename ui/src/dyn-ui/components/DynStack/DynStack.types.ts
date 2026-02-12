import type { ElementType, ReactNode, ComponentPropsWithoutRef } from 'react';
import type { BaseComponentProps, AccessibilityProps } from '../../types';

export type DynStackDirection = 'vertical' | 'horizontal' | 'reverse' | 'vertical-reverse' | 'horizontal-reverse';
export type DynStackGap = 'none' | '2xs' | 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '3xl' | '4xl';
export type DynStackAlign = 'start' | 'center' | 'end' | 'stretch' | 'baseline';
export type DynStackJustify = 'start' | 'center' | 'end' | 'between' | 'around' | 'evenly';

export interface DynStackOwnProps extends BaseComponentProps, AccessibilityProps {
    /** Stack direction */
    direction?: DynStackDirection;

    /** Gap between items */
    gap?: DynStackGap;

    /** Align items */
    align?: DynStackAlign;

    /** Justify content */
    justify?: DynStackJustify;

    /** Whether items should wrap */
    wrap?: boolean;

    /** Children to render */
    children?: ReactNode;

    /** Flex shorthand for the stack itself */
    flex?: string | number;
}

type PolymorphicComponentProps<E extends ElementType, P> = P &
    Omit<ComponentPropsWithoutRef<E>, keyof P>;

export type DynStackProps<E extends ElementType = 'div'> = PolymorphicComponentProps<
    E,
    DynStackOwnProps
> & {
    as?: E;
};

export const DYN_STACK_DEFAULT_PROPS = {
    direction: 'vertical',
    gap: 'md',
    align: 'stretch',
    justify: 'start',
    wrap: false,
} as const;
