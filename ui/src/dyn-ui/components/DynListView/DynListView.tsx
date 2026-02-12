import React, { forwardRef, useEffect, useImperativeHandle, useMemo, useRef, useState, useId } from 'react';
import { cn } from '../../utils/classNames';
import styles from './DynListView.module.css';
import type { DynListViewProps, DynListViewRef, ListViewItem, ListAction } from './DynListView.types';
import { DynIcon } from '../DynIcon';
import { DynCheckbox } from '../DynCheckbox';
import { DynButton } from '../DynButton';
import { DynStack } from '../DynStack';
import { DynBox } from '../DynBox';
import { DynLoading } from '../DynLoading';


const isComplexItem = (item: any) => {
  // Consider item complex if it has more than typical display fields
  const displayKeys = new Set(['id', 'title', 'label', 'value', 'description', 'icon', 'disabled', 'selected']);
  const keys = Object.keys(item || {});
  return keys.filter(k => !displayKeys.has(k)).length >= 3; // threshold can be tuned
};

export const DynListView = forwardRef<HTMLDivElement, DynListViewProps>(function DynListView(
  {
    items = [],
    data = [], // legacy alias
    value,
    defaultValue,
    multiSelect = false,
    selectable = false,
    disabled = false,
    loading = false,
    emptyText = 'No data available',
    loadingText = 'Loading...',
    selectAllText = 'Select All',
    expandText = 'Expand',
    collapseText = 'Collapse',
    dividers = false,
    striped = false,
    actions = [],
    renderItem,
    size,
    height,
    bordered = false,
    selectedKeys = [],
    itemKey,
    onChange,
    onSelectionChange,
    className,
    id,
    'aria-label': ariaLabel,
    'aria-labelledby': ariaLabelledBy,
    'data-testid': dataTestId,
    ...rest
  }, ref) {

  // Internal ref for imperative handle
  const rootRef = useRef<HTMLDivElement>(null);

  // Use items prop, fallback to data for backward compatibility
  const listItems = items.length > 0 ? items : data;

  const generatedId = useId();
  const internalId = id || generatedId;
  const isControlled = value !== undefined;
  const [selected, setSelected] = useState<string[] | string | undefined>(
    value ?? (multiSelect ? [] : defaultValue)
  );
  const [activeIndex, setActiveIndex] = useState(0);
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});

  useEffect(() => {
    if (isControlled) setSelected(value as any);
  }, [isControlled, value]);

  const itemIds = useMemo(() =>
    listItems.map((_, i) => `${internalId}-option-${i}`),
    [listItems, internalId]
  );

  const getItemKey = (item: ListViewItem, index: number): string => {
    if (typeof itemKey === 'function') return itemKey(item);
    if (typeof itemKey === 'string') return String((item as any)[itemKey]);
    return item.id ? String(item.id) : item.value ? String(item.value) : String(index);
  };

  const isSelected = (val: string) => {
    return multiSelect || selectable ? Array.isArray(selected) && selected.includes(val) : selected === val;
  };

  const commit = (vals: string[] | string) => {
    if (!isControlled) setSelected(vals as any);

    const valArray = Array.isArray(vals) ? vals : [vals];
    const selectedItems = listItems.filter((item, idx) => valArray.includes(getItemKey(item, idx)));

    onChange?.(vals as any, (multiSelect || selectable) ? selectedItems : selectedItems[0]);
    onSelectionChange?.(valArray, selectedItems);
  };

  const toggle = (val: string) => {
    if (disabled) return;
    if (multiSelect || selectable) {
      const current = Array.isArray(selected) ? selected : [];
      const next = current.includes(val) ? current.filter(v => v !== val) : [...current, val];
      commit(next);
    } else {
      commit(val);
    }
  };

  const moveActive = (delta: number) => {
    const count = listItems.length;
    if (!count) return;
    setActiveIndex(idx => (idx + delta + count) % count);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    switch (e.key) {
      case 'ArrowDown': e.preventDefault(); moveActive(1); break;
      case 'ArrowUp': e.preventDefault(); moveActive(-1); break;
      case 'Home': e.preventDefault(); setActiveIndex(0); break;
      case 'End': e.preventDefault(); setActiveIndex(Math.max(0, listItems.length - 1)); break;
      case 'Enter':
      case ' ': {
        e.preventDefault();
        const item = listItems[activeIndex];
        if (item) {
          const key = getItemKey(item, activeIndex);
          toggle(key);
        }
        break;
      }
    }
  };

  const badgeSize = size === 'sm' ? 'xs' : 'sm';
  const iconSize = size === 'sm' ? 'xs' : 'sm';
  // Match DynTable button sizing logic
  const buttonSize = size === 'sm' ? 'xs' : (size === 'lg' ? 'md' : 'sm');

  const rootClasses = cn(
    styles.root,
    size === 'sm' && styles['sizeSm'],
    size === 'lg' && styles['sizeLg'],
    bordered && styles.bordered,
    dividers && styles.dividers,
    striped && styles.striped,
    className
  );

  const rootStyle = height ? {
    height: typeof height === 'number' ? `${height}px` : String(height)
  } : undefined;

  const allKeys = listItems.map((item, i) => getItemKey(item, i));
  const allChecked = (multiSelect || selectable) && allKeys.length > 0 && allKeys.every(k => isSelected(k));

  // Expose imperative methods via ref
  useImperativeHandle(ref, () => ({
    focus: () => rootRef.current?.focus(),
    selectAll: () => commit(allKeys),
    clearSelection: () => commit(multiSelect ? [] : ''),
  }) as unknown as HTMLDivElement, [allKeys, multiSelect, commit]);

  return (
    <div
      ref={rootRef}
      id={internalId}
      role="listbox"
      aria-multiselectable={multiSelect || selectable || undefined}
      aria-label={ariaLabel}
      aria-labelledby={ariaLabelledBy}
      aria-activedescendant={listItems[activeIndex] ? itemIds[activeIndex] : undefined}
      aria-busy={loading}
      aria-disabled={disabled || undefined}
      className={rootClasses}
      data-testid={dataTestId || 'dyn-listview'}
      tabIndex={disabled ? -1 : 0}
      onKeyDown={handleKeyDown}
      style={rootStyle}
      {...rest}
    >
      {(multiSelect || selectable) && (
        <DynBox
          display="flex"
          align="center"
          gap={size === 'sm' ? 'xs' : size === 'lg' ? 'md' : 'sm'}
          px={size === 'sm' ? 'sm' : size === 'lg' ? 'lg' : 'md'}
          py={size === 'sm' ? '2xs' : size === 'lg' ? 'md' : 'sm'}
          className={cn(
            styles.option,
            size === 'sm' && styles['optionSm'],
            size === 'lg' && styles['optionLg']
          )}
          role="option"
          aria-selected={allChecked}
        >
          <DynBox display="flex" align="center" justify="center" onClick={(e: any) => e.stopPropagation()} style={{ flex: 'none' }}>
            <DynCheckbox
              size={buttonSize}
              checked={allChecked}
              onChange={() => commit(allChecked ? [] : allKeys)}
              aria-label={selectAllText}
            />
          </DynBox>
          <DynBox width="50%" display="flex" align="center" gap="sm">
            <span className={cn(
              styles.optionLabel,
              size === 'sm' && styles['optionLabelSm'],
              size === 'lg' && styles['optionLabelLg']
            )}>{selectAllText}</span>
          </DynBox>
        </DynBox>
      )}

      {loading ? (
        <div role="status" className={styles.loading}>
          <DynLoading label={loadingText} size={size === 'lg' ? 'lg' : size === 'sm' ? 'sm' : 'md'} />
        </div>
      ) : listItems.length === 0 ? (
        <div role="note" className={styles.empty}>
          {emptyText}
        </div>
      ) : (
        listItems.map((item, i) => {
          const key = getItemKey(item, i);
          const selectedState = isSelected(key);
          const title = (item as any).title ?? (item as any).label ?? (item as any).name ?? (item as any).value ?? String((item as any).id ?? i + 1);
          const desc = (item as any).description ?? (item as any).email ?? (item as any).role;
          const complex = isComplexItem(item);

          return (
            <DynBox
              key={key}
              id={itemIds[i]}
              role="option"
              aria-selected={selectedState}
              aria-setsize={listItems.length}
              aria-posinset={i + 1}
              direction="column"
              align="stretch"
              gap="none"
              px={size === 'sm' ? 'sm' : size === 'lg' ? 'lg' : 'md'}
              py={size === 'sm' ? '2xs' : size === 'lg' ? 'md' : 'sm'}
              radius="sm"
              className={cn(
                styles.option,
                size === 'sm' && styles['optionSm'],
                size === 'lg' && styles['optionLg'],
                selectedState && styles.optionSelected,
                i === activeIndex && styles.optionActive,
                item.disabled && styles.optionDisabled
              )}
              onMouseEnter={() => !item.disabled && setActiveIndex(i)}
              onMouseDown={(e: any) => e.preventDefault()}
              onClick={() => !item.disabled && toggle(key)}
            >
              <DynBox
                display="flex"
                direction="row"
                align="center"
                width="100%"
                gap={size === 'sm' ? 'xs' : size === 'lg' ? 'md' : 'sm'}
                minHeight={size === 'sm' ? '2rem' : size === 'lg' ? '3.5rem' : '2.5rem'}
              >
                {(selectable || multiSelect) && (
                  <DynBox display="flex" direction="row" align="center" justify="center" onClick={(e: any) => e.stopPropagation()} style={{ flex: 'none' }}>
                    <DynCheckbox
                      size={buttonSize}
                      checked={!!selectedState}
                      disabled={item.disabled}
                      onChange={() => !item.disabled && toggle(key)}
                      aria-label={`Select ${title}`}
                    />
                  </DynBox>
                )}

                <DynBox
                  display="flex"
                  direction="row"
                  align="center"
                  gap="sm"
                  className={styles.optionContentWrapper}
                  style={{ minWidth: 0, flex: 1 }}
                >
                  {item.icon && (
                    <DynBox display="flex" direction="row" align="center" justify="center" mr="xs" style={{ flex: 'none' }}>
                      <DynIcon icon={item.icon} size={iconSize} />
                    </DynBox>
                  )}
                  <DynStack direction="vertical" gap="none" flex={1} style={{ minWidth: 0 }}>
                    {renderItem ? (
                      renderItem(item, i)
                    ) : (
                      <DynStack direction="vertical" gap={size === 'lg' ? 'xs' : '2xs'}>
                        <span className={cn(
                          styles.optionLabel,
                          size === 'sm' && styles['optionLabelSm'],
                          size === 'lg' && styles['optionLabelLg']
                        )}>
                          {title}
                        </span>
                        {desc && (
                          <span className={cn(
                            styles.optionDescription,
                            size === 'sm' && styles['optionDescSm'],
                            size === 'lg' && styles['optionDescLg']
                          )}>
                            {desc}
                          </span>
                        )}
                      </DynStack>
                    )}
                  </DynStack>
                </DynBox>

                {actions && actions.length > 0 && (
                  <div
                    className={styles.optionActions}
                    onClick={(e) => e.stopPropagation()}
                    style={{ flex: 'none' }}
                  >
                    {actions.map((action) => (
                      <DynButton
                        key={action.key}
                        size={buttonSize}
                        kind={action.type === 'primary' ? 'soft' : action.type === 'danger' ? 'secondary' : 'tertiary'}
                        color={action.type === 'danger' ? 'danger' : 'primary'}
                        onClick={() => action.onClick(item, i)}
                        title={action.title}
                        icon={action.icon}
                        label={action.title}
                      />
                    ))}
                  </div>
                )}

                {complex && (
                  <DynButton
                    kind="tertiary"
                    size={buttonSize}
                    onClick={(e) => {
                      e.stopPropagation();
                      setExpanded(prev => ({ ...prev, [key]: !prev[key] }));
                    }}
                    aria-expanded={!!expanded[key]}
                    label={expanded[key] ? collapseText : expandText}
                    title={expanded[key] ? collapseText : expandText}
                  />
                )}
              </DynBox>

              {expanded[key] && (
                <DynBox
                  mt="sm"
                  p="md"
                  background="surface"
                  border="default"
                  radius="sm"
                  className={styles.optionDetails}
                  width="100%"
                >
                  {Object.entries(item).map(([k, v]) => (
                    <DynBox
                      key={k}
                      py="2xs"
                      style={{ borderBottom: k === Object.keys(item).pop() ? 'none' : '1px solid var(--dyn-semantic-border)' }}
                    >
                      <strong>{k}:</strong> {String(v)}
                    </DynBox>
                  ))}
                </DynBox>
              )}
            </DynBox>
          );
        })
      )}
    </div>
  );
});

export default DynListView;
