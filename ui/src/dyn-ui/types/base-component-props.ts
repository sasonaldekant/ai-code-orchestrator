/**
 * Base properties that all public components expose.
 * Extending this interface ensures a consistent surface area.
 */
import type { ReactNode } from 'react';

export interface BaseComponentProps {
  /** Unique identifier for the component */
  id?: string;
  /** Additional CSS class names to apply */
  className?: string;
  /** Test identifier for automated testing */
  'data-testid'?: string;
  /** Child elements to render */
  children?: ReactNode;
}
