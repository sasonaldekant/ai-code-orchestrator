import type { DynThemeTokens, TokenGroup } from './tokens';

export type ApplyOptions = {
  scope?: HTMLElement | string;
  id?: string;
  prefix?: string;
};

function getLeafEntries(obj: TokenGroup, prefix: string[] = []) {
  const out: Array<[string, string]> = [];
  for (const key in obj) {
    const v: any = (obj as any)[key];
    if (v && typeof v === 'object' && !('value' in v)) {
      out.push(...getLeafEntries(v as TokenGroup, [...prefix, key]));
    } else {
      const raw = typeof v === 'object' && v && 'value' in v ? String(v.value) : String(v);
      out.push([[...prefix, key].join('.'), raw]);
    }
  }
  return out;
}

export function tokensToCssVars(tokens: DynThemeTokens, prefix = 'dyn') {
  const entries: Array<[string, string]> = [];
  for (const group of ['size','spacing','radius','fontSize','fontWeight','colors','shadow'] as const) {
    const g = (tokens as any)[group] as TokenGroup | undefined;
    if (!g) continue;
    for (const [dotKey, value] of getLeafEntries(g)) {
      const varName = `--${prefix}-${group}-${dotKey.replace(/\./g, '-')}`;
      entries.push([varName, value]);
    }
  }
  return entries;
}

export function applyCssVars(tokens: DynThemeTokens, opts: ApplyOptions = {}) {
  const id = opts.id ?? 'dyn-theme';
  const prefix = opts.prefix ?? 'dyn';
  const entries = tokensToCssVars(tokens, prefix);

  let scopeEl: HTMLElement | null;
  if (typeof opts.scope === 'string') scopeEl = document.querySelector(opts.scope);
  else if (opts.scope instanceof HTMLElement) scopeEl = opts.scope;
  else scopeEl = document.documentElement;

  let styleEl = document.getElementById(id) as HTMLStyleElement | null;
  if (!styleEl) {
    styleEl = document.createElement('style');
    styleEl.id = id;
    document.head.appendChild(styleEl);
  }

  const selector = scopeEl === document.documentElement ? ':root' : `[data-dyn-theme]`;
  if (scopeEl && scopeEl !== document.documentElement) scopeEl.setAttribute('data-dyn-theme', '');

  const css = `${selector}{\n${entries.map(([k,v]) => `  ${k}: ${v};`).join('\n')}\n}`;
  styleEl.textContent = css;
  return css;
}
