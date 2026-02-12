import React from 'react';
import { cn } from '../../utils/classNames';
import { DynButton } from '../DynButton';
import { DynIcon } from '../DynIcon';
import { DynLoading } from '../DynLoading';
import type { DynButtonKind } from '../DynButton/DynButton.types';
import type { DynPageProps } from './DynPage.types';
import styles from './DynPage.module.css';

export const DynPage: React.FC<DynPageProps> = ({
  title,
  subtitle,
  breadcrumbs = [],
  actions = [],
  children,
  loading = false,
  error,
  size = 'md',
  padding = 'md',
  background = 'page',
  className,
  id,
  'data-testid': testId
}) => {
  const pageClasses = cn(
    styles.container,
    size === 'sm' && styles['sizeSm'],
    size === 'md' && styles['sizeMd'],
    size === 'lg' && styles['sizeLg'],
    padding === 'none' && styles.paddingNone,
    padding === 'xs' && styles.paddingXs,
    padding === 'sm' && styles.paddingSm,
    padding === 'md' && styles.paddingMd,
    padding === 'lg' && styles.paddingLg,
    background === 'none' && styles.backgroundNone,
    background === 'surface' && styles.backgroundSurface,
    background === 'page' && styles.backgroundPage,
    {
      [styles.loading]: loading,
      [styles.error]: !!error
    },
    className
  );

  const renderBreadcrumbs = () => {
    if (breadcrumbs.length === 0) return null;

    return (
      <nav className={styles.breadcrumbs} aria-label="Breadcrumb">
        <ol className={styles.breadcrumbList}>
          {breadcrumbs.map((breadcrumb, index) => (
            <li key={index} className={styles.breadcrumbItem}>
              {breadcrumb.href ? (
                <a
                  href={breadcrumb.href}
                  className={styles.breadcrumbLink}
                >
                  {breadcrumb.title}
                </a>
              ) : breadcrumb.onClick ? (
                <button
                  type="button"
                  onClick={breadcrumb.onClick}
                  className={styles.breadcrumbLink}
                >
                  {breadcrumb.title}
                </button>
              ) : (
                <span className={styles.breadcrumbText}>{breadcrumb.title}</span>
              )}
              {index < breadcrumbs.length - 1 && (
                <span className={styles.breadcrumbSeparator} aria-hidden="true">
                  <DynIcon icon="chevron-right" size="sm" />
                </span>
              )}
            </li>
          ))}
        </ol>
      </nav>
    );
  };

  const renderActions = () => {
    if (actions.length === 0) return null;

    return (
      <div className={styles.actions}>
        {actions.map((action) => (
          <DynButton
            key={action.key}
            kind={(action.type ?? 'secondary') as DynButtonKind}
            size={size === 'lg' ? 'lg' : 'md'}
            disabled={action.disabled}
            loading={action.loading}
            onClick={action.onClick}
            icon={action.icon}
          >
            {action.title}
          </DynButton>
        ))}
      </div>
    );
  };

  if (loading) {
    return (
      <div className={pageClasses} id={id} data-testid={testId}>
        <div className={styles.loadingContainer}>
          <DynLoading
            variant="spinner"
            size="lg"
            label="Loading page..."
            color="primary"
          />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={pageClasses} id={id} data-testid={testId}>
        <div className={styles.errorContainer}>
          <div className={styles.errorIcon}>
            <DynIcon icon="warning" size="lg" />
          </div>
          <div className={styles.errorContent}>
            {typeof error === 'string' ? (
              <span className={styles.errorMessage}>{error}</span>
            ) : (
              error
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={pageClasses} id={id} data-testid={testId}>
      <header className={styles.header}>
        {renderBreadcrumbs()}

        <div className={styles.titleSection}>
          <div className={styles.titleContent}>
            <h1 className={styles.headerTitle}>{title}</h1>
            {subtitle && (
              <p className={styles.headerSubtitle}>{subtitle}</p>
            )}
          </div>
          {renderActions()}
        </div>
      </header>

      <main className={styles.content}>
        {children}
      </main>
    </div>
  );
};


DynPage.displayName = 'DynPage';

export default DynPage;
