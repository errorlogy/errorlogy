---
id: TZ-001
title: Engine bugfixes — dead code, fragile rules, Challenger-specific keywords
status: done
priority: 1
estimated: 1h
author: Claude
created: 2026-06-12
---

## Контекст

Re-audit engine modules после v0.2.2. Четыре независимых исправления в четырёх файлах.
Каждое исправление изолировано — можно делать в любом порядке.

---

## Fix 1 — pno.py: удалить dead code + починить fragile ID matching

**Файл:** `mas/engine/pno.py`

**Проблема 1:** `_family_weights()` (строки 14–21) определена но нигде не вызывается.

**Действие:** Удалить функцию целиком.

---

**Проблема 2:** PNO name lookup (строки 55–59) — хрупкий string replace:
```python
# БЫЛО:
if pid.replace("PNO-00", "PNO-").replace("PNO-0", "PNO-") == dominant.replace("PNO-0", "PNO-"):
```
Ломается если ID имеет неожиданный формат.

**Действие:** Заменить на нормализацию через int:
```python
def _pno_num(pid: str) -> int:
    try:
        return int(pid.split("-")[-1])
    except ValueError:
        return -1

dominant_num = _pno_num(dominant)
pno_name = ""
for p in pno_defs:
    if _pno_num(p.get("id", "")) == dominant_num:
        pno_name = p.get("name", "")
        break
```

---

## Fix 2 — t4d.py: убрать Challenger-специфичные keywords

**Файл:** `mas/engine/t4d.py`

**Проблема:** `_STAGE_KEYWORDS` содержит "1977" и "teleconference" — артефакты Challenger-кейса 1986 года. Сработают на любом кейсе где упоминается год 1977 или слово teleconference.

**Действие — заменить `_STAGE_KEYWORDS` целиком (строки 12–18):**
```python
_STAGE_KEYWORDS = {
    "weak_signal":     ("concern", "memo", "warning", "risk", "prior", "documented", "flagged", "noted"),
    "ignored_warning": ("overruled", "reversed", "pressure", "dissent", "ignored", "rejected", "dismissed"),
    "escalation":      ("launch", "approve", "authorize", "decision", "proceed", "greenlit", "signed"),
    "failure":         ("broke", "destroyed", "disaster", "failure", "explosion", "accident", "collapsed"),
    "inquiry":         ("commission", "investigation", "inquiry", "report", "hearing", "audit", "review"),
}
```

**Также:** в `build_topology` (строки 88–94) исправить latency_risk condition:
```python
# БЫЛО:
if any(k in text for k in ("overruled", "not conveyed", "not transmitted", "pressure")):

# СТАЛО:
if any(k in text for k in ("overruled", "reversed", "pressure", "dissent", "ignored",
                            "rejected", "dismissed", "not transmitted")):
```

---

## Fix 3 — egd.py: убрать synthetic fallback mode insertion

**Файл:** `mas/engine/egd.py`

**Проблема:** Когда реальные EGD-режимы не найдены в `top_modes` (строки 66–77), код вставляет CB-019/CB-028/EGD-002 с синтетическим μ = `0.3 + 0.4 * echo_pressure`. Это создаёт ложные "результаты" — будто groupthink точно активирован, хотя данных для этого нет.

**Действие:** Удалить блок `if not egd_modes_raw:` целиком. Пустой `egd_modes_raw` — это корректный результат (EGD-паттерны не выявлены).

```python
# БЫЛО:
if not egd_modes_raw:
    for mid in ("CB-019", "CB-028", "EGD-002"):
        egd_modes_raw.append(ModeScore(...synthetic mu...))

likely = apply_mode_guards(egd_modes_raw[:4], warnings)

# СТАЛО:
likely = apply_mode_guards(egd_modes_raw[:4], warnings)
# (блок if not egd_modes_raw удалён)
```

---

## Fix 4 — cat.py: починить CAT-002 + расширить sympy forms

**Файл:** `mas/engine/cat.py`

**Проблема 1:** CAT-002 (строка 11) проверяет `"capacity" in cluster.name.lower()` — ломается если ACC вернул кластер с другим именем.

**Действие — расширить проверку:**
```python
("CAT-002", lambda w, t, a: a.max_contribution_cluster.score > 0.45 and (
    a.max_contribution_cluster.cluster_id in ("ACC-001", "ACC-002", "ACC-003") or
    "capacity" in a.max_contribution_cluster.name.lower() or
    "veto" in a.max_contribution_cluster.name.lower()
)),
```

**Проблема 2:** `_sympy_form` возвращает "generic_fold" для CAT-003/010/015.

**Действие — заменить `forms` dict в `_sympy_form`:**
```python
forms = {
    "CAT-001": f"x**3 + {a}*x",
    "CAT-002": f"x**4 + {a}*x**2 + {b}*x",
    "CAT-003": f"x**5 + {a}*x**3 + {b}*x**2 + c*x",
    "CAT-010": f"x**3 - {a}*x",
    "CAT-015": f"x**4 - {a}*x**2",
}
```

---

## Проверка

```bash
cd c:\Users\Public\ERRORLOGY_MVP\errorlogy-mas
pytest tests/ -x -q
# Ожидается: 16 passed
```

Тесты не изменять.
