import React, { useMemo, useRef, useState, useEffect, forwardRef, useImperativeHandle, useId } from 'react';
import { cn } from '../../utils/classNames';
import styles from './DynTabs.module.css';
import type { DynTabsProps, DynTabsRef } from './DynTabs.types';
import { DynIcon } from '../DynIcon';
import { DynLoading } from '../DynLoading';

/**
 * DynTabs Component
 * Standardized with Design Tokens & CSS Modules
 */
export const DynTabs = forwardRef<DynTabsRef, DynTabsProps>(
  (
    {
      items = [],
      value,
      activeTab,
      defaultValue,
      defaultActiveTab,
      onChange,
      onTabClose,
      closable,
      position = 'top',
      orientation = 'horizontal',
      activation = 'auto',
      variant = 'default',
      size = 'md',
      fitted = false,
      scrollable = false,
      lazy = false,
      animated = true,
      className,
      id,
      'aria-label': ariaLabel,
      'aria-labelledby': ariaLabelledBy,
      'aria-describedby': ariaDescribedBy,
      'data-testid': dataTestId,
      loadingComponent,
      tabListClassName,
      contentClassName,
      onTabClick,
      addable,
      onTabAdd,
      ...rest
    },
    ref
  ) => {
    const generatedId = useId();
    const internalId = id || generatedId;

    // Process items to ensure they have consistent IDs/values
    const processedItems = useMemo(() => {
      return items.map((item, index) => {
        const processedValue = item.value !== undefined ? String(item.value) : (item.id !== undefined ? String(item.id) : `tab-${index}`);
        return {
          ...item,
          processedValue,
          processedId: item.id || `tab-${index}`
        };
      });
    }, [items]);

    // Handle active tab state
    const controlledValue = activeTab !== undefined ? String(activeTab) : (value !== undefined ? String(value) : undefined);
    const initialValue = defaultActiveTab !== undefined ? String(defaultActiveTab) : (defaultValue !== undefined ? String(defaultValue) : (processedItems[0]?.processedValue));

    const [current, setCurrent] = useState<string | undefined>(controlledValue ?? initialValue);
    const [loaded, setLoaded] = useState<Record<string, boolean>>({});

    useEffect(() => {
      if (controlledValue !== undefined && controlledValue !== current) {
        setCurrent(controlledValue);
      }
    }, [controlledValue, current]);

    // Handle tab selection
    const handleSelect = (val: string, focusPanel = false) => {
      if (controlledValue === undefined) {
        setCurrent(val);
      }
      onChange?.(val);

      if (lazy && !loaded[val]) {
        setLoaded(prev => ({ ...prev, [val]: true }));
      }

      if (focusPanel) {
        const panel = document.getElementById(`${internalId}-panel-${val}`);
        panel?.focus();
      }
    };

    // Keyboard navigation
    const tabsRef = useRef<Array<HTMLButtonElement | null>>([]);
    const currentIndex = processedItems.findIndex(i => i.processedValue === current);

    const handleKeyDown = (e: React.KeyboardEvent) => {
      const isHorizontal = orientation === 'horizontal';
      const count = processedItems.length;
      let nextIndex = currentIndex;

      switch (e.key) {
        case 'ArrowRight':
          if (isHorizontal) nextIndex = (currentIndex + 1) % count;
          break;
        case 'ArrowLeft':
          if (isHorizontal) nextIndex = (currentIndex - 1 + count) % count;
          break;
        case 'ArrowDown':
          if (!isHorizontal) nextIndex = (currentIndex + 1) % count;
          break;
        case 'ArrowUp':
          if (!isHorizontal) nextIndex = (currentIndex - 1 + count) % count;
          break;
        case 'Home':
          nextIndex = 0;
          break;
        case 'End':
          nextIndex = count - 1;
          break;
        case 'Delete':
        case 'Backspace':
          const item = processedItems[currentIndex];
          if (item && (closable || item.closable)) {
            onTabClose?.(item.processedValue);
          }
          return;
        default:
          return;
      }

      if (nextIndex !== currentIndex) {
        e.preventDefault();
        const nextItem = processedItems[nextIndex];
        if (nextItem && !nextItem.disabled) {
          handleSelect(nextItem.processedValue);
          tabsRef.current[nextIndex]?.focus();
        }
      }
    };

    // Imperative handle for DynTabsRef
    useImperativeHandle(ref, () => ({
      focus: () => tabsRef.current[currentIndex]?.focus(),
      blur: () => tabsRef.current[currentIndex]?.blur(),
      focusTab: (tabId: string) => {
        const index = processedItems.findIndex(i => i.processedValue === tabId);
        if (index >= 0) tabsRef.current[index]?.focus();
      },
      getActiveTab: () => current,
      setActiveTab: (tabId: string) => handleSelect(tabId),
      getTabs: () => tabsRef.current.filter(Boolean) as HTMLButtonElement[],
      getTabElement: (tabId: string) => {
        const index = processedItems.findIndex(i => i.processedValue === tabId);
        return index >= 0 ? tabsRef.current[index] : null;
      },
      getActiveTabElement: () => tabsRef.current[currentIndex] || null,
      getTabPanel: (tabId: string) => document.getElementById(`${internalId}-panel-${tabId}`) as HTMLDivElement | null,
      getActiveTabPanel: () => current ? document.getElementById(`${internalId}-panel-${current}`) as HTMLDivElement | null : null
    }), [current, currentIndex, processedItems, internalId, handleSelect]);

    // Explicit position mapping for type safety
    const POSITION_MAP: Record<NonNullable<DynTabsProps['position']>, string> = {
      top: styles.tabsTop,
      bottom: styles.tabsBottom,
      left: styles.tabsLeft,
      right: styles.tabsRight,
    };

    // Style classes
    const rootClass = cn(
      styles.tabs,
      POSITION_MAP[position],
      variant === 'pills' && styles.tabsPills,
      variant === 'underlined' && styles.tabsUnderlined,
      variant === 'bordered' && styles.tabsBordered,
      scrollable && styles.scrollable,
      fitted && styles.tabsFitted,
      className
    );

    const listClass = cn(styles.tablist, tabListClassName);

    if (processedItems.length === 0) return null;

    return (
      <div id={internalId} className={rootClass} data-testid={dataTestId || 'dyn-tabs'} {...rest}>
        <div
          role="tablist"
          aria-label={ariaLabel}
          aria-labelledby={ariaLabelledBy}
          aria-describedby={ariaDescribedBy}
          aria-orientation={orientation === 'horizontal' ? 'horizontal' : 'vertical'}
          className={listClass}
          onKeyDown={handleKeyDown}
        >
          {processedItems.map((item, index) => {
            const isSelected = item.processedValue === current;
            const tabId = `${internalId}-tab-${item.processedValue}`;
            const panelId = `${internalId}-panel-${item.processedValue}`;

            const SIZE_MAP: Record<string, string> = {
              sm: styles.sizeSm,
              md: styles.sizeMd,
              lg: styles.sizeLg
            };

            const tabClass = cn(
              styles.tab,
              isSelected && styles.tabActive,
              item.disabled && styles.tabDisabled,
              SIZE_MAP[size] || styles.sizeMd,
              variant === 'pills' && styles.variantPill,
              variant === 'underlined' && styles.variantUnderlined,
              variant === 'bordered' && styles.variantBordered
            );

            // Handle tab click with optional callback
            const handleTabClick = (e: React.MouseEvent) => {
              if (item.disabled) return;

              // Call onTabClick if provided, allow prevent default
              if (onTabClick) {
                const shouldContinue = onTabClick(item.processedValue, e);
                if (shouldContinue === false) return;
              }

              handleSelect(item.processedValue, activation === 'auto');
            };

            return (
              <div
                key={item.processedId}
                ref={el => { tabsRef.current[index] = el as any; }}
                id={tabId}
                role="tab"
                className={tabClass}
                aria-selected={isSelected}
                aria-controls={panelId}
                aria-disabled={item.disabled}
                tabIndex={isSelected ? 0 : -1}
                onClick={handleTabClick}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    handleSelect(item.processedValue, activation === 'auto');
                  }
                }}
                data-status={isSelected ? 'active' : item.disabled ? 'disabled' : 'inactive'}
              >
                <div className={styles.tabContent}>
                  {item.icon && (
                    <span className={styles.icon}>
                      {typeof item.icon === 'string' ? <DynIcon icon={item.icon} size="sm" /> : item.icon}
                    </span>
                  )}
                  <span className={styles.label}>{item.label}</span>
                  {item.badge && <span className={styles.badge}>{item.badge}</span>}
                  {(closable || item.closable) && (
                    <span
                      className={styles.closeButton}
                      aria-label="Close tab"
                      title="Close tab (Delete)"
                      data-testid={dataTestId ? `${dataTestId}-close-${item.processedValue}` : undefined}
                      onClick={(e) => {
                        e.stopPropagation();
                        onTabClose?.(item.processedValue);
                      }}
                    >
                      <DynIcon icon="close" size="sm" />
                    </span>
                  )}
                </div>
              </div>
            );
          })}

          {addable && onTabAdd && (
            <button
              type="button"
              className={styles.addableButton}
              onClick={onTabAdd}
              aria-label="Add tab"
            >
              <DynIcon icon="plus" size="sm" />
            </button>
          )}
        </div>

        {processedItems.map(item => {
          const isSelected = item.processedValue === current;
          const panelId = `${internalId}-panel-${item.processedValue}`;
          const tabId = `${internalId}-tab-${item.processedValue}`;

          const isLoaded = !lazy || loaded[item.processedValue];

          return (
            <div
              key={`panel-${item.processedValue}`}
              id={panelId}
              role="tabpanel"
              aria-labelledby={tabId}
              hidden={!isSelected}
              className={cn(styles.panel, animated && styles.panelAnimated, contentClassName)}
              tabIndex={0}
            >
              {isSelected && (
                <>
                  {!isLoaded && (
                    <div className={styles.loading}>
                      <DynLoading
                        label={typeof loadingComponent === 'string' ? loadingComponent : (loadingComponent ? undefined : 'Loading...')}
                        size="md"
                      />
                      {loadingComponent && typeof loadingComponent !== 'string' && loadingComponent}
                    </div>
                  )}
                  {isLoaded && (typeof item.content === 'function' ? item.content({ value: item.processedValue, selected: isSelected }) : item.content)}
                </>
              )}
            </div>
          );
        })}
      </div>
    );
  }
);

DynTabs.displayName = 'DynTabs';
export default DynTabs;
