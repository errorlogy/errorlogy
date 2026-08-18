"""Shared test setup: importable repo root + null-byte safety net.

Cowork bash mount has an observed size-ceiling cache bug: a file pinned
at first-read size can later be served null-padded if it shrinks. We
defend against that here by skipping any test_*.py that turns up with
null bytes at collection time. On a clean Windows-side checkout the
predicate is always false and nothing is skipped.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


collect_ignore: list[str] = []
_TESTS_DIR = Path(__file__).resolve().parent
for _candidate in _TESTS_DIR.glob("test_*.py"):
    try:
        if b"\x00" in _candidate.read_bytes():
            collect_ignore.append(_candidate.name)
    except OSError:
        continue
