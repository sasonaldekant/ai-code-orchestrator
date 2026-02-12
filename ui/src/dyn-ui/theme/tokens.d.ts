export type TokenDict = Record<string, any>;

export type TokenGroup = {
  [key: string]: string | { value: string } | TokenGroup;
};

export interface DynThemeTokens {
  size?: TokenGroup;
  spacing?: TokenGroup;
  radius?: TokenGroup;
  fontSize?: TokenGroup;
  fontWeight?: TokenGroup;
  colors?: TokenGroup;
  shadow?: TokenGroup;
  variants?: string[];
  tones?: string[];
}
