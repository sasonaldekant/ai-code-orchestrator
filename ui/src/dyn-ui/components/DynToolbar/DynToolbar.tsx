import React, { forwardRef, useImperativeHandle, useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { cn } from '../../utils/classNames';
import { DynToolbarProps, ToolbarItem, DynToolbarRef, TOOLBAR_DEFAULTS } from './DynToolbar.types';
import { DynIcon } from '../DynIcon';
import { DynBadge } from '../DynBadge';
import styles from './DynToolbar.module.css';

/**
 * DynToolbar - Responsive Toolbar Component
 * Standardized with Design Tokens & CSS Modules
 */
const DynToolbar = forwardRef<DynToolbarRef, DynToolbarProps>((
  {
    items = [],
    variant = TOOLBAR_DEFAULTS.variant,
    size = TOOLBAR_DEFAULTS.size,
    position = TOOLBAR_DEFAULTS.position,
    responsive = TOOLBAR_DEFAULTS.responsive,
    overflowMenu = TOOLBAR_DEFAULTS.overflowMenu,
    overflowThreshold = TOOLBAR_DEFAULTS.overflowThreshold,
    showLabels = TOOLBAR_DEFAULTS.showLabels,
    className,
    itemClassName,
    onItemClick,
    onOverflowToggle
  },
  ref
) => {
  const [visibleItems, setVisibleItems] = useState<ToolbarItem[]>(items);
  const [overflowItems, setOverflowItems] = useState<ToolbarItem[]>([]);
  const [isOverflowOpen, setIsOverflowOpen] = useState(false);
  const [activeDropdown, setActiveDropdown] = useState<string | null>(null);
  const toolbarRef = useRef<HTMLDivElement>(null);

  // Filter visible items
  const filteredItems = useMemo(() => {
    return items.filter(item => item.visible !== false);
  }, [items]);

  // Handle responsive layout
  const updateLayout = useCallback(() => {
    if (!responsive || !overflowMenu || !toolbarRef.current) {
      setVisibleItems(filteredItems);
      setOverflowItems([]);
      return;
    }

    const toolbarWidth = toolbarRef.current.offsetWidth;
    if (!toolbarWidth) {
      setVisibleItems(filteredItems);
      setOverflowItems([]);
      return;
    }

    const itemElements = toolbarRef.current.querySelectorAll('[data-toolbar-item]');
    let totalWidth = 0;
    let visibleCount = 0;
    const overflowButtonWidth = 48;
    const padding = 32;

    for (let i = 0; i < itemElements.length; i++) {
      const itemWidth = itemElements[i].getBoundingClientRect().width;
      if (totalWidth + itemWidth + overflowButtonWidth + padding <= toolbarWidth) {
        totalWidth += itemWidth;
        visibleCount++;
      } else {
        break;
      }
    }

    if (filteredItems.length > overflowThreshold && visibleCount < filteredItems.length) {
      const actualVisibleCount = Math.max(1, Math.min(visibleCount, filteredItems.length - 1));
      setVisibleItems(filteredItems.slice(0, actualVisibleCount));
      setOverflowItems(filteredItems.slice(actualVisibleCount));
    } else {
      setVisibleItems(filteredItems);
      setOverflowItems([]);
    }
  }, [filteredItems, responsive, overflowMenu, overflowThreshold]);

  useEffect(() => {
    updateLayout();
  }, [updateLayout]);

  useEffect(() => {
    if (!responsive || !toolbarRef.current) return;

    let resizeObserver: ResizeObserver | null = null;

    try {
      resizeObserver = new ResizeObserver(() => {
        updateLayout();
      });
      resizeObserver.observe(toolbarRef.current);
    } catch (e) {
      // Fallback or handle error
      window.addEventListener('resize', updateLayout);
    }

    return () => {
      if (resizeObserver && typeof resizeObserver.disconnect === 'function') {
        resizeObserver.disconnect();
      }
      window.removeEventListener('resize', updateLayout);
    };
  }, [responsive, updateLayout]);

  useEffect(() => {
    onOverflowToggle?.(isOverflowOpen);
  }, [isOverflowOpen, onOverflowToggle]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as Node;
      if (toolbarRef.current && !toolbarRef.current.contains(target)) {
        setIsOverflowOpen(false);
        setActiveDropdown(null);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useImperativeHandle(ref, () => ({
    openOverflow: () => setIsOverflowOpen(true),
    closeOverflow: () => setIsOverflowOpen(false),
    toggleOverflow: () => setIsOverflowOpen(prev => !prev),
    refreshLayout: updateLayout
  }));

  const handleItemClick = (item: ToolbarItem, event?: React.MouseEvent) => {
    if (item.disabled) return;

    if (item.type === 'dropdown') {
      event?.preventDefault();
      setActiveDropdown(prev => (prev === item.id ? null : item.id));
      return;
    }

    if (item.action) {
      item.action();
    }

    onItemClick?.(item);

    if (isOverflowOpen) {
      setIsOverflowOpen(false);
    }
  };

  const renderBadge = (badge: ToolbarItem['badge']) => {
    if (!badge) return null;
    const count = typeof badge === 'object' ? badge.count ?? badge.value : badge;
    return (
      <DynBadge
        count={typeof count === 'number' ? count : undefined}
        size="sm"
        className={styles.itemBadge}
      >
        {typeof count !== 'number' ? count : undefined}
      </DynBadge>
    );
  };

  const renderToolbarItem = (item: ToolbarItem, isInOverflow = false) => {
    if (item.type === 'separator') {
      return <div key={item.id} className={styles.separator} data-toolbar-item />;
    }

    if (item.type === 'search') {
      return (
        <div key={item.id} className={styles.search} data-toolbar-item>
          <input
            type="search"
            placeholder={item.label || 'Search...'}
            className={styles.searchInput}
            onChange={(e) => item.onChange?.(e.target.value)}
          />
        </div>
      );
    }

    if (item.type === 'custom' && item.component) {
      return <div key={item.id} className={styles.custom} data-toolbar-item>{item.component}</div>;
    }

    const itemClass = cn(
      styles.item,
      activeDropdown === item.id && styles.itemActive,
      item.disabled && styles.itemDisabled,
      itemClassName
    );

    return (
      <div key={item.id} className={styles.itemWrapper}>
        <button
          type="button"
          className={itemClass}
          onClick={(e) => handleItemClick(item, e)}
          disabled={item.disabled}
          title={item.tooltip || item.label}
          data-toolbar-item
          aria-expanded={item.type === 'dropdown' ? activeDropdown === item.id : undefined}
          aria-haspopup={item.type === 'dropdown' ? 'menu' : undefined}
          aria-label={item.label}
        >
          {item.icon && (
            <span className={styles.itemIcon}>
              {typeof item.icon === 'string' ? <DynIcon icon={item.icon} size="md" /> : item.icon}
            </span>
          )}
          {showLabels && item.label && <span className={styles.itemLabel}>{item.label}</span>}
          {item.badge && renderBadge(item.badge)}
          {item.type === 'dropdown' && (
            <span className={styles.dropdownArrow}>
              <DynIcon icon="chevron-down" size="sm" />
            </span>
          )}
        </button>

        {item.type === 'dropdown' && item.items && activeDropdown === item.id && (
          <div className={styles.dropdownMenu} role="menu">
            {item.items.map(subItem => (
              <button
                key={subItem.id}
                type="button"
                className={styles.dropdownItem}
                onClick={() => handleSelectSubItem(subItem)}
                disabled={subItem.disabled}
                role="menuitem"
              >
                {subItem.icon && (
                  <span className={styles.itemIcon}>
                    {typeof subItem.icon === 'string' ? <DynIcon icon={subItem.icon} size="sm" /> : subItem.icon}
                  </span>
                )}
                <span className={styles.itemLabel}>{subItem.label}</span>
                {subItem.badge && renderBadge(subItem.badge)}
              </button>
            ))}
          </div>
        )}
      </div>
    );
  };

  const handleSelectSubItem = (item: ToolbarItem) => {
    item.action?.();
    onItemClick?.(item);
    setActiveDropdown(null);
  };

  // Explicit variant and size mapping for type safety
  const VARIANT_MAP: Record<NonNullable<DynToolbarProps['variant']>, string | undefined> = {
    default: undefined,
    minimal: styles.variantLight, // CSS uses 'light' for minimal
    floating: styles.variantFloating, // CSS uses 'floating' for floating
  };

  const SIZE_MAP: Record<NonNullable<DynToolbarProps['size']>, string | undefined> = {
    md: undefined,
    sm: styles['sizeSm'],
    lg: styles['sizeLg'],
  };

  const toCamelCase = (s: string) => s.replace(/-([a-z])/g, (g) => g[1].toUpperCase());

  const rootClass = cn(
    styles.root,
    VARIANT_MAP[variant],
    SIZE_MAP[size],
    position && styles[`position${position.charAt(0).toUpperCase() + toCamelCase(position).slice(1)}`],
    className
  );

  return (
    <div className={rootClass} ref={toolbarRef} role="toolbar">
      <div className={styles.content}>
        <div className={styles.items}>
          {visibleItems.map(item => renderToolbarItem(item))}
        </div>

        {overflowItems.length > 0 && (
          <div className={styles.overflow}>
            <button
              type="button"
              className={cn(styles.overflowButton, isOverflowOpen && styles.active)}
              onClick={() => setIsOverflowOpen(prev => !prev)}
              aria-haspopup="menu"
              aria-expanded={isOverflowOpen}
              aria-label="More actions"
            >
              <DynIcon icon="more-horizontal" size="md" />
            </button>

            {isOverflowOpen && (
              <div className={styles.overflowMenu} role="menu">
                {overflowItems.map(item => renderToolbarItem(item, true))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
});

DynToolbar.displayName = 'DynToolbar';

export { DynToolbar };
export default DynToolbar;
