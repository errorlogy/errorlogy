---
id: TZ-003
title: Seed corpus — 5 governance cases, engine_only pipeline, SQLite
status: done
priority: 3
estimated: 30min
author: Claude
created: 2026-06-12
depends_on: [TZ-002]
---

## Контекст

После TZ-002 появляется SQLite. Нужно наполнить его первыми кейсами чтобы:
- Globe показывал реальные данные вместо static seed JSON
- Появился baseline для будущей калибровки engine
- MasPage показывал recent_runs из реальных прогонов

Все 5 кейсов — из OLD SKETCH (полные исходники в `ERRORLOGY/errorlogy_old_version/`).
Запускаем `engine_only=True` — без LLM-вызовов.

---

## Создать `scripts/seed_corpus.py`

**Новый файл:** `c:\Users\Public\ERRORLOGY_MVP\errorlogy-mas\scripts\seed_corpus.py`

```python
"""Load 5 seed governance cases and run engine_only pipeline on each."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from mas.db import init_db
from mas.orchestrator import Orchestrator

SEED_CASES = [
    {
        "case_id": "challenger-1986",
        "title": "Space Shuttle Challenger Disaster",
        "country": "USA",
        "year": 1986,
        "text": (
            "NASA management overruled engineers who warned that O-rings would fail in cold temperatures. "
            "Engineers sent a memo documenting concerns prior to launch. "
            "Management pressure reversed the engineers' no-launch recommendation. "
            "The shuttle broke apart 73 seconds after launch, killing all 7 crew members. "
            "The Rogers Commission investigation found groupthink and communication failure among decision-makers."
        ),
    },
    {
        "case_id": "chernobyl-1986",
        "title": "Chernobyl Nuclear Disaster",
        "country": "USSR",
        "year": 1986,
        "text": (
            "Operators at Chernobyl conducted a safety test while the reactor was in an unstable state. "
            "Warnings about reactor design flaws had been suppressed by Soviet authorities for years. "
            "Bureaucratic pressure to complete the test overrode safety protocols. "
            "The explosion released massive radiation causing a regional catastrophe. "
            "Government initially concealed the scale of the disaster from the public and international community."
        ),
    },
    {
        "case_id": "iraq-wmd-2003",
        "title": "Iraq WMD Intelligence Failure",
        "country": "USA",
        "year": 2003,
        "text": (
            "US intelligence agencies produced a National Intelligence Estimate concluding Iraq possessed WMDs. "
            "Dissenting assessments from DIA and State Department were minimized in the final report. "
            "Political pressure influenced intelligence analysis and suppressed alternative views. "
            "No weapons of mass destruction were found after the invasion of Iraq. "
            "The Senate Intelligence Committee inquiry found groupthink and absence of critical review."
        ),
    },
    {
        "case_id": "post-office-horizon-1999",
        "title": "UK Post Office Horizon IT Scandal",
        "country": "UK",
        "year": 1999,
        "text": (
            "Post Office deployed the Horizon IT system despite known accounting errors and software defects. "
            "Over 900 subpostmasters were prosecuted for false accounting based on faulty data. "
            "Post Office management repeatedly dismissed and suppressed complaints about system bugs. "
            "Whistleblowers and legal challenges were ignored for over 15 years. "
            "The Horizon Inquiry found systematic denial and cover-up by Post Office leadership."
        ),
    },
    {
        "case_id": "deepwater-horizon-2010",
        "title": "Deepwater Horizon Blowout",
        "country": "USA",
        "year": 2010,
        "text": (
            "BP management accepted risk trade-offs to reduce cost and time on the Macondo well. "
            "Engineers raised concerns about cement integrity and well control procedures. "
            "A pressure test showing a kick was misinterpreted due to schedule pressure. "
            "The blowout killed 11 workers and caused the largest marine oil spill in US history. "
            "Presidential Commission found management decisions prioritized schedule over safety."
        ),
    },
]


def main() -> None:
    init_db()
    orch = Orchestrator(init_llm=False)

    for case in SEED_CASES:
        print(f"  → {case['case_id']} ...", end=" ", flush=True)
        result = orch.run_from_text(
            case_id=case["case_id"],
            raw_text=case["text"],
            title=case["title"],
            country=case["country"],
            year=case["year"],
            engine_only=True,
            verbose=False,
        )
        top = result.top_modes[0] if result.top_modes else None
        print(
            f"top={top.mode_id if top else 'none'} μ={top.mu:.3f} "
            f"cat={result.cat.catastrophe_hypothesis} "
            f"cep={result.wms.cep:.3f}"
        )

    print(f"\nDone. {len(SEED_CASES)} cases saved to DB.")


if __name__ == "__main__":
    main()
```

---

## Запуск

```bash
cd c:\Users\Public\ERRORLOGY_MVP\errorlogy-mas
python scripts/seed_corpus.py
```

Ожидаемый вывод (примерный):
```
  → challenger-1986 ... top=CB-XXX μ=0.5xx cat=CAT-003 cep=0.xxx
  → chernobyl-1986 ...  top=CB-XXX μ=0.5xx cat=CAT-001 cep=0.xxx
  → iraq-wmd-2003 ...   top=CB-XXX μ=0.5xx cat=CAT-000 cep=0.xxx
  → post-office-horizon-1999 ... top=CB-XXX μ=0.5xx cat=CAT-000 cep=0.xxx
  → deepwater-horizon-2010 ...   top=CB-XXX μ=0.5xx cat=CAT-003 cep=0.xxx

Done. 5 cases saved to DB.
```

---

## Проверка после запуска

```bash
# Проверить записи в DB:
python -c "
from mas.db import list_cases, country_stats
import json
print('Cases:', json.dumps(list_cases(), indent=2))
print('Countries:', json.dumps(country_stats(), indent=2))
"

# Globe endpoint должен вернуть реальные данные:
# GET /api/stats/countries → countries: [{country: USA, total_cases: 3}, {country: UK, total_cases: 1}, ...]
```

---

## Что НЕ делать

- Не запускать full MAS pipeline на seed кейсах (нет LLM keys в scope этой задачи)
- Не редактировать тексты кейсов для "улучшения" результатов движка
- Не добавлять больше 5 кейсов в этом скрипте
- Не удалять `country_stats_seed.json` — он остаётся fallback
