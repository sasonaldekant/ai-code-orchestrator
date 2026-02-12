import * as React from 'react';

type Key = string;

export type SxProps = {
  p?: Key; px?: Key; py?: Key; pt?: Key; pr?: Key; pb?: Key; pl?: Key;
  m?: Key; mx?: Key; my?: Key; mt?: Key; mr?: Key; mb?: Key; ml?: Key;
  gap?: Key;
  w?: Key | number | string; h?: Key | number | string;
  size?: Key;
  radius?: Key;
  color?: Key;
  bg?: Key;
  fontSize?: Key;
  fontWeight?: Key;
  shadow?: Key;
};

function tokenVar(group: string, key?: string) {
  return key ? `var(--${'dyn'}-${group}-${String(key).replace(/\./g,'-')})` : undefined;
  // Napomena: CSS_VAR_PREFIX je već upisan u DOM kroz applyCssVars(); ovde koristimo 'dyn' u "sx" eksplicitno
  // ili možeš proslediti prefiks kroz context ako želiš dodatnu fleksibilnost.
}

export function sxToStyle(sx?: SxProps): React.CSSProperties {
  if (!sx) return {};
  const st: React.CSSProperties = {};
  const set = (prop: keyof React.CSSProperties, val?: any) => { if (val != null) (st as any)[prop] = val; };

  const sp = (k?: Key) => tokenVar('spacing', k);
  set('padding', sp(sx.p));
  set('paddingLeft', sp(sx.pl ?? sx.px));
  set('paddingRight', sp(sx.pr ?? sx.px));
  set('paddingTop', sp(sx.pt ?? sx.py));
  set('paddingBottom', sp(sx.pb ?? sx.py));

  set('margin', sp(sx.m));
  set('marginLeft', sp(sx.ml ?? sx.mx));
  set('marginRight', sp(sx.mr ?? sx.mx));
  set('marginTop', sp(sx.mt ?? sx.my));
  set('marginBottom', sp(sx.mb ?? sx.my));

  set('gap', sp(sx.gap));

  const sz = (k?: Key) => tokenVar('size', k);
  set('width', typeof sx.w === 'string' || typeof sx.w === 'number' ? sx.w : sz(sx.w as any));
  set('height', typeof sx.h === 'string' || typeof sx.h === 'number' ? sx.h : sz(sx.h as any));
  if (sx.size) { set('width', sz(sx.size)); set('height', sz(sx.size)); }

  set('borderRadius', tokenVar('radius', sx.radius));
  set('color', tokenVar('colors', sx.color));
  set('backgroundColor', tokenVar('colors', sx.bg));
  set('fontSize', tokenVar('fontSize', sx.fontSize));
  set('fontWeight', tokenVar('fontWeight', sx.fontWeight));
  set('boxShadow', tokenVar('shadow', sx.shadow));

  return st;
}
