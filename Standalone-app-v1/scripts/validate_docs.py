#!/usr/bin/env python3
"""Valida i link Markdown interni del repo (file .md + anchor).

Porta a script permanente i check M6 step 1-2 del piano di armonizzazione doc
(storico: Docs/Piano-di-lavoro.md, rimosso — vedi Docs/piano-di-lavoro-v2.md §1):
  1. ogni link [testo](path.md) relativo deve risolvere a un file esistente,
     con risoluzione relativa al file SORGENTE (non alla CWD);
  2. ogni link [testo](path.md#anchor) deve puntare a uno slug GitHub reale
     di un heading del file target (underscore mantenuti, emoji/punteggiatura
     rimossi, accenti mantenuti, heading duplicati -> suffissi -1/-2/...).

Esecuzione: python scripts/validate_docs.py   (da Standalone-app-v1/)
Exit code: 0 = verde, 1 = almeno un link/anchor rotto.
Output volutamente ASCII-only (nessun crash cp1252 su console Windows).

NON copre: link verso file non-.md (es. ../src/*.tsx — vedi piano-di-lavoro-v2.md
§7.6), anchor in-page ](#x), URL esterni (ignorati).
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

EXCLUDED_PARTS = {"node_modules", ".venv", ".git", "__pycache__"}
# Docs/archive = testo storico non normativo (piano-di-lavoro-v2.md §7.11)
EXCLUDED_REL_PREFIXES = ("docs/archive",)

LINK_RE = re.compile(r"\]\(([^)#\s]+\.md)(#[^)\s]*)?\)")


def github_slug(heading: str) -> str:
    """Slug GitHub di un heading Markdown (regole verificate su questo repo)."""
    h = re.sub(r"^#+\s*", "", heading.strip())
    # strip code/emphasis come GitHub; NON rimuovere '_' (GitHub lo mantiene)
    h = h.replace("`", "").replace("*", "")
    h = h.lower()
    # \w in Python 3 e' Unicode di default -> mantiene lettere accentate come GitHub
    h = re.sub(r"[^\w\s-]", "", h, flags=re.U)
    return re.sub(r"\s+", "-", h)


def heading_slugs(md_path: Path) -> set[str]:
    """Tutti gli slug del file, con suffissi -1/-2 per heading duplicati."""
    slugs: set[str] = set()
    seen: dict[str, int] = {}
    try:
        text = md_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return slugs
    in_fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or not line.lstrip().startswith("#"):
            continue
        base = github_slug(line)
        n = seen.get(base, 0)
        seen[base] = n + 1
        slugs.add(base if n == 0 else f"{base}-{n}")
    return slugs


def is_excluded(path: Path, root: Path) -> bool:
    if EXCLUDED_PARTS.intersection(p.lower() for p in path.parts):
        return True
    rel = path.relative_to(root).as_posix().lower()
    return rel.startswith(EXCLUDED_REL_PREFIXES)


def main() -> int:
    root = Path(__file__).resolve().parent.parent  # Standalone-app-v1/
    broken = 0
    slug_cache: dict[Path, set[str]] = {}

    for md in sorted(root.rglob("*.md")):
        if is_excluded(md, root):
            continue
        try:
            text = md.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            print(f"READ ERROR: {md.relative_to(root)}: {exc}")
            broken += 1
            continue
        in_fence = False
        for lineno, line in enumerate(text.splitlines(), start=1):
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            for match in LINK_RE.finditer(line):
                target, anchor = match.group(1), match.group(2)
                if target.startswith(("http://", "https://")):
                    continue
                resolved = (md.parent / target).resolve()
                rel_src = md.relative_to(root).as_posix()
                if not resolved.exists():
                    print(f"BROKEN LINK: {rel_src}:{lineno} -> {target}")
                    broken += 1
                    continue
                if anchor:
                    slugs = slug_cache.setdefault(resolved, heading_slugs(resolved))
                    if anchor[1:].lower() not in slugs:
                        print(f"BAD ANCHOR: {rel_src}:{lineno} -> {target}{anchor}")
                        broken += 1

    if broken:
        print(f"FAIL: {broken} link/anchor rotti")
        return 1
    print("OK: tutti i link e gli anchor .md sono validi")
    return 0


if __name__ == "__main__":
    sys.exit(main())
