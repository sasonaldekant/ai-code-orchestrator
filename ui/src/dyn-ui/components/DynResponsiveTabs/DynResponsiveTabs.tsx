import React, { forwardRef, useState, useEffect, useMemo, useCallback, useId } from 'react';
import type { KeyboardEventHandler } from 'react';
import { cn } from '../../utils/classNames';
import { DynIcon } from '../DynIcon';
import type {
  DynResponsiveTabsProps,
  DynResponsiveTabsRef,
  DynResponsiveTabsDefaultProps,
} from './DynResponsiveTabs.types';
import { DYN_RESPONSIVE_TABS_DEFAULT_PROPS } from './DynResponsiveTabs.types';
import styles from './DynResponsiveTabs.module.css';

/**
 * Hook to detect responsive breakpoint
 */
const useResponsiveMode = (breakpoint: number, responsive: boolean): boolean => {
  const [isAccordion, setIsAccordion] = useState(() => {
    // Initial state based on current window size
    if (!responsive) return false;
    if (typeof window === 'undefined') return false;
    return window.innerWidth <= breakpoint;
  });

  useEffect(() => {
    if (!responsive) {
      setIsAccordion(false);
      return;
    }

    // Check immediately on mount
    const checkBreakpoint = () => {
      setIsAccordion(window.innerWidth <= breakpoint);
    };

    checkBreakpoint();

    // Use both matchMedia and resize for better compatibility
    const mediaQuery = window.matchMedia(`(max-width: ${breakpoint}px)`);

    const handleChange = (e: MediaQueryListEvent | MediaQueryList) => {
      setIsAccordion(e.matches);
    };

    // Debounce resize handler with RAF to prevent layout thrashing
    let rafId: number | null = null;
    const handleResize = () => {
      if (rafId) return;
      rafId = window.requestAnimationFrame(() => {
        checkBreakpoint();
        rafId = null;
      });
    };

    // Modern browsers
    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener('change', handleChange);
      // Also listen to resize for Storybook viewport changes
      window.addEventListener('resize', handleResize);
      return () => {
        mediaQuery.removeEventListener('change', handleChange);
        window.removeEventListener('resize', handleResize);
        if (rafId) cancelAnimationFrame(rafId);
      };
    }
    // Legacy browsers
    else {
      mediaQuery.addListener(handleChange);
      window.addEventListener('resize', handleResize);
      return () => {
        mediaQuery.removeListener(handleChange);
        window.removeEventListener('resize', handleResize);
        if (rafId) cancelAnimationFrame(rafId);
      };
    }
  }, [breakpoint, responsive]);

  return isAccordion;
};

/**
 * DynResponsiveTabs
 *
 * Responsive tabs component that transforms into accordion on smaller screens.
 * Supports nested tabs composition for complex layouts.
 * Follows DYN UI architecture, accessibility standards, and design token system.
 */
