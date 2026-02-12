// Global counters for different component types to ensure unique IDs
const counters = new Map<string, number>();

/**
 * Generates a unique ID for a component with the given prefix.
 * Uses separate counters for different prefixes to ensure uniqueness.
 * 
 * @param prefix - The prefix to use for the ID (e.g., 'button', 'input')
 * @returns A unique ID string
 */
export const generateId = (prefix: string = 'dyn-id'): string => {
  const currentCount = counters.get(prefix) || 0;
  const nextCount = currentCount + 1;
  counters.set(prefix, nextCount);
  return `${prefix}-${nextCount}`;
};

/**
 * Resets all ID counters. Primarily used for testing purposes.
 * 
 * @internal
 */
export const resetIdCounters = (): void => {
  counters.clear();
};
