import * as React from 'react';

export interface ThemeContextValue {
  theme: string;
  setTheme: (theme: string) => void;
  availableThemes: string[];
}

const ThemeContext = React.createContext<ThemeContextValue | null>(null);

export interface ThemeProviderProps {
  initialTheme?: string;
  children: React.ReactNode;
}

const AVAILABLE_THEMES = ['light', 'dark'];

export function ThemeProvider({ initialTheme = 'light', children }: ThemeProviderProps) {
  const [theme, setThemeState] = React.useState(initialTheme);

  const setTheme = React.useCallback((newTheme: string) => {
    if (AVAILABLE_THEMES.includes(newTheme)) {
      setThemeState(newTheme);
      // Apply theme to document
      const root = document.documentElement;
      root.setAttribute('data-theme', newTheme);
      root.classList.remove('theme-light', 'theme-dark');
      root.classList.add(`theme-${newTheme}`);
    }
  }, []);

  // Set initial theme on mount
  React.useEffect(() => {
    setTheme(theme);
  }, []); // Only run on mount

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

export function useTheme(): ThemeContextValue {
  const context = React.useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}