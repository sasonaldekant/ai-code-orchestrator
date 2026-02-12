/**
 * Data Display Components Types - SCOPE 8
 * Advanced components for displaying complex data structures
 */

export type LayoutSize = 'small' | 'medium' | 'large';
export type LayoutSpacing = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

// Table Types
export type TableColumnType = 
  | 'text' 
  | 'number' 
  | 'boolean' 
  | 'date' 
  | 'time' 
  | 'datetime' 
  | 'currency' 
  | 'link' 
  | 'icon' 
  | 'custom';

export type TableSortDirection = 'asc' | 'desc';

export interface DynTableColumn {
  key: string;
  title: string;
  width?: string | number;
  type?: TableColumnType;
  sortable?: boolean;
  filterable?: boolean;
  align?: 'left' | 'center' | 'right';
  render?: (value: any, row: any, index: number) => React.ReactNode;
  tooltip?: string;
  fixed?: boolean;
}

export interface DynTableAction {
  key: string;
  title: string;
  icon?: string;
  type?: 'default' | 'primary' | 'danger';
  disabled?: (row: any) => boolean;
  visible?: (row: any) => boolean;
  onClick: (row: any, index: number) => void;
}

export interface DynTableProps {
  data: any[];
  columns: DynTableColumn[];
  actions?: DynTableAction[];
  loading?: boolean;
  size?: LayoutSize;
  bordered?: boolean;
  striped?: boolean;
  hoverable?: boolean;
  selectable?: boolean | 'single' | 'multiple';
  selectedKeys?: string[];
  rowKey?: string | ((row: any) => string);
  pagination?: {
    current: number;
    pageSize: number;
    total: number;
    showSizeChanger?: boolean;
    showQuickJumper?: boolean;
    onChange?: (page: number, pageSize?: number) => void;
  };
  sortBy?: {
    column: string;
    direction: TableSortDirection;
  };
  onSort?: (column: string, direction: TableSortDirection) => void;
  onSelectionChange?: (keys: string[], rows: any[]) => void;
  emptyText?: React.ReactNode;
  height?: number;
  className?: string;
}

// List View Types
export interface DynListViewAction {
  key: string;
  title: string;
  icon?: string;
  type?: 'default' | 'primary' | 'danger';
  disabled?: (item: any) => boolean;
  visible?: (item: any) => boolean;
  onClick: (item: any, index: number) => void;
}

export interface DynListViewProps {
  data: any[];
  actions?: DynListViewAction[];
  loading?: boolean;
  size?: LayoutSize;
  bordered?: boolean;
  selectable?: boolean;
  selectedKeys?: string[];
  itemKey?: string | ((item: any) => string);
  renderItem?: (item: any, index: number) => React.ReactNode;
  onSelectionChange?: (keys: string[], items: any[]) => void;
  emptyText?: React.ReactNode;
  height?: number;
  className?: string;
}

// Tree View Types
export interface DynTreeNode {
  key: string;
  title: string;
  icon?: string;
  disabled?: boolean;
  checkable?: boolean;
  selectable?: boolean;
  children?: DynTreeNode[];
  data?: any; // Additional data attached to node
}

export interface DynTreeViewProps {
  treeData: DynTreeNode[];
  checkable?: boolean;
  selectable?: boolean;
  multiple?: boolean;
  expandedKeys?: string[];
  checkedKeys?: string[];
  selectedKeys?: string[];
  defaultExpandAll?: boolean;
  showIcon?: boolean;
  showLine?: boolean;
  searchable?: boolean;
  onExpand?: (expandedKeys: string[]) => void;
  onCheck?: (checkedKeys: string[], info: { checked: boolean; node: DynTreeNode }) => void;
  onSelect?: (selectedKeys: string[], info: { selected: boolean; node: DynTreeNode }) => void;
  onSearch?: (value: string) => void;
  height?: number;
  className?: string;
}

// Chart Types
export type ChartType = 'line' | 'bar' | 'pie' | 'area' | 'scatter';

export interface ChartDataPoint {
  label: string;
  value: number;
  color?: string;
  [key: string]: any;
}

export interface ChartSeries {
  name: string;
  data: ChartDataPoint[];
  color?: string;
  type?: ChartType;
}

export interface DynChartProps {
  type: ChartType;
  data: ChartSeries[] | ChartDataPoint[];
  title?: string;
  subtitle?: string;
  width?: number;
  height?: number;
  colors?: string[];
  showLegend?: boolean;
  showTooltip?: boolean;
  showGrid?: boolean;
  xAxis?: {
    title?: string;
    categories?: string[];
  };
  yAxis?: {
    title?: string;
    min?: number;
    max?: number;
  };
  options?: any; // Additional chart options
  className?: string;
}

// Gauge Types
export interface GaugeRange {
  from: number;
  to: number;
  color: string;
  label?: string;
}

export interface DynGaugeProps {
  value: number;
  min?: number;
  max?: number;
  title?: string;
  subtitle?: string;
  unit?: string;
  ranges?: GaugeRange[];
  showValue?: boolean;
  showRanges?: boolean;
  size?: LayoutSize;
  thickness?: number;
  rounded?: boolean;
  animated?: boolean;
  color?: string;
  backgroundColor?: string;
  className?: string;
  format?: (value: number) => string;
}

// Common Data Display Types
export interface DataDisplayLiterals {
  loading: string;
  empty: string;
  noData: string;
  selectAll: string;
  selected: string;
  total: string;
  page: string;
  of: string;
  itemsPerPage: string;
  search: string;
  filter: string;
  sort: string;
  expand: string;
  collapse: string;
  actions: string;
}

export interface PaginationConfig {
  current: number;
  pageSize: number;
  total: number;
  showSizeChanger?: boolean;
  showQuickJumper?: boolean;
  showTotal?: boolean;
  pageSizeOptions?: number[];
  onChange?: (page: number, pageSize?: number) => void;
  onShowSizeChange?: (current: number, size: number) => void;
}

export interface SortConfig {
  column: string;
  direction: TableSortDirection;
}

export interface FilterConfig {
  column: string;
  value: any;
  operator?: 'eq' | 'ne' | 'gt' | 'gte' | 'lt' | 'lte' | 'contains' | 'startsWith' | 'endsWith';
}

export interface SelectionConfig {
  type: 'single' | 'multiple';
  rowKey: string | ((row: any) => string);
  selectedKeys: string[];
  onChange: (keys: string[], rows: any[]) => void;
}