import { useContext } from 'react';
import { ThemeContext } from '../theme/ThemeProvider';
import type { ThemeContextValue } from '../theme/ThemeProvider';

/**
 * Hook for accessing theme context
 * @returns Theme context value with current theme and theme utilities
 */
export const useTheme = (): ThemeContextValue => {
  const context = useContext(ThemeContext);
  
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  
  return context;
};

/**
 * Hook for getting CSS custom properties from current theme
 * @returns Object with CSS custom properties for current theme
 */
export const useThemeVars = () => {
  const { theme } = useTheme();
  
  const cssVars: Record<string, string> = {};
  
  // Basic theme variables
  cssVars['--theme-name'] = theme;
  cssVars['--theme-mode'] = theme === 'dark' ? 'dark' : 'light';
  
  return cssVars;
};