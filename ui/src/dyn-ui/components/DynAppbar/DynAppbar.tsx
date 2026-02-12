import React, { forwardRef } from 'react';
import { cn } from '../../utils/classNames';
import { DynAppbarProps, DYN_APPBAR_DEFAULT_PROPS } from './DynAppbar.types';
import styles from './DynAppbar.module.css';

// Explicit position mapping for type safety
const POSITION_MAP: Record<'sticky' | 'fixed', string> = {
    sticky: styles.sticky,
    fixed: styles.fixed,
};

export const DynAppbar = forwardRef<HTMLDivElement, DynAppbarProps>(
    (
        {
            leftContent,
            rightContent,
            title,
            centerContent,
            position = DYN_APPBAR_DEFAULT_PROPS.position,
            size = DYN_APPBAR_DEFAULT_PROPS.size,
            variant = DYN_APPBAR_DEFAULT_PROPS.variant,
            loading = false,
            className,
            children,
            id,
            style,
            'data-testid': dataTestId,
            ...rest
        },
        ref
    ) => {
        const rootClasses = cn(
            styles.container,
            position !== 'static' && POSITION_MAP[position as 'sticky' | 'fixed'],
            styles[variant!],
            styles[`size${size!.charAt(0).toUpperCase()}${size!.slice(1)}`],
            className
        );

        return (
            <header
                ref={ref}
                id={id}
                style={style}
                data-testid={dataTestId || 'dyn-appbar'}
                className={rootClasses}
                aria-busy={loading}
                {...rest}
            >
                <div className={styles.content}>
                    {(leftContent || title) && (
                        <div className={styles.left}>
                            {leftContent}
                            {title && (
                                <div className={styles.title}>
                                    {typeof title === 'string' ? <h3>{title}</h3> : title}
                                </div>
                            )}
                        </div>
                    )}

                    {centerContent && <div className={styles.center}>{centerContent}</div>}

                    {children && <div className={styles.center}>{children}</div>}

                    {rightContent && <div className={styles.right}>{rightContent}</div>}
                </div>

                {loading && (
                    <div className={styles.loadingBar} role="progressbar" aria-hidden="true">
                        <div className={styles.loadingProgress} />
                    </div>
                )}
            </header>
        );
    }
);

DynAppbar.displayName = 'DynAppbar';

export default DynAppbar;
