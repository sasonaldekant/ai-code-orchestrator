import React, { useEffect, useMemo, useRef, useState, useId } from 'react';
import { cn } from '../../utils/classNames';
import styles from './DynTable.module.css';
import type { DynTableProps, TableSortDirection, DynTableColumn } from './DynTable.types';
import { DynIcon } from '../DynIcon';
import { DynButton } from '../DynButton';
import { DynBadge } from '../DynBadge';
import { DynCheckbox } from '../DynCheckbox';
import { DynRadio } from '../DynRadio';

/**
 * DynTable Component
 * Standardized with Design Tokens & CSS Modules
 */
export const DynTable: React.FC<DynTableProps> = ({
  columns,
  data,
  actions = [],
  loading = false,
  size = 'md',
  bordered = true,
  striped = false,
  hoverable = false,
  selectable = false,
  sortable = true,
  selectedKeys,
  rowKey,
  pagination,
  sortBy,
  onSort,
  onSelectionChange,
  emptyText = 'No data available',
  height,
  className,
  id,
  'aria-label': ariaLabel,
  'aria-labelledby': ariaLabelledBy,
  'aria-describedby': ariaDescribedBy,
  'data-testid': dataTestId,
  ...rest
}) => {
  const generatedId = useId();
  const internalId = id || generatedId;

  const selectionMode = selectable === true ? 'multiple' : selectable === false ? undefined : selectable;
  const isSelectable = selectionMode === 'multiple' || selectionMode === 'single';
  const isMultiSelect = selectionMode === 'multiple';

  const [internalSelectedKeys, setInternalSelectedKeys] = useState<string[]>(() => selectedKeys ?? []);
  useEffect(() => {
    if (selectedKeys !== undefined) {
      const hasChanged = selectedKeys.length !== internalSelectedKeys.length ||
        !selectedKeys.every((k, i) => k === internalSelectedKeys[i]);
      if (hasChanged) {
        setInternalSelectedKeys(selectedKeys);
      }
    }
  }, [selectedKeys, internalSelectedKeys]);

  const [internalSort, setInternalSort] = useState(sortBy ?? null);
  const userHasInteracted = useRef(false);

  useEffect(() => {
    if (sortBy !== undefined && !userHasInteracted.current) {
      setInternalSort(sortBy);
    }
  }, [sortBy?.column, sortBy?.direction]);

  const activeSort = userHasInteracted.current ? internalSort : (sortBy ?? internalSort ?? undefined);

  const sortedData = useMemo(() => {
    if (!activeSort || !sortable) {
      return data;
    }

    const sorted = [...data].sort((a, b) => {
      const aValue = a[activeSort.column];
      const bValue = b[activeSort.column];

      if (aValue == null && bValue == null) return 0;
      if (aValue == null) return 1;
      if (bValue == null) return -1;

      if (typeof aValue === 'string' && typeof bValue === 'string') {
        const comparison = aValue.localeCompare(bValue);
        return activeSort.direction === 'asc' ? comparison : -comparison;
      }

      if (typeof aValue === 'number' && typeof bValue === 'number') {
        return activeSort.direction === 'asc' ? aValue - bValue : bValue - aValue;
      }

      if (typeof aValue === 'boolean' && typeof bValue === 'boolean') {
        const comparison = aValue === bValue ? 0 : aValue ? 1 : -1;
        return activeSort.direction === 'asc' ? comparison : -comparison;
      }

      const aStr = String(aValue);
      const bStr = String(bValue);
      const comparison = aStr.localeCompare(bStr);
      return activeSort.direction === 'asc' ? comparison : -comparison;
    });

    return sorted;
  }, [data, activeSort, sortable]);

  const getRowKeyInternal = (row: any, index: number) => {
    if (typeof rowKey === 'function') return rowKey(row);
    if (typeof rowKey === 'string' && rowKey in row) return String(row[rowKey]);
    if ('id' in row) return String(row.id);
    return String(index);
  };

  const rowKeys = useMemo(
    () => sortedData.map((row, index) => getRowKeyInternal(row, index)),
    [sortedData, rowKey]
  );

  const toCamelCase = (s: string) => s ? s.replace(/-([a-z])/g, (g) => g[1].toUpperCase()) : '';


  const SIZE_MAP: Record<string, string> = {
    sm: styles['sizeSm'],
    md: styles['sizeMd'],
    lg: styles['sizeLg']
  };

  const badgeSize = size === 'sm' ? 'xs' : 'sm';
  const iconSize = size === 'sm' ? 'xs' : 'sm';
  const buttonSize = size === 'sm' ? 'xs' : (size === 'lg' ? 'md' : 'sm');

  const rootClasses = cn(
    styles.root,
    bordered && styles.bordered,
    striped && styles.striped,
    hoverable && styles.hoverable,
    height !== undefined && styles.fixedHeight,
    size && SIZE_MAP[size],
    className
  );

  const rootStyle = {
    ...(height !== undefined ? { height: typeof height === 'number' ? `${height}px` : String(height) } : {}),
    ...(rest.style as React.CSSProperties | undefined)
  };

  const handleSelectionChange = (keys: string[]) => {
    if (!selectedKeys) {
      setInternalSelectedKeys(keys);
    }

    if (onSelectionChange) {
      const rows = keys.map(key => {
        const index = rowKeys.indexOf(key);
        return index >= 0 ? sortedData[index] : undefined;
      }).filter(Boolean);
      onSelectionChange(keys, rows as any[]);
    }
  };

  const toggleRowSelection = (key: string) => {
    if (!isSelectable) return;
    if (isMultiSelect) {
      const exists = internalSelectedKeys.includes(key);
      const next = exists ? internalSelectedKeys.filter(k => k !== key) : [...internalSelectedKeys, key];
      handleSelectionChange(next);
    } else {
      handleSelectionChange([key]);
    }
  };

  const toggleSelectAll = () => {
    if (!isMultiSelect) return;
    const allSelected = rowKeys.length > 0 && rowKeys.every(key => internalSelectedKeys.includes(key));
    handleSelectionChange(allSelected ? [] : rowKeys);
  };

  const handleSortClick = (columnKey: string) => {
    const column = columns.find(col => col.key === columnKey);
    if (!column || column.sortable === false || !sortable) return;

    const isCurrentlySorted = activeSort?.column === columnKey;
    const nextDirection: TableSortDirection = isCurrentlySorted && activeSort?.direction === 'asc' ? 'desc' : 'asc';

    userHasInteracted.current = true;
    setInternalSort({ column: columnKey, direction: nextDirection });
    onSort?.(columnKey, nextDirection);
  };

  const getEffectiveAlign = (column: DynTableColumn): string => {
    if (column.align) return column.align;
    if (column.type === 'number' || column.type === 'currency') return 'right';
    return 'left';
  };

  const renderSelectionHeader = () => {
    if (!isSelectable) return null;
    return (
      <th className={cn(styles.cellHeader, styles.cellSelection)}>
        {isMultiSelect && (
          <DynCheckbox
            checked={rowKeys.length > 0 && rowKeys.every(key => internalSelectedKeys.includes(key))}
            onChange={toggleSelectAll}
            aria-label="Select all rows"
          />
        )}
      </th>
    );
  };

  const renderHeaderCells = () => columns.map(column => {
    const isSorted = activeSort?.column === column.key;
    const sortableColumn = sortable && column.sortable !== false;
    const align = getEffectiveAlign(column);

    return (
      <th
        key={column.key}
        className={cn(
          styles.cellHeader,
          sortableColumn && styles.cellHeaderSortable,
          isSorted && styles.cellHeaderSorted,
          styles[`cell${align.charAt(0).toUpperCase() + align.slice(1)}`]
        )}
        style={column.width ? { width: column.width } : undefined}
        onClick={sortableColumn ? () => handleSortClick(column.key) : undefined}
      >
        <div className={styles.cellContent}>
          <span>{column.title ?? column.header ?? column.key}</span>
          {sortableColumn && (
            <span className={styles.sortIndicator}>
              <DynIcon
                icon={isSorted ? (activeSort.direction === 'asc' ? 'chevron-up' : 'chevron-down') : 'chevron-down'}
                size="sm"
                style={{ opacity: isSorted ? 1 : 0.3 }}
              />
            </span>
          )}
        </div>
      </th>
    );
  });

  const renderActionsHeader = () => {
    if (!actions.length) return null;
    return <th className={cn(styles.cellHeader, styles.cellActions)}>Actions</th>;
  };

  const renderSelectionCell = (key: string) => {
    if (!isSelectable) return null;
    const checked = internalSelectedKeys.includes(key);
    return (
      <td className={cn(styles.cell, styles.cellSelection)}>
        {isMultiSelect ? (
          <DynCheckbox
            checked={checked}
            onChange={() => toggleRowSelection(key)}
            aria-label="Select row"
          />
        ) : (
          <DynRadio
            name={`${internalId}-selection`}
            value={key}
            checked={checked}
            onChange={() => toggleRowSelection(key)}
            aria-label="Select row"
          />
        )}
      </td>
    );
  };

  const renderActionsCell = (row: any, rowIndex: number) => {
    if (!actions.length) return null;
    return (
      <td className={cn(styles.cell, styles.cellActions)}>
        <div className={styles.actionsContainer}>
          {actions
            .filter(action => !action.visible || action.visible(row))
            .map(action => (
              <DynButton
                key={action.key}
                size={buttonSize}
                kind={action.type === 'primary' ? 'soft' : action.type === 'danger' ? 'secondary' : 'tertiary'}
                danger={action.type === 'danger'}
                onClick={() => action.onClick(row, rowIndex)}
                disabled={action.disabled?.(row)}
                label={action.title}
              />
            ))}
        </div>
      </td>
    );
  };

  const renderCellContent = (column: any, row: any, rowIndex: number) => {
    const value = row[column.key];
    if (column.render) return column.render(value, row, rowIndex);
    if (value == null) return '';

    switch (column.type) {
      case 'boolean':
        return (
          <DynBadge
            color={value ? 'success' : 'danger'}
            variant="dot"
            size={badgeSize}
          >
            {value ? 'Active' : 'Inactive'}
          </DynBadge>
        );
      case 'link':
        return <a href={String(value)} className={styles.cellLink}>{String(value)}</a>;
      case 'number':
        return typeof value === 'number' ? value.toLocaleString() : String(value);
      case 'currency':
        return typeof value === 'number'
          ? new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value)
          : String(value);
      case 'date':
        return new Date(value).toLocaleDateString();
      case 'datetime':
        return new Date(value).toLocaleString();
      case 'icon':
        return <DynIcon icon={String(value)} size={iconSize} />;
      default:
        return String(value);
    }
  };

  return (
    <div id={internalId} className={rootClasses} style={rootStyle} data-testid={dataTestId || 'dyn-table'}>
      <div className={styles.wrapper}>
        <table className={styles.tableContainer} {...rest}>
          <thead className={styles.head}>
            <tr className={styles.row}>
              {renderSelectionHeader()}
              {renderHeaderCells()}
              {renderActionsHeader()}
            </tr>
          </thead>
          <tbody className={styles.body}>
            {sortedData.map((row, rowIndex) => {
              const key = rowKeys[rowIndex];
              const isSelected = internalSelectedKeys.includes(key);
              return (
                <tr key={key} className={cn(styles.row, isSelected && styles.rowSelected)}>
                  {renderSelectionCell(key)}
                  {columns.map(column => {
                    const align = getEffectiveAlign(column);
                    return (
                      <td
                        key={column.key}
                        className={cn(
                          styles.cell,
                          styles[`cell${align.charAt(0).toUpperCase() + align.slice(1)}`]
                        )}
                      >
                        {renderCellContent(column, row, rowIndex)}
                      </td>
                    );
                  })}
                  {renderActionsCell(row, rowIndex)}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      {loading && (
        <div className={styles.loading}>
          <DynIcon icon="loading" spin size="lg" />
          <span>Loading...</span>
        </div>
      )}
      {!loading && sortedData.length === 0 && (
        <div className={styles.empty}>{emptyText}</div>
      )}
      {pagination && (
        <div className={styles.pagination}>
          <div className={styles.paginationControls}>
            <DynButton
              kind="secondary"
              size={buttonSize}
              disabled={pagination.current <= 1}
              onClick={() => pagination.onChange?.(pagination.current - 1, pagination.pageSize)}
              label="Previous"
            />
            <span className={styles.paginationInfo}>Page {pagination.current}</span>
            <DynButton
              kind="secondary"
              size={buttonSize}
              disabled={pagination.current >= Math.ceil(pagination.total / pagination.pageSize)}
              onClick={() => pagination.onChange?.(pagination.current + 1, pagination.pageSize)}
              label="Next"
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default DynTable;
