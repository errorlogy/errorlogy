---
id: TZ-001
title: Engine bugfixes — dead code, fragile rules, Challenger-specific keywords
status: done
priority: 1
estimated: 1h
author: Claude
created: 2026-06-12
---

## Context

Re-audit engine modules after v0.2.2. Four independent fixes across four files.
Each fix is isolated — can be done in any order.

---

## Fix 1 — pno.py: remove dead code + fix fragile ID matching

**File:** `mas/engine/pno.py`

**Problem 1:** `_family_weights()` (lines 14–21) is defined but never called.

**Action:** Delete the function entirely.

---

**Problem 2:** PNO name lookup (lines 55–59) — fragile string replace:
```python
# BEFORE:
if pid.replace("PNO-00", "PNO-").replace("PNO-0", "PNO-") == dominant.replace("PNO-0", "PNO-"):
```
Breaks if ID has unexpected format.

**Action:** Replace with normalization via int:
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

## Fix 2 — t4d.py: remove Challenger-specific keywords

**File:** `mas/engine/t4d.py`

**Problem:** `_STAGE_KEYWORDS` contains "1977" and "teleconference" — Challenger 1986 case artifacts. They fire on any case mentioning year 1977 or the word teleconference.

**Action — replace `_STAGE_KEYWORDS` entirely (lines 12–18):**
```python
_STAGE_KEYWORDS = {
    "weak_signal":     ("concern", "memo", "warning", "risk", "prior", "documented", "flagged", "noted"),
    "ignored_warning": ("overruled", "reversed", "pressure", "dissent", "ignored", "rejected", "dismissed"),
    "escalation":      ("launch", "approve", "authorize", "decision", "proceed", "greenlit", "signed"),
    "failure":         ("broke", "destroyed", "disaster", "failure", "explosion", "accident", "collapsed"),
    "inquiry":         ("commission", "investigation", "inquiry", "report", "hearing", "audit", "review"),
}
```

**Also:** in `build_topology` (lines 88–94) fix latency_risk condition:
```python
# BEFORE:
if any(k in text for k in ("overruled", "not conveyed", "not transmitted", "pressure")):

# AFTER:
if any(k in text for k in ("overruled", "reversed", "pressure", "dissent", "ignored",
                            "rejected", "dismissed", "not transmitted")):
```

---

## Fix 3 — egd.py: remove synthetic fallback mode insertion

**File:** `mas/engine/egd.py`

**Problem:** When real EGD modes are not found in `top_modes` (lines 66–77), code inserts CB-019/CB-028/EGD-002 with synthetic μ = `0.3 + 0.4 * echo_pressure`. This creates false "results" — as if groupthink is definitely active when data does not support it.

**Action:** Delete the `if not egd_modes_raw:` block entirely. Empty `egd_modes_raw` is a valid result (EGD patterns not detected).

```python
# BEFORE:
if not egd_modes_raw:
    for mid in ("CB-019", "CB-028", "EGD-002"):
        egd_modes_raw.append(ModeScore(...synthetic mu...))

likely = apply_mode_guards(egd_modes_raw[:4], warnings)

# AFTER:
likely = apply_mode_guards(egd_modes_raw[:4], warnings)
# (if not egd_modes_raw block removed)
```

---

## Fix 4 — cat.py: fix CAT-002 + extend sympy forms

**File:** `mas/engine/cat.py`

**Problem 1:** CAT-002 (line 11) checks `"capacity" in cluster.name.lower()` — breaks if ACC returned a cluster with a different name.

**Action — extend check:**
```python
("CAT-002", lambda w, t, a: a.max_contribution_cluster.score > 0.45 and (
    a.max_contribution_cluster.cluster_id in ("ACC-001", "ACC-002", "ACC-003") or
    "capacity" in a.max_contribution_cluster.name.lower() or
    "veto" in a.max_contribution_cluster.name.lower()
)),
```

**Problem 2:** `_sympy_form` returns "generic_fold" for CAT-003/010/015.

**Action — replace `forms` dict in `_sympy_form`:**
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

## Verification

```bash
cd errorlogy-mas
pytest tests/ -x -q
# Expected: 16 passed
```

Do not modify tests.
