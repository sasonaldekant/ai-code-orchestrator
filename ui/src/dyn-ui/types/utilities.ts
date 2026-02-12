/**
 * TypeScript utility types for DYN UI
 * Strict typing utilities for enterprise-grade components
 */

// Component props with required children
export type ComponentWithChildren<T = {}> = T & {
  children: React.ReactNode;
};

// Strict event handlers
export type ClickHandler<T = HTMLElement> = (event: React.MouseEvent<T>) => void;
export type ChangeHandler<T = string> = (value: T) => void;

// CSS class names union
export type ClassName = string | string[] | Record<string, boolean> | undefined;

// Common size variants
export type Size = 'small' | 'medium' | 'large';

// Common color variants
export type ColorVariant = 'primary' | 'secondary' | 'success' | 'warning' | 'danger';

// Position types
export type Position = 'top' | 'bottom' | 'left' | 'right';

// Validation result
export type ValidationResult = {
  isValid: boolean;
  errors: string[];
};

// Loading state
export type LoadingState = 'idle' | 'loading' | 'success' | 'error';
