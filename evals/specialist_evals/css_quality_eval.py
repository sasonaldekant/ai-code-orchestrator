from __future__ import annotations
import re, json

WCAG_TOKENS = ["contrast", "focus", "aria-", "sr-only"]
BEM_RE = re.compile(r"\\.([a-z]+(?:-[a-z]+)*)(__[a-z-]+)?(--[a-z-]+)?\s*\{", re.I)

def score_css(doc: dict) -> dict:
    css = (doc.get("utilities", "") + "\n" + "\n".join(c.get("css", "") for c in doc.get("components", [])))
    bem_ok = bool(BEM_RE.search(css))
    wcag_hits = sum(tok in css.lower() for tok in WCAG_TOKENS)
    notes = []
    if not bem_ok: notes.append("No BEM selectors detected")
    if wcag_hits < 1: notes.append("No WCAG related tokens found")
    return {"score": (1 if bem_ok else 0) + wcag_hits, "notes": notes}
