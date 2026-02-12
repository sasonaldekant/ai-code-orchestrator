/**
 * Enhanced classNames utility - TypeScript compatible version
 * Optimized for DYN UI components with CSS Module support
 */

type ClassNameValue = string | number | boolean | null | undefined;

type ClassNameArg = 
  | ClassNameValue
  | Record<string, ClassNameValue>
  | ClassNameArg[];

/**
 * Concatenates class names conditionally
 * Built-in implementation compatible with all environments
 * @param args - Array of class name arguments
 * @returns Concatenated class name string
 * 
 * @example
 * ```typescript
 * // Basic usage
 * classNames('btn', 'btn-primary'); // 'btn btn-primary'
 * 
 * // Conditional classes
 * classNames('btn', {
 *   'btn-primary': isPrimary,
 *   'btn-disabled': isDisabled
 * }); // 'btn btn-primary' (if isPrimary is true)
 * 
 * // CSS Modules support
 * classNames(styles.button, styles.primary, {
 *   [styles.loading]: isLoading
 * });
 * ```
 */
export function classNames(...args: ClassNameArg[]): string {
  const classes: string[] = [];

  for (const arg of args) {
    if (!arg) continue;

    if (typeof arg === 'string' || typeof arg === 'number') {
      classes.push(String(arg));
    } else if (Array.isArray(arg)) {
      const nested = classNames(...arg);
      if (nested) classes.push(nested);
    } else if (typeof arg === 'object') {
      for (const [key, value] of Object.entries(arg)) {
        if (value) classes.push(key);
      }
    }
  }

  return classes.join(' ');
}

/**
 * Shorter alias for classNames
 */
export const cn = classNames;

/**
 * Creates a CSS module class name generator
 * @param styles - CSS module styles object
 * @returns Function that maps class names to CSS module classes
 * 
 * @example
 * ```typescript
 * import { styles } from './Button.module.css';
 * const cx = createClassNameGenerator(styles);
 * 
 * const buttonClasses = cx('button', {
 *   primary: kind === 'primary',
 *   loading: isLoading
 * });
 * ```
 */
export function createClassNameGenerator(styles: Record<string, string>) {
  return (...args: ClassNameArg[]) => {
    const className = classNames(...args);
    return className
      .split(' ')
      .map(cls => styles[cls] || cls)
      .join(' ');
  };
}

/**
 * CSS Module helper - combines CSS Module styles with additional classes
 * Provides type safety for CSS Module objects
 * 
 * @param styles - CSS Module styles object
 * @param baseClass - Base class name from styles
 * @param additionalClasses - Additional classes to combine
 * @returns Combined class names
 * 
 * @example
 * ```typescript
 * import { styles } from './Button.module.css';
 * 
 * const buttonClasses = combineStyles(styles, 'button', {
 *   [styles.primary]: kind === 'primary',
 *   [styles.loading]: isLoading,
 *   'external-class': hasExternalClass
 * });
 * ```
 */
export function combineStyles(
  styles: Record<string, string>,
  baseClass: keyof typeof styles,
  additionalClasses?: ClassNameArg
): string {
  return classNames(styles[baseClass], additionalClasses);
}

/**
 * Combines base classes with conditional classes
 * @param baseClasses - Always applied classes
 * @param conditionalClasses - Conditionally applied classes
 * @returns Combined class name string
 */
export function combineClasses(
  baseClasses: string,
  conditionalClasses?: ClassNameArg
): string {
  return classNames(baseClasses, conditionalClasses);
}

/**
 * Conditional class helper - applies class only if condition is true
 * 
 * @param className - Class name to apply
 * @param condition - Condition to evaluate
 * @returns Class name if condition is true, empty string otherwise
 * 
 * @example
 * ```typescript
 * const classes = classNames(
 *   'btn',
 *   conditionalClass('btn-loading', isLoading),
 *   conditionalClass('btn-disabled', isDisabled)
 * );
 * ```
 */
export function conditionalClass(className: string, condition: boolean): string {
  return condition ? className : '';
}

/**
 * Variant class helper - applies variant class with prefix
 * Useful for consistent variant naming in design systems
 * 
 * @param prefix - Prefix for the variant class
 * @param variant - Variant name
 * @param condition - Optional condition (defaults to true)
 * @returns Prefixed variant class name
 * 
 * @example
 * ```typescript
 * const classes = classNames(
 *   'btn',
 *   variantClass('btn', 'primary'), // 'btn-primary'
 *   variantClass('btn', 'large', size === 'large') // 'btn-large' if condition is true
 * );
 * ```
 */
export function variantClass(
  prefix: string,
  variant: string,
  condition: boolean = true
): string {
  return condition ? `${prefix}-${variant}` : '';
}

/**
 * Size class helper - converts size tokens to class names
 * Supports both full names and abbreviations for optimized bundle size
 * 
 * @param prefix - Prefix for the size class
 * @param size - Size token ('small', 'medium', 'large' or 's', 'm', 'l')
 * @param useAbbreviation - Whether to use abbreviated size names
 * @returns Size class name
 * 
 * @example
 * ```typescript
 * sizeClass('btn', 'medium'); // 'btn-medium'
 * sizeClass('btn', 'medium', true); // 'btn-m'
 * sizeClass('btn', 'large'); // 'btn-large'
 * sizeClass('btn', 'large', true); // 'btn-l'
 * ```
 */
export function sizeClass(
  prefix: string,
  size: 'small' | 'medium' | 'large' | 's' | 'm' | 'l',
  useAbbreviation: boolean = false
): string {
  const sizeMap = {
    small: useAbbreviation ? 's' : 'small',
    medium: useAbbreviation ? 'm' : 'medium',
    large: useAbbreviation ? 'l' : 'large',
    s: 's',
    m: 'm',
    l: 'l'
  };
  
  const mappedSize = sizeMap[size];
  return `${prefix}-${mappedSize}`;
}