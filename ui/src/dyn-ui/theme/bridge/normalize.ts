import type { DynThemeTokens } from '../tokens';

type AnyObj = Record<string, any>;

function alias(target: AnyObj, from: string, to: string) {
  if (target[from] != null && target[to] == null) {
    target[to] = target[from];
  }
}

function unwrap(group?: AnyObj): AnyObj | undefined {
  if (!group) return group;
  const out: AnyObj = {};
  for (const [k, v] of Object.entries(group)) {
    if (v && typeof v === 'object' && 'value' in v) out[k] = v.value;
    else out[k] = v;
  }
  return out;
}

export function normalizeTokens(input: AnyObj): DynThemeTokens {
  const t: AnyObj = { ...(input?.default ?? input) };

  // aliasi ka "standardizovanom" imenovanju
  alias(t, 'sizes', 'size');
  alias(t, 'space', 'spacing');
  alias(t, 'radii', 'radius');
  alias(t, 'fontSizes', 'fontSize');
  alias(t, 'fontWeights', 'fontWeight');
  alias(t, 'palette', 'colors');
  alias(t, 'tone', 'tones');

  const normalized: DynThemeTokens = {
    size: unwrap(t.size),
    spacing: unwrap(t.spacing),
    radius: unwrap(t.radius),
    fontSize: unwrap(t.fontSize),
    fontWeight: unwrap(t.fontWeight),
    colors: unwrap(t.colors),
    shadow: unwrap(t.shadow),
    variants: t.variants,
    tones: t.tones,
  };

  return normalized;
}
