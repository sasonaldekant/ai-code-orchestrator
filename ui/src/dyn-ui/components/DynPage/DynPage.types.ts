import type { ReactNode } from 'react';
import type { BaseComponentProps } from '../../types/theme';
import type { LayoutSize, LayoutSpacing } from '../../types/layout.types';

export interface DynPageBreadcrumb {
  title: string;
  href?: string;
  onClick?: () => void;
}

export interface DynPageAction {
  key: string;
  title: string;
  icon?: string;
  type?: 'primary' | 'secondary' | 'danger';
  onClick: () => void;
  disabled?: boolean;
  loading?: boolean;
}

export interface DynPageProps extends BaseComponentProps {
  title: string;
  subtitle?: string;
  breadcrumbs?: DynPageBreadcrumb[];
  actions?: DynPageAction[];
  children: ReactNode;
  loading?: boolean;
  error?: string | ReactNode;
  size?: LayoutSize;
  padding?: LayoutSpacing;
  background?: 'none' | 'surface' | 'page';
}
