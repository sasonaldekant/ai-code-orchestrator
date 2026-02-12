import * as React from 'react';

export type Theme = 'light' | 'dark';

export type ThemeContextValue = {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  availableThemes: Theme[];
};

export const ThemeContext = React.createContext<ThemeContextValue | null>(null);

export type ThemeProviderProps = {
  initialTheme?: Theme;
  children: React.ReactNode;
};

const AVAILABLE_THEMES: Theme[] = ['light', 'dark'];

export function ThemeProvider({ initialTheme = 'light', children }: ThemeProviderProps) {
  const [theme, setThemeState] = React.useState<Theme>(initialTheme);

  const setTheme = React.useCallback((newTheme: Theme) => {
    if (AVAILABLE_THEMES.includes(newTheme)) {
      setThemeState(newTheme);
    }
  }, []);

  // Apply theme to document when theme changes
  React.useEffect(() => {
    const root = document.documentElement;
    
    // Remove existing theme classes
    AVAILABLE_THEMES.forEach(t => {
      root.classList.remove(`theme-${t}`);
    });
    
    // Add new theme class
    root.classList.add(`theme-${theme}`);
    
    // Set data attribute for CSS selector support
    root.setAttribute('data-theme', theme);
  }, [theme]);

  // Set initial theme on mount
  React.useEffect(() => {
    setTheme(initialTheme);
  }, [initialTheme, setTheme]);

  const contextValue = React.useMemo(() => ({
    theme,
    setTheme,
    availableThemes: AVAILABLE_THEMES,
  }), [theme, setTheme]);

  return (
    <ThemeContext.Provider value={contextValue}>
      {children}
    </ThemeContext.Provider>
  );
}

export const useTheme = () => {
  const context = React.useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};