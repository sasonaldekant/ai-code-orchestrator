export interface ThemeSwitcherProps {
  theme?: 'light' | 'dark' | 'system';
  onChange?: (theme: 'light' | 'dark' | 'system') => void;
}
