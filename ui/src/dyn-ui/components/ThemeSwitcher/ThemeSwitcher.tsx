import * as React from 'react';
import { useTheme, type Theme } from '../../theme/ThemeProvider';
import { cn } from '../../utils/classNames';
import styles from './ThemeSwitcher.module.css';

export type ThemeSwitcherProps = {
  themes?: Theme[];
  size?: 'sm' | 'md';
  rounded?: 'sm' | 'md' | 'lg' | 'full';
  onChange?: (theme: Theme) => void;
  labels?: Record<Theme, string>;
  className?: string;
};

const toPascalCase = (value: string) => value.charAt(0).toUpperCase() + value.slice(1);

export function ThemeSwitcher({
  themes,
  size = 'md',
  rounded = 'md',
  onChange,
  labels,
  className,
}: ThemeSwitcherProps) {
  const { theme, setTheme, availableThemes } = useTheme();
  const themeList = themes && themes.length ? themes : availableThemes;

  const handleThemeChange = (newTheme: Theme) => {
    setTheme(newTheme);
    onChange?.(newTheme);
  };

  const containerClasses = cn(
    styles.container,
    styles[`rounded${toPascalCase(rounded)}` as keyof typeof styles],
    className
  );

  return (
    <div
      role="tablist"
      aria-label="Theme switcher"
      className={containerClasses}
    >
      {themeList.map((t) => {
        const isActive = theme === t;
        const label = labels?.[t] ?? t.charAt(0).toUpperCase() + t.slice(1);

        return (
          <button
            key={t}
            type="button"
            role="tab"
            aria-selected={isActive}
            onClick={() => handleThemeChange(t)}
            className={cn(
              styles.button,
              styles[`size${toPascalCase(size)}` as keyof typeof styles],
              isActive && styles.active
            )}
          >
            {label}
          </button>
        );
      })}
    </div>
  );
}

ThemeSwitcher.displayName = 'ThemeSwitcher';

export default ThemeSwitcher;