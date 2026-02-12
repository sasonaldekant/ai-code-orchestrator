import React from 'react';
import { cn } from '../../utils/classNames';
import { DynAccordionItemProps } from './DynAccordion.types';
import { DynIcon } from '../DynIcon/DynIcon';
import DynLoading from '../DynLoading/DynLoading';
import styles from './DynAccordion.module.css';
export const DynAccordionItem: React.FC<DynAccordionItemProps> = ({
    id,
    title,
    content,
    disabled,
    loading,
    isExpanded,
    onToggle,
    size = 'md',
    expandIcon,
}) => {
    const headerId = `header-${id}`;
    const contentId = `content-${id}`;

    return (
        <div className={cn(
            styles.item,
            { [styles.expanded]: isExpanded },
            styles[`size${size.charAt(0).toUpperCase()}${size.slice(1)}`]
        )}>
            <button
                type="button"
                className={cn(styles.header, {
                    [styles.disabled]: disabled || loading,
                    [styles.loading]: loading
                })}
                onClick={onToggle}
                aria-expanded={isExpanded}
                aria-controls={contentId}
                id={headerId}
                disabled={disabled || loading}
            >
                <div className={styles.headerContent}>
                    {loading && (
                        <div className={styles.loadingSpinner}>
                            <DynLoading size="xs" />
                        </div>
                    )}
                    <span className={styles.title}>{title}</span>
                </div>
                <span className={styles.icon} aria-hidden="true">
                    {expandIcon || <DynIcon icon="chevron-down" size="sm" />}
                </span>
            </button>
            <div
                className={styles.contentWrapper}
                id={contentId}
                role="region"
                aria-labelledby={headerId}
            >
                <div className={styles.content}>
                    <div className={styles.contentInner}>
                        {content}
                    </div>
                </div>
            </div>
        </div>
    );
};