export const DynResponsiveTabs = forwardRef<DynResponsiveTabsRef, DynResponsiveTabsProps>(
  (
    {
      tabs,
      defaultActive = DYN_RESPONSIVE_TABS_DEFAULT_PROPS.defaultActive,
      activeTab,
      orientation = DYN_RESPONSIVE_TABS_DEFAULT_PROPS.orientation,
      responsive = DYN_RESPONSIVE_TABS_DEFAULT_PROPS.responsive,
      breakpoint = DYN_RESPONSIVE_TABS_DEFAULT_PROPS.breakpoint,
      allowCollapse = DYN_RESPONSIVE_TABS_DEFAULT_PROPS.allowCollapse,
      expandIcon = DYN_RESPONSIVE_TABS_DEFAULT_PROPS.expandIcon,
      collapseIcon = DYN_RESPONSIVE_TABS_DEFAULT_PROPS.collapseIcon,
      disableAnimation = DYN_RESPONSIVE_TABS_DEFAULT_PROPS.disableAnimation,
      tabIdentifier,
      onChange,
      onTabChange,
      className,
      id,
      'aria-label': ariaLabel,
      'data-testid': dataTestId,
      ...rest
    },
    ref
  ) => {
    // Determine if we're in controlled mode
    const isControlled = activeTab !== undefined;

    // Generate unique ID for this tabs instance
    const generatedId = useId();
    const internalId = useMemo(() => id || generatedId, [id, generatedId]);

    // Internal state for uncontrolled mode
    const [internalActiveIndex, setInternalActiveIndex] = useState(defaultActive);

    // Use activeTab prop if controlled, otherwise use internal state
    const currentActiveIndex = isControlled ? activeTab : internalActiveIndex;

    const isAccordion = useResponsiveMode(breakpoint, responsive);

    // Validate tabs
    const validTabs = useMemo(() => {
      return tabs.filter(tab => tab && (tab.label || tab.content));
    }, [tabs]);

    // Handle tab click - supports both controlled and uncontrolled modes
    const handleTabClick = useCallback((index: number, disabled?: boolean) => {
      if (disabled) return;

      let newIndex = index;

      // In accordion mode with allowCollapse, toggle the same tab
      if (isAccordion && allowCollapse && currentActiveIndex === index) {
        newIndex = -1;
      }

      // Update internal state if uncontrolled
      if (!isControlled) {
        setInternalActiveIndex(newIndex);
      }

      // Call appropriate callback
      if (isControlled && onTabChange) {
        onTabChange(newIndex);
      } else if (onChange) {
        onChange(newIndex);
      }
    }, [isAccordion, allowCollapse, currentActiveIndex, isControlled, onChange, onTabChange]);

    // Keyboard navigation for tabs (non-accordion mode)
    const handleTabKeyDown: (index: number) => KeyboardEventHandler<HTMLButtonElement> =
      useCallback((index) => (event) => {
        if (isAccordion) return;

        const tabCount = validTabs.length;
        let nextIndex = index;

        switch (event.key) {
          case 'ArrowRight':
          case 'ArrowDown':
            event.preventDefault();
            nextIndex = (index + 1) % tabCount;
            // Skip disabled tabs
            while (validTabs[nextIndex]?.disabled && nextIndex !== index) {
              nextIndex = (nextIndex + 1) % tabCount;
            }
            break;
          case 'ArrowLeft':
          case 'ArrowUp':
            event.preventDefault();
            nextIndex = (index - 1 + tabCount) % tabCount;
            // Skip disabled tabs
            while (validTabs[nextIndex]?.disabled && nextIndex !== index) {
              nextIndex = (nextIndex - 1 + tabCount) % tabCount;
            }
            break;
          case 'Home':
            event.preventDefault();
            nextIndex = 0;
            while (validTabs[nextIndex]?.disabled && nextIndex < tabCount - 1) {
              nextIndex++;
            }
            break;
          case 'End':
            event.preventDefault();
            nextIndex = tabCount - 1;
            while (validTabs[nextIndex]?.disabled && nextIndex > 0) {
              nextIndex--;
            }
            break;
          default:
            return;
        }

        if (nextIndex !== index && !validTabs[nextIndex]?.disabled) {
          handleTabClick(nextIndex);
          // Focus the next tab
          const nextButton = document.getElementById(
            `${internalId}-tab-${nextIndex}`
          ) as HTMLButtonElement;
          nextButton?.focus();
        }
      }, [isAccordion, validTabs, handleTabClick, internalId]);

    // Generate CSS classes
    const containerClass = cn(
      styles.container,
      // Map orientation to specific class if needed, checking specifically for 'vertical'
      orientation === 'vertical' && styles.orientationVertical,
      {
        [styles.accordion]: isAccordion,
        [styles.nested]: tabIdentifier !== undefined,
        [styles.noAnimation]: disableAnimation,
      },
      className
    );

    // Render tab headers (non-accordion mode)
    const renderTabHeaders = () => {
      if (isAccordion) return null;

      return (
        <div
          role="tablist"
          className={cn(
            styles.tabList,
            // Only add dynamic class if using modules correctly, normally dynamic classes like this
            // don't work with modules comfortably unless explicitly defined. 
            // Safeguarding with styles access, assuming styles[...] might be undefined.
            tabIdentifier && styles[`tabList-${tabIdentifier}`]
          )}
          aria-label={ariaLabel}
          aria-orientation={orientation}
        >
          {validTabs.map((tab, index) => {
            const isActive = currentActiveIndex === index;
            const isDisabled = tab.disabled;
            const tabId = `${internalId}-tab-${index}`;
            const panelId = `${internalId}-panel-${index}`;

            return (
              <button
                key={index}
                id={tabId}
                ref={isActive ? ref : undefined}
                role="tab"
                type="button"
                aria-selected={isActive}
                aria-controls={panelId}
                aria-disabled={isDisabled || undefined}
                disabled={isDisabled}
                tabIndex={isActive ? 0 : -1}
                className={cn(
                  styles.tab,
                  {
                    [styles.activeTab]: isActive,
                    [styles.disabledTab]: isDisabled,
                  }
                )}
                onClick={() => handleTabClick(index, isDisabled)}
                onKeyDown={handleTabKeyDown(index)}
                data-testid={`${dataTestId || 'dyn-responsive-tabs'}-tab-${index}`}
              >
                {tab.icon && (
                  <span className={styles.tabIcon} aria-hidden="true">
                    {typeof tab.icon === 'string' ? (
                      <DynIcon icon={tab.icon} size="sm" />
                    ) : (
                      tab.icon
                    )}
                  </span>
                )}
                {tab.label}
              </button>
            );
          })}
        </div>
      );
    };

    // Render panels
    const renderPanels = () => {
      return (
        <div className={styles.panelContainer}>
          {validTabs.map((tab, index) => {
            const isActive = currentActiveIndex === index;
            const tabId = `${internalId}-${isAccordion ? 'accordion' : 'tab'}-${index}`;
            const panelId = `${internalId}-panel-${index}`;
            const isDisabled = tab.disabled;

            return (
              <div key={index} className={styles.panelWrapper}>
                {/* Accordion header (mobile view) */}
                {isAccordion && (
                  <button
                    id={tabId}
                    ref={isActive ? ref : undefined}
                    type="button"
                    className={cn(
                      styles.accordionHeader,
                      {
                        [styles.activeAccordion]: isActive,
                        [styles.disabledAccordion]: isDisabled,
                      }
                    )}
                    aria-expanded={isActive}
                    aria-controls={panelId}
                    aria-disabled={isDisabled || undefined}
                    disabled={isDisabled}
                    onClick={() => handleTabClick(index, isDisabled)}
                    data-testid={`${dataTestId || 'dyn-responsive-tabs'}-accordion-${index}`}
                  >
                    <span className={styles.accordionLabel}>
                      {tab.icon && (
                        <span className={styles.accordionIcon} aria-hidden="true">
                          {typeof tab.icon === 'string' ? (
                            <DynIcon icon={tab.icon} size="sm" />
                          ) : (
                            tab.icon
                          )}
                        </span>
                      )}
                      {tab.label}
                    </span>
                    <span className={styles.accordionToggle} aria-hidden="true">
                      {typeof expandIcon === 'string' ? (
                        <DynIcon icon={isActive ? collapseIcon as string : expandIcon} size="sm" />
                      ) : isActive ? (
                        collapseIcon
                      ) : (
                        expandIcon
                      )}
                    </span>
                  </button>
                )}

                {/* Panel content */}
                <div
                  id={panelId}
                  role="tabpanel"
                  aria-labelledby={tabId}
                  hidden={!isActive}
                  className={cn(
                    styles.panel,
                    {
                      [styles.activePanel]: isActive,
                    }
                  )}
                  data-testid={`${dataTestId || 'dyn-responsive-tabs'}-panel-${index}`}
                >
                  {/* Render content - supports nested tabs */}
                  {isActive && tab.content}
                </div>
              </div>
            );
          })}
        </div>
      );
    };

    return (
      <div
        id={internalId}
        className={containerClass}
        data-testid={dataTestId || 'dyn-responsive-tabs'}
        {...rest}
      >
        {renderTabHeaders()}
        {renderPanels()}
      </div>
    );
  }
);

DynResponsiveTabs.displayName = 'DynResponsiveTabs';

export default DynResponsiveTabs;
