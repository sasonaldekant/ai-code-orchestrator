/**
 * DynStepper TypeScript type definitions
 * Complete step navigation component types with advanced progression features
 */

import type { BaseComponentProps, AccessibilityProps } from '../../types';

// Enhanced Step interface with all required properties
export interface StepItem {
  id: string;
  title?: string;
  label?: string; // alias for title
  content?: React.ReactNode | ((props: { index: number; selected: boolean }) => React.ReactNode);
  description?: string;
  icon?: string | React.ReactNode;
  disabled?: boolean;
  completed?: boolean;
  error?: boolean;
  optional?: boolean;
  tooltip?: string;
  status?: 'inactive' | 'active' | 'completed' | 'error' | 'disabled';
  validator?: (step: StepItem) => boolean; // Custom validation function
  state?: 'pending' | 'active' | 'completed' | 'error'; // Alternative to status
}

// Complete DynStepperProps interface
export interface DynStepperProps extends BaseComponentProps, AccessibilityProps {
  /** 
   * Array of step configurations. 
   * Each item defines titles, icons, and the content/logic for that specific step.
   */
  steps: StepItem[];

  /** 
   * Current active step identifier (id or index). 
   * Use this for controlled components where you manage the state externally.
   * @deprecated Use activeStep for numeric indexing.
   */
  value?: string | number;

  /** 
   * Initial active step identifier for uncontrolled components.
   * @deprecated Use defaultActiveStep for numeric indexing.
   */
  defaultValue?: string | number;

  /** 
   * The 0-based index of the currently active step. 
   * This is the preferred way to control the stepper in modern implementations.
   */
  activeStep?: number;

  /** The 0-based index of the step that should be active by default. */
  defaultActiveStep?: number;

  /** 
   * Callback triggered when the active step changes.
   * Provides the new value, the full step object, and the index.
   */
  onChange?: (value: string | number, step: StepItem, index: number) => void;

  /** 
   * The visual flow direction of the step indicators.
   * @default 'horizontal'
   */
  orientation?: 'horizontal' | 'vertical';

  /** 
   * Visual theme for the step indicators.
   * - 'numbered': Traditional 1, 2, 3 circles.
   * - 'dots': Clean bullet points.
   * - 'progress': Continuous bar.
   * - 'tabs': Tab-like buttons.
   * @default 'numbered'
   */
  variant?: 'default' | 'numbered' | 'dots' | 'progress' | 'tabs';

  /** 
   * Vertical density and item scaling.
   * @default 'md'
   */
  size?: 'sm' | 'md' | 'lg';

  /** 
   * If true, users must complete steps in sequential order. 
   * Navigation to future steps (beyond current + 1) is blocked.
   * @default true
   */
  linear?: boolean;

  /** If true, step titles are displayed alongside icons/numbers. */
  showLabels?: boolean;

  /** If true, step description text is displayed below the titles. */
  showDescription?: boolean;

  /** If true, users can click on step headers to navigate (subject to linear constraints). */
  clickableSteps?: boolean;

  /** Custom CSS class for the root container. */
  className?: string;

  /** Custom CSS class applied to each individual step indicator. */
  stepClassName?: string;

  /** Custom CSS class for the container holding the step content panels. */
  contentClassName?: string;

  /** 
   * Callback triggered when active step changes (Legacy support). 
   * @deprecated Use onChange instead.
   */
  onStepChange?: (step: number, stepData: StepItem) => void;

  /** 
   * Callback triggered when a step is clicked. 
   * Return `false` to prevent the navigation from happening.
   */
  onStepClick?: (step: number, stepData: StepItem) => boolean | void;

  /** 
   * Higher-order function to override how the main content of a step is rendered.
   * Useful for adding global wrappers like animations or context providers to all steps.
   */
  renderStepContent?: (step: StepItem, index: number) => React.ReactNode;

  /** 
   * Function to provide a custom icon element for the step header.
   * Overrides both default numbers and the item's `icon` property.
   */
  renderStepIcon?: (step: StepItem, index: number, isActive: boolean) => React.ReactNode;

  /** Unique identifier for the component. */
  id?: string;

  /** Accessibility label for the stepper group. */
  'aria-label'?: string;

  /** ID of an element that labels this stepper group. */
  'aria-labelledby'?: string;

  /** Identifier used specifically for automated testing. */
  'data-testid'?: string;
}

// Complete DynStepperRef interface with proper return types
export interface DynStepperRef {
  /** Navigate to next step - returns success status */
  nextStep: () => boolean;

  /** Navigate to previous step - returns success status */
  prevStep: () => boolean;

  /** Navigate to specific step - returns success status */
  goToStep: (step: number) => boolean;

  /** Get current active step index */
  getCurrentStep: () => number;

  /** Get step data by index */
  getStepData: (step: number) => StepItem | undefined;

  /** Validate step by index */
  validateStep: (step: number) => boolean;

  /** Mark step as completed */
  completeStep: (step: number) => void;

  /** Set error state for step */
  errorStep: (step: number, hasError: boolean) => void;
}

// Legacy aliases for backward compatibility
export type DynStepperHandle = DynStepperRef;
export type DynStep = StepItem;

// Step interface alias (matching test expectations)
export interface Step extends StepItem { }

// Default configuration
export const STEPPER_DEFAULTS = {
  orientation: 'horizontal' as const,
  variant: 'numbered' as const,
  size: 'md' as const,
  linear: true,
  showLabels: true,
  showDescription: false,
  clickableSteps: true,
  defaultActiveStep: 0
};

// Step variants
export const STEPPER_VARIANTS = {
  DEFAULT: 'default',
  NUMBERED: 'numbered',
  DOTS: 'dots',
  PROGRESS: 'progress',
  TABS: 'tabs'
} as const;

// Step orientations
export const STEPPER_ORIENTATIONS = {
  HORIZONTAL: 'horizontal',
  VERTICAL: 'vertical'
} as const;

// Step states
export const STEP_STATES = {
  INACTIVE: 'inactive',
  ACTIVE: 'active',
  COMPLETED: 'completed',
  ERROR: 'error',
  DISABLED: 'disabled',
  PENDING: 'pending'
} as const;

export type StepState = typeof STEP_STATES[keyof typeof STEP_STATES];

// Step sizes
export const STEPPER_SIZES = {
  SMALL: 'sm',
  MEDIUM: 'md',
  LARGE: 'lg'
} as const;

export type StepperSize = typeof STEPPER_SIZES[keyof typeof STEPPER_SIZES];

// Component validation
export interface StepValidation {
  required?: boolean;
  validator?: (step: StepItem) => boolean | string;
  message?: string;
}

// Event handlers
export interface StepEventHandlers {
  onNext?: (currentStep: number, stepData: StepItem) => boolean | void;
  onPrevious?: (currentStep: number, stepData: StepItem) => boolean | void;
  onComplete?: (steps: StepItem[]) => void;
  onValidationError?: (step: number, error: string) => void;
}

// Extended props for advanced usage
export interface DynStepperAdvancedProps extends DynStepperProps, StepEventHandlers {
  /** Enable step validation */
  enableValidation?: boolean;

  /** Show progress indicator */
  showProgress?: boolean;

  /** Animation type */
  animation?: 'none' | 'fade' | 'slide';

  /** Allow step skipping in linear mode */
  allowSkipping?: boolean;

  /** Persist step state */
  persistState?: boolean;

  /** Storage key for persistence */
  storageKey?: string;
}