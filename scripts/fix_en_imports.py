#!/usr/bin/env python3
"""One-shot helper: replace ru.ts imports with en.ts in GUI src trees."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for d in ("errorlogy-gui/src", "errorlogy-gui-v2/src"):
    for p in (ROOT / d).rglob("*.ts*"):
        text = p.read_text(encoding="utf-8")
        if "../lib/ru" in text:
            p.write_text(text.replace("from '../lib/ru'", "from '../lib/en'"), encoding="utf-8")
            print("updated", p.relative_to(ROOT))
