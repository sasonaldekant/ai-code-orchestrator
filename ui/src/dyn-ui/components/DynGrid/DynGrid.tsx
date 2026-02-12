import {
  forwardRef,
  useCallback,
  useEffect,
  useId,
  useMemo,
  useState,
} from 'react';
import type { ReactNode } from 'react';
import { cn } from '../../utils/classNames';
import { DynCheckbox } from '../DynCheckbox';
import { DynRadio } from '../DynRadio';
import { DynLoading } from '../DynLoading';
import { DynButton } from '../DynButton';
import type {
  DynGridColumn,
  DynGridProps,
  DynGridSortDirection,
} from './DynGrid.types';
import { DYN_GRID_DEFAULT_PROPS } from './DynGrid.types';
import styles from './DynGrid.module.css';

const headerAlignClassMap: Record<'center' | 'right', string> = {
  center: styles.headerCellAlignCenter,
  right: styles.headerCellAlignRight,
};

const cellAlignClassMap: Record<'center' | 'right', string> = {
  center: styles.cellAlignCenter,
  right: styles.cellAlignRight,
};

const sizeClassNameMap: Record<NonNullable<DynGridProps['size']>, string | undefined> = {
  sm: styles['sizeSm'],
  md: undefined,
  lg: styles['sizeLg'],
};

