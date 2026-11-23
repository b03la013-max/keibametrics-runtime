"""PDF/detail runner-universe guard (11/23 review P0).

On 2026-11-23 the legacy meeting-PDF parser bound the previous race's column to
FKS R03 (it returned FKS R02's runners) and to TKY R04 (TKY R03's runners). The
strict column recovery also failed, so SOURCE failed and both races were lost,
although the official JRADB detailed card for the right race was present.

`pdf_is_other_race` recognises only that case: the PDF parse and the detail card
have no horse name in common (every horse number differs, at least 5 runners on
both sides). Then the PDF parse is about another race and carries no evidence for
this race, and the same-authority detail fallback (already used before the PDF is
published) applies. Any partial mismatch still fails SOURCE as before.
"""
from __future__ import annotations
import re
import unicodedata

MIN_RUNNERS = 5


def _norm(name) -> str:
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", str(name or "")))


def pdf_is_other_race(pdf_names: dict, detail_names: dict) -> bool:
    """True only when the two runner maps share no horse name at all."""
    p = {_norm(v) for v in (pdf_names or {}).values() if _norm(v)}
    h = {_norm(v) for v in (detail_names or {}).values() if _norm(v)}
    if len(p) < MIN_RUNNERS or len(h) < MIN_RUNNERS:
        return False
    if len(p) != len(pdf_names) or len(h) != len(detail_names):
        return False  # blank names: not provable
    return not (p & h)
