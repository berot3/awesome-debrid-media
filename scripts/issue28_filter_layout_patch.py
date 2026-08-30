#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "scripts" / "build.py"

text = BUILD.read_text(encoding="utf-8")
old = "      .filters {{ grid-template-columns: 1fr auto; align-items: center; }}"
new = "      .filters {{ grid-template-columns: 1fr; align-items: stretch; }}"

if old not in text:
    if new in text:
        raise SystemExit(0)
    raise SystemExit("expected Issue 28 CSS target not found")

BUILD.write_text(text.replace(old, new, 1), encoding="utf-8")
