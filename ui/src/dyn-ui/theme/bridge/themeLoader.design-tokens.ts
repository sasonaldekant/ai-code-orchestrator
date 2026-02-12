/// <reference types="vite/client" />
import type { DynThemeTokens } from '../tokens';
import { normalizeTokens } from './normalize';

// 1) Primarni izvor: vaĹˇ postojeÄ‡i design-tokens (TS/JS/JSON)
const dtModules = import.meta.glob('../../design-tokens/themes/*.{ts,tsx,js,json}');
const cfgModules = import.meta.glob('../../design-tokens/config.{ts,tsx,js,json}', { eager: true }) as Record<string, any>;
const cfg = Object.values(cfgModules)[0] || {};

// 2) Fallback (ako ne postoji design-tokens)
const fbModules = import.meta.glob('../themes/*.json');

export const CSS_VAR_PREFIX: string = cfg.CSS_VAR_PREFIX ?? 'dyn';

function onlyName(fp: string) {
  return fp.split('/').pop()!.replace(/\.(ts|tsx|js|json)$/, '');
}

export function getAvailableThemes(): string[] {
  const fromDT = Object.keys(dtModules).map(onlyName);
  if (fromDT.length) return fromDT;
  return Object.keys(fbModules).map((p) => p.split('/').pop()!.replace('.json',''));
}

export type ThemeName = string;

export async function loadThemeTokens(name: ThemeName): Promise<DynThemeTokens> {
  // probaj design-tokens prvo
  const dtKey = Object.keys(dtModules).find((p) => p.endsWith(`/themes/${name}.ts`) || p.endsWith(`/themes/${name}.tsx`) || p.endsWith(`/themes/${name}.js`) || p.endsWith(`/themes/${name}.json`));
  if (dtKey) {
    const mod: any = await (dtModules as Record<string, () => Promise<any>>)[dtKey]();
    const raw = mod?.default ?? mod?.tokens ?? mod;
    return normalizeTokens(raw);
  }
  // fallback JSON
  const fbKey = `../themes/${name}.json`;
  const loader = (fbModules as Record<string, () => Promise<any>>)[fbKey];
  if (!loader) {
    const all = getAvailableThemes();
    throw new Error(`[dyn-ui] Tema "${name}" nije pronaÄ‘ena. Dostupne teme: ${all.join(', ') || 'â€”'}`);
  }
  const mod = await loader();
  const raw = mod?.default ?? mod;
  return normalizeTokens(raw);
}

