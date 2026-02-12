/// <reference types="vite/client" />
import type { DynThemeTokens } from './tokens';

// Vite-only: map JSON fajlova u ovom folderu
const themeModules = import.meta.glob('./themes/*.json');

export type ThemeName = string; // npr. 'light' | 'dark'

export async function loadThemeTokens(name: ThemeName): Promise<DynThemeTokens> {
  const path = `./themes/${name}.json`;
  const loader = (themeModules as Record<string, () => Promise<any>>)[path];
  if (!loader) {
    throw new Error(`[dyn-ui] Nepoznata tema: ${name}. Dostupno: ${Object.keys(themeModules).map(p => p.replace('./themes/','').replace('.json','')).join(', ')}`);
  }
  const mod = await loader();
  return (mod?.default ?? mod) as DynThemeTokens;
}

export function getAvailableThemes(): string[] {
  return Object.keys(themeModules).map(p => p.replace('./themes/','').replace('.json',''));
}