const DynGrid = forwardRef<HTMLDivElement, DynGridProps>((props, ref) => {
  const {
    columns,
    data,
    loading,
    size,
    bordered,
    striped,
    hoverable,
    sortable,
    filterable,
    selectable,
    selectedKeys,
    onSelectionChange,
    onSort,
    onFilter,
    pagination,
    emptyText,
    className,
    id,
    'data-testid': dataTestId,
    ...rest
  } = props;

  // Apply defaults only when undefined
  const effectiveLoading = loading ?? DYN_GRID_DEFAULT_PROPS.loading;
  const effectiveSize = size ?? DYN_GRID_DEFAULT_PROPS.size;
  const effectiveBordered = bordered ?? DYN_GRID_DEFAULT_PROPS.bordered;
  const effectiveStriped = striped ?? DYN_GRID_DEFAULT_PROPS.striped;
  const effectiveHoverable = hoverable ?? DYN_GRID_DEFAULT_PROPS.hoverable;
  const effectiveSortable = sortable ?? DYN_GRID_DEFAULT_PROPS.sortable;
  const effectiveFilterable = filterable ?? DYN_GRID_DEFAULT_PROPS.filterable;
  const effectiveSelectable = selectable ?? DYN_GRID_DEFAULT_PROPS.selectable;
  const effectiveEmptyText = emptyText ?? DYN_GRID_DEFAULT_PROPS.emptyText;
  const effectiveDataTestId = dataTestId ?? DYN_GRID_DEFAULT_PROPS['data-testid'];

  const buttonSize = effectiveSize === 'sm' ? 'xs' : (effectiveSize === 'lg' ? 'md' : 'sm');

  const selectionName = useId();

  void effectiveFilterable;
  void onFilter;

  const selectionMode: 'none' | 'single' | 'multiple' = useMemo(() => {
    if (effectiveSelectable === 'single') {
      return 'single';
    }

    if (effectiveSelectable === 'multiple' || effectiveSelectable === true) {
      return 'multiple';
    }

    return 'none';
  }, [effectiveSelectable]);

  const [sortConfig, setSortConfig] = useState<{
    key: string;
    direction: DynGridSortDirection;
  } | null>(null);

  const resolvedSelectedKeys = useMemo(
    () => selectedKeys ?? DYN_GRID_DEFAULT_PROPS.selectedKeys,
    [selectedKeys]
  );

  const [selectedRows, setSelectedRows] = useState<string[]>(resolvedSelectedKeys);

  useEffect(() => {
    setSelectedRows(resolvedSelectedKeys);
  }, [resolvedSelectedKeys]);

  const visibleColumns = useMemo(
    () => columns.filter(column => !column.hidden),
    [columns]
  );

  const getRowKey = useCallback((record: Record<string, unknown>, index: number) => {
    const candidate =
      (record.id as string | number | undefined) ??
      (record.key as string | number | undefined) ??
      (record.rowKey as string | number | undefined);

    if (typeof candidate === 'string' || typeof candidate === 'number') {
      return String(candidate);
    }

    return index.toString();
  }, []);

  // Sort data internally if sortable is enabled
  const sortedData = useMemo(() => {
    if (!sortConfig || !effectiveSortable) {
      return data;
    }

    const sorted = [...data].sort((a, b) => {
      const aValue = a[sortConfig.key];
      const bValue = b[sortConfig.key];

      // Handle null/undefined
      if (aValue == null && bValue == null) return 0;
      if (aValue == null) return 1;
      if (bValue == null) return -1;

      // String comparison
      if (typeof aValue === 'string' && typeof bValue === 'string') {
        const comparison = aValue.localeCompare(bValue);
        return sortConfig.direction === 'asc' ? comparison : -comparison;
      }

      // Number comparison
      if (typeof aValue === 'number' && typeof bValue === 'number') {
        return sortConfig.direction === 'asc' ? aValue - bValue : bValue - aValue;
      }

      // Boolean comparison
      if (typeof aValue === 'boolean' && typeof bValue === 'boolean') {
        const comparison = aValue === bValue ? 0 : aValue ? 1 : -1;
        return sortConfig.direction === 'asc' ? comparison : -comparison;
      }

      // Date comparison
      if (aValue instanceof Date && bValue instanceof Date) {
        const comparison = aValue.getTime() - bValue.getTime();
        return sortConfig.direction === 'asc' ? comparison : -comparison;
      }

      // Fallback: convert to string
      const aStr = String(aValue);
      const bStr = String(bValue);
      const comparison = aStr.localeCompare(bStr);
      return sortConfig.direction === 'asc' ? comparison : -comparison;
    });

    return sorted;
  }, [data, sortConfig, effectiveSortable]);

  const handleSort = useCallback(
    (columnKey: string) => {
      if (!effectiveSortable) {
        return;
      }

      const column = visibleColumns.find(col => col.key === columnKey);
      if (!column?.sortable) {
        return;
      }

      let direction: DynGridSortDirection = 'asc';

      if (sortConfig?.key === columnKey && sortConfig.direction === 'asc') {
        direction = 'desc';
      }

      setSortConfig({ key: columnKey, direction });
      onSort?.(columnKey, direction);
    },
    [effectiveSortable, visibleColumns, sortConfig, onSort]
  );

  const getSelectedRowData = useCallback(
    (keys: string[]): Record<string, unknown>[] =>
      keys
        .map(key => {
          const rowIndex = sortedData.findIndex((record, index) => getRowKey(record, index) === key);
          return rowIndex >= 0 ? sortedData[rowIndex] : undefined;
        })
        .filter((record): record is Record<string, unknown> => Boolean(record)),
    [sortedData, getRowKey]
  );

  const handleRowSelect = useCallback(
    (rowKey: string, selected: boolean) => {
      if (selectionMode === 'none') {
        return;
      }

      let newSelection: string[];

      if (selectionMode === 'single') {
        newSelection = selected ? [rowKey] : [];
      } else {
        newSelection = selected
          ? [...new Set([...selectedRows, rowKey])]
          : selectedRows.filter(key => key !== rowKey);
      }

      setSelectedRows(newSelection);
      onSelectionChange?.(newSelection, getSelectedRowData(newSelection));
    },
    [selectionMode, selectedRows, onSelectionChange, getSelectedRowData]
  );

  const handleSelectAll = useCallback(
    (selected: boolean) => {
      if (selectionMode !== 'multiple') {
        return;
      }

      const allKeys = sortedData.map((record, index) => getRowKey(record, index));
      const newSelection = selected ? allKeys : [];

      setSelectedRows(newSelection);
      onSelectionChange?.(newSelection, selected ? sortedData : []);
    },
    [selectionMode, sortedData, getRowKey, onSelectionChange]
  );

  const renderCell = useCallback(
    (column: DynGridColumn, record: Record<string, unknown>, rowIndex: number) => {
      if (column.render) {
        return column.render(record[column.key], record, rowIndex);
      }

      return record[column.key] as ReactNode;
    },
    []
  );

  const isAllSelected = useMemo(() => {
    if (selectionMode !== 'multiple' || sortedData.length === 0) {
      return false;
    }

    const allKeys = sortedData.map((record, index) => getRowKey(record, index));
    return allKeys.every(key => selectedRows.includes(key));
  }, [selectionMode, sortedData, getRowKey, selectedRows]);

  const isSelectionIndeterminate = useMemo(() => {
    if (selectionMode !== 'multiple' || sortedData.length === 0) {
      return false;
    }

    const selectedCount = sortedData.filter((record, index) => selectedRows.includes(getRowKey(record, index))).length;
    return selectedCount > 0 && selectedCount < sortedData.length;
  }, [selectionMode, sortedData, getRowKey, selectedRows]);

  const totalPages = pagination ? Math.ceil(pagination.total / pagination.pageSize) : 1;
  const canGoPrevious = pagination ? pagination.current > 1 : false;
  const canGoNext = pagination ? pagination.current < totalPages : false;

  const handlePageChange = useCallback(
    (newPage: number) => {
      if (!pagination?.onChange) return;
      pagination.onChange(newPage, pagination.pageSize);
    },
    [pagination]
  );

  const gridClassName = cn(
    styles.root,
    sizeClassNameMap[effectiveSize],
    effectiveBordered && styles.bordered,
    effectiveStriped && styles.striped,
    effectiveHoverable && styles.hoverable,
    effectiveLoading && styles.loading,
    className
  );

  if (effectiveLoading) {
    return (
      <div ref={ref} className={gridClassName} id={id} data-testid={effectiveDataTestId} {...rest}>
        <div className={styles.loadingState}>
          <DynLoading
            variant="spinner"
            size="lg"
            label="Loading data…"
            color="primary"
          />
        </div>
      </div>
    );
  }

  if (sortedData.length === 0) {
    return (
      <div ref={ref} className={gridClassName} id={id} data-testid={effectiveDataTestId} {...rest}>
        <div className={styles.emptyState}>
          {typeof effectiveEmptyText === 'string' ? (
            <span>{effectiveEmptyText}</span>
          ) : (
            effectiveEmptyText
          )}
        </div>
      </div>
    );
  }

  return (
    <div ref={ref} className={gridClassName} id={id} data-testid={effectiveDataTestId} {...rest}>
      <div className={styles.wrapper}>
        <table className={styles.table} role="table">
          <thead className={styles.header}>
            <tr className={styles.headerRow}>
              {selectionMode === 'multiple' && (
                <th className={cn(styles.headerCell, styles.selectionCell)} scope="col">
                  <DynCheckbox
                    checked={isAllSelected}
                    indeterminate={isSelectionIndeterminate}
                    onChange={checked => handleSelectAll(checked)}
                    aria-label="Select all rows"
                  />
                </th>
              )}
              {visibleColumns.map(column => {
                const isSorted = sortConfig?.key === column.key;
                const direction = isSorted ? sortConfig?.direction : undefined;
                const headerAlignmentClass =
                  column.align && column.align !== 'left'
                    ? headerAlignClassMap[column.align]
                    : undefined;

                return (
                  <th
                    key={column.key}
                    className={cn(
                      styles.headerCell,
                      headerAlignmentClass,
                      column.sortable && effectiveSortable && styles.headerCellSortable,
                      isSorted && styles.headerCellSorted
                    )}
                    style={{ width: column.width, minWidth: column.minWidth }}
                    onClick={() => column.sortable && handleSort(column.key)}
                    aria-sort={
                      column.sortable && effectiveSortable
                        ? direction === 'asc'
                          ? 'ascending'
                          : direction === 'desc'
                            ? 'descending'
                            : 'none'
                        : undefined
                    }
                    scope="col"
                  >
                    <div className={styles.headerContent}>
                      <span>{column.title}</span>
                      {column.sortable && effectiveSortable && (
                        <span className={styles.sortIndicator} aria-hidden="true">
                          {isSorted ? (direction === 'asc' ? '↑' : '↓') : '↕'}
                        </span>
                      )}
                    </div>
                  </th>
                );
              })}
            </tr>
          </thead>
          <tbody className={styles.body}>
            {sortedData.map((record, rowIndex) => {
              const rowKey = getRowKey(record, rowIndex);
              const isSelected = selectedRows.includes(rowKey);

              return (
                <tr
                  key={rowKey}
                  className={cn(
                    styles.row,
                    rowIndex % 2 === 0 ? styles.rowEven : styles.rowOdd,
                    isSelected && styles.rowSelected
                  )}
                  role="row"
                >
                  {selectionMode !== 'none' && (
                    <td className={cn(styles.cell, styles.selectionCell)}>
                      {selectionMode === 'single' ? (
                        <DynRadio
                          name={selectionName}
                          value={rowKey}
                          checked={isSelected}
                          onChange={checked => checked && handleRowSelect(rowKey, true)}
                          aria-label={`Select row ${rowIndex + 1}`}
                        />
                      ) : (
                        <DynCheckbox
                          checked={isSelected}
                          onChange={checked => handleRowSelect(rowKey, checked)}
                          aria-label={`Select row ${rowIndex + 1}`}
                        />
                      )}
                    </td>
                  )}
                  {visibleColumns.map(column => (
                    <td
                      key={column.key}
                      className={cn(
                        styles.cell,
                        column.align && column.align !== 'left'
                          ? cellAlignClassMap[column.align]
                          : undefined
                      )}
                    >
                      {renderCell(column, record, rowIndex)}
                    </td>
                  ))}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {pagination && (
        <div className={styles.pagination} role="navigation" aria-label="Table pagination">
          <div className={styles.paginationInfo}>
            {pagination.showTotal?.(
              pagination.total,
              [
                (pagination.current - 1) * pagination.pageSize + 1,
                Math.min(pagination.current * pagination.pageSize, pagination.total),
              ]
            )}
          </div>
          <div className={styles.paginationControls}>
            <DynButton
              kind="secondary"
              size={buttonSize}
              onClick={() => handlePageChange(1)}
              disabled={!canGoPrevious}
              aria-label="First page"
            >
              «
            </DynButton>
            <DynButton
              kind="secondary"
              size={buttonSize}
              onClick={() => handlePageChange(pagination.current - 1)}
              disabled={!canGoPrevious}
              aria-label="Previous page"
            >
              ‹
            </DynButton>
            <span className={styles.paginationText}>
              Page {pagination.current} of {totalPages}
            </span>
            <DynButton
              kind="secondary"
              size={buttonSize}
              onClick={() => handlePageChange(pagination.current + 1)}
              disabled={!canGoNext}
              aria-label="Next page"
            >
              ›
            </DynButton>
            <DynButton
              kind="secondary"
              size={buttonSize}
              onClick={() => handlePageChange(totalPages)}
              disabled={!canGoNext}
              aria-label="Last page"
            >
              »
            </DynButton>
          </div>
        </div>
      )}
    </div>
  );
});

DynGrid.displayName = 'DynGrid';

export { DynGrid };
export default DynGrid;
