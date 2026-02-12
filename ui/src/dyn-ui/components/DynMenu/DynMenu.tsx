import React, { useEffect, useMemo, useRef, useState, forwardRef, useId } from 'react';
import { cn } from '../../utils/classNames';
import styles from './DynMenu.module.css';
import { DynIcon } from '../DynIcon';
import type { DynMenuProps, DynMenuItem } from './DynMenu.types';



export const DynMenu: React.FC<DynMenuProps> = ({
  items,
  orientation = 'horizontal',
  className,
  id,
  'aria-label': ariaLabel,
  'aria-labelledby': ariaLabelledBy,
  'data-testid': dataTestId,
  onAction,
  ...rest
}) => {
  const generatedId = useId();
  const internalId = id || generatedId;
  const isHorizontal = orientation === 'horizontal';
  const [openIndex, setOpenIndex] = useState<number | null>(null);
  const [focusIndex, setFocusIndex] = useState<number>(0);

  const menubarRef = useRef<HTMLDivElement | null>(null);
  const itemRefs = useRef<Array<HTMLButtonElement | null>>([]);

  useEffect(() => {
    if (focusIndex >= 0) itemRefs.current[focusIndex]?.focus();
  }, [focusIndex]);

  const visibleMenuCount = useMemo(() => items.length, [items]);

  const moveFocus = (delta: number) => {
    if (!visibleMenuCount) return;
    setFocusIndex((prev) => {
      const next = (prev + delta + visibleMenuCount) % visibleMenuCount;
      return next;
    });
  };

  const closeAll = () => setOpenIndex(null);

  const onMenubarKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    const horizontal = isHorizontal;
    switch (e.key) {
      case 'ArrowRight': if (horizontal) { e.preventDefault(); moveFocus(1); } break;
      case 'ArrowLeft': if (horizontal) { e.preventDefault(); moveFocus(-1); } break;
      case 'ArrowDown': if (!horizontal) { e.preventDefault(); moveFocus(1); } else if (openIndex === focusIndex) { e.preventDefault(); /* focus first submenu item handled by browser tab */ } break;
      case 'ArrowUp': if (!horizontal) { e.preventDefault(); moveFocus(-1); } break;
      case 'Home': e.preventDefault(); setFocusIndex(0); break;
      case 'End': e.preventDefault(); setFocusIndex(Math.max(0, visibleMenuCount - 1)); break;
      case 'Enter':
      case ' ': {
        e.preventDefault();
        setOpenIndex((prev) => (prev === focusIndex ? null : focusIndex));
        break;
      }
      case 'Escape':
        if (openIndex !== null) { e.preventDefault(); closeAll(); }
        break;
    }
  };

  const handleItemClick = (index: number) => {
    setOpenIndex((prev) => (prev === index ? null : index));
    setFocusIndex(index);
  };

  const onSubItemClick = (action: string | (() => void) | undefined) => {
    if (typeof action === 'string') {
      onAction?.(action);
    } else if (typeof action === 'function') {
      try {
        action();
      } catch {
        // ignore errors from provided callback
      }
    }
    closeAll();
  };

  return (
    <div
      id={internalId}
      role="menubar"
      aria-label={ariaLabel}
      aria-labelledby={ariaLabelledBy}
      aria-orientation={orientation}
      className={cn(styles.menubar, className)}
      data-testid={dataTestId || 'dyn-menu'}
      ref={menubarRef}
      onKeyDown={onMenubarKeyDown}
      {...rest}
    >
      {items.map((item, idx) => {
        const isOpen = openIndex === idx;
        const buttonId = `${internalId}-item-${idx}`;
        const menuId = `${internalId}-submenu-${idx}`;
        return (
          <div key={buttonId} className={styles.menubarItem}>
            <button
              ref={(el) => { itemRefs.current[idx] = el; }}
              id={buttonId}
              type="button"
              role="menuitem"
              className={cn(styles.menubarButton, isOpen && styles.menubarButtonOpen)}
              aria-haspopup={item.children && item.children.length ? 'menu' : undefined}
              aria-expanded={item.children && item.children.length ? isOpen : undefined}
              aria-controls={item.children && item.children.length ? menuId : undefined}
              onClick={() => handleItemClick(idx)}
            >
              <div className={styles.menubarButtonContent}>
                {item.icon && (
                  <span className={styles.menubarIcon}>
                    <DynIcon icon={item.icon} size="sm" />
                  </span>
                )}
                <span className={styles.menubarLabel}>{item.label}</span>
              </div>
              {item.children && item.children.length > 0 && (
                <span className={cn(styles.menubarChevron)}>
                  <DynIcon icon={isHorizontal ? 'chevron-down' : 'chevron-right'} size="sm" />
                </span>
              )}
            </button>
            {item.children && item.children.length > 0 && isOpen && (
              <div
                id={menuId}
                role="menu"
                aria-labelledby={buttonId}
                className={styles.menu}
              >
                {item.children.map((sub, sidx) => (
                  <button
                    key={`${menuId}-opt-${sidx}`}
                    role="menuitem"
                    type="button"
                    className={styles.menuItem}
                    onClick={() => onSubItemClick(sub.action)}
                  >
                    {sub.icon && (
                      <span className={styles.menuIcon}>
                        <DynIcon icon={sub.icon} size="sm" />
                      </span>
                    )}
                    <span className={styles.menuLabel}>{sub.label}</span>
                  </button>
                ))}
              </div>
            )}

          </div>
        );
      })}
    </div>
  );
};

export default DynMenu;
