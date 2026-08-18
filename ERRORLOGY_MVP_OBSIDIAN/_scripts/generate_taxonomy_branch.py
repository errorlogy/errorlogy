#!/usr/bin/env python3
"""Generate Obsidian taxonomy branch from unified v16 JSON."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
JSON_PATH = (
    REPO
    / "ERRORLOGY"
    / "errorlogy_old_version"
    / "AGIU"
    / "errorlogy_unified_taxonomy_v16_max_catastrophe_2.json"
)
OUT = Path(__file__).resolve().parents[1] / "Таксономия"
POLITIC_CB = (
    REPO
    / "ERRORLOGY"
    / "errorlogy_old_version"
    / "Windows_old_MVP"
    / "Politic Bar (pre errorlogy)"
    / "taxonomy"
)


def slug(s: str) -> str:
    s = s.replace("–", "-").replace("—", "-").replace("/", "-")
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE)
    s = re.sub(r"\s+", " ", s).strip()
    return s[:80] if s else "mode"


def file_name(layer_key: str, title: str) -> str:
    return f"{layer_key} — {slug(title)}.md"


def md_escape(s: str) -> str:
    return (s or "").replace("|", "\\|").replace("\n", " ")


def mode_row(m: dict, *, def_field: str = "definition") -> str:
    mid = m.get("id", "?")
    name = md_escape(m.get("name", ""))
    d = md_escape(m.get(def_field) or m.get("operational_signature") or m.get("description", ""))[:200]
    if len((m.get(def_field) or m.get("operational_signature") or "")) > 200:
        d += "…"
    return f"| `{mid}` | {name} | {d} |"


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def table_header() -> str:
    return "| ID | Название | Определение (кратко) |\n|----|----------|----------------------|\n"


def extract_modes_list(obj, keys=("modes", "patterns", "error_types", "signal_types", "cluster_archetypes")):
    if isinstance(obj, list):
        return obj
    if isinstance(obj, dict):
        for k in keys:
            if k in obj and isinstance(obj[k], list):
                return obj[k]
    return []


def main() -> None:
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    layers = data.get("layers", {})
    counts = data.get("counts", {})
    meta = data.get("meta_dimensions", {})

    # --- Index ---
    LAYER_NOTE: dict[str, str] = {
        "L1": "Слои/L1 — Individual cognitive",
        "L2": "Слои/L2 — Group dynamic",
        "L3": "Слои/L3 — Informational environment",
        "L4": "Слои/L4 — Strategic incentive",
        "L5": "Слои/L5 — Mechanism aggregation",
        "L6": "Композиты и игровая теория",
        "GT": "Композиты и игровая теория",
        "MP_EXT": "Расширенные/MP_EXT — Механизмы расширенные",
        "GT_EXT": "Расширенные/GT_EXT — Игровая теория расширенная",
        "HM": "Расширенные/HM — Homo-MAS pathologies",
        "METHODS": "Слои MAX/METHODS — Methods - Inference",
        "LΩ": "Слои MAX/LΩ — Generative Topology",
        "SOCIAL_MEDIA": "Слои MAX/SOCIAL_MEDIA — Social Media Environment",
        "LCJ": "Слои MAX/LCJ — Legal - Juridical Contour",
        "LBI": "Слои MAX/LBI — Betterment - Improvement",
        "LAC": "Слои MAX/LAC — Agent Strategy Contribution",
        "LCC": "Слои MAX/LCC — Cognitive Competence Capacity",
        "MAX_UNIVERSE": "MAX mode universe — сводка",
        "WMS": "Слои MAX/WMS — Weak Multisource Signals",
        "ACC": "Слои MAX/ACC — Agent Contour Clusters",
        "EGD": "Слои MAX/EGD — Echo-room - Small-group",
        "FPD": "Слои MAX/FPD — Fuzzy Predictive Dynamics",
        "T4D": "Слои MAX/T4D — Temporal-Spatial Topology",
        "CAT": "Слои MAX/CAT — Catastrophe - Bifurcation",
    }
    layer_links = "\n".join(
        f"- [[{LAYER_NOTE.get(k, 'Слои — обзор')}|{k}]] — {v}"
        for k, v in layers.items()
    )
    write(
        OUT / "00 — Индекс таксономии.md",
        f"""# Индекс таксономии Errorlogy

> **Источник:** unified JSON v16 (OLD SKETCH).  
> Файл: `ERRORLOGY/errorlogy_old_version/AGIU/errorlogy_unified_taxonomy_v16_max_catastrophe_2.json`

**Версия:** `{data.get("version", "")}`  
**Онтология:** {data.get("ontology", "")}

## Навигация по ветке

- [[Источники и версии]]
- [[Мета-измерения]]
- [[Слои — обзор]]
- [[Атомарные режимы — сводка]]
- [[Композиты и игровая теория]]
- [[Расширенные слои MAX]]
- [[MAX mode universe — сводка]]
- [[Связь с politic.bar v0.6]]

## Слои (24 ключа в JSON)

{layer_links}

## Счётчики (из JSON)

| Ключ | Число |
|------|-------|
"""
        + "\n".join(f"| `{k}` | {v} |" for k, v in counts.items())
        + """

## Формула анализа (из ТЗ)

```text
DATA → WMS → μ → α → ACC → PNO → FPD → LBI → public card
```

→ [[../00 — Главная|Главная Obsidian]] · [[../Карта артефактов]]

#taxonomy #errorlogy #v16
""",
    )

    # --- Sources ---
    write(
        OUT / "Источники и версии.md",
        f"""# Источники и версии

## Unified taxonomy v16 (эта ветка)

| | |
|---|---|
| Версия | `{data.get("version")}` |
| Путь в репо | `AGIU/errorlogy_unified_taxonomy_v16_max_catastrophe_2.json` |
| Статус | **OLD SKETCH** — черновик онтологии |

{data.get("description", "")[:1200]}…

### Исходные файлы (atomic L1–L5)

| Файл | Роль |
|------|------|
| `cognitive_biases.json` | CB, слои L1–L3 |
| `strategic_failure_modes.json` | SF, L4 |
| `mechanism_pathologies.json` | MP, L5 |

## politic.bar pipeline (параллельный мир)

Три отдельных JSON в `Windows_old_MVP/.../taxonomy/` — **v0.6**, используются пайплайном `politic_bar/`, не merged с v16 автоматически.

→ [[Связь с politic.bar v0.6]] · [[00 — Индекс таксономии]]
""",
    )

    # --- Meta dimensions ---
    rows = "\n".join(
        f"| `{k}` | {md_escape(v)} |" for k, v in meta.items()
    )
    write(
        OUT / "Мета-измерения.md",
        f"""# Мета-измерения (R, O, A, C, T, X)

Поперечные оси, по которым режимы ошибок могут быть размечены в `atomic_modes.meta_dimensions`.

| Код | Смысл |
|-----|--------|
{rows}

→ [[00 — Индекс таксономии]] · [[Атомарные режимы — сводка]]
""",
    )

    # --- Layers overview ---
    write(
        OUT / "Слои — обзор.md",
        """# Слои — обзор

Таксономия Errorlogy v16 организована в **слои** — от атомарных когнитивных режимов до прогноза и катастроф.

## Группы

### Атомарный фундамент (L1–L5)
| Слой | Фокус |
|------|--------|
| [[Слои/L1 — Individual cognitive|L1]] | Индивидуальные когнитивные искажения (166) |
| [[Слои/L2 — Group dynamic|L2]] | Групповая динамика (17) |
| [[Слои/L3 — Informational environment|L3]] | Информационная среда (6) |
| [[Слои/L4 — Strategic incentive|L4]] | Стратегические / incentive сбои (14) |
| [[Слои/L5 — Mechanism aggregation|L5]] | Патологии агрегации (14) |

### Композиты и взаимодействие
- **L6 / PNO** — устойчивая неоптимальность → [[Композиты и игровая теория]]
- **GT** — игровые паттерны → [[Композиты и игровая теория]]

### Контуры и улучшение
- **LCJ** — правовой контур
- **LBI** — counterfactual / «как лучше»
- **LAC** — вклад агентов и стратегий
- **LCC** — когнитивная ёмкость системы

### Среда и MAS
- **SOCIAL_MEDIA**, **HM** — соцсети и Homo-MAS
- **MP_EXT**, **GT_EXT** — расширенные механизмы и игры

### Сигналы, прогноз, топология
- **WMS** — слабые мультисредные сигналы
- **ACC** — кластеры вклада
- **EGD** — эхо-комнаты малых групп
- **FPD** — fuzzy-прогноз
- **T4D** — время + пространство (3D+1D)
- **CAT** — теория катастроф / бифуркации

### Мета-слои
- **METHODS** — детекция, майнинг, валидация
- **LΩ** — генеративная топология (новые режимы)
- **MAX_UNIVERSE** — сводная вселенная режимов (381)

→ [[00 — Индекс таксономии]]
""",
    )

    # --- Atomic by layer ---
    by_layer: dict[str, list] = defaultdict(list)
    for m in data.get("atomic_modes", []):
        by_layer[m.get("layer", "?")].append(m)

    layer_titles = {
        "L1": "Individual cognitive",
        "L2": "Group dynamic",
        "L3": "Informational environment",
        "L4": "Strategic incentive",
        "L5": "Mechanism aggregation",
    }
    for layer_id in ["L1", "L2", "L3", "L4", "L5"]:
        modes = sorted(by_layer.get(layer_id, []), key=lambda x: x.get("id", ""))
        rows = "\n".join(mode_row(m) for m in modes)
        title = layer_titles.get(layer_id, layer_id)
        desc = layers.get(layer_id, "")
        write(
            OUT / "Слои" / file_name(layer_id, title),
            f"""# {layer_id} — {title}

{desc}

**Режимов в v16:** {len(modes)} (семейства: CB / SF / MP по `family`)

{table_header()}{rows}

→ [[../Слои — обзор]] · [[../00 — Индекс таксономии]]
""",
        )

    # --- Atomic summary ---
    fam = defaultdict(int)
    for m in data.get("atomic_modes", []):
        fam[m.get("family", "?")] += 1
    write(
        OUT / "Атомарные режимы — сводка.md",
        f"""# Атомарные режимы — сводка

Всего **{len(data.get("atomic_modes", []))}** записей в `atomic_modes` (целевой atomic_total: {counts.get("atomic_total")}).

| Слой | Число | Заметка |
|------|-------|---------|
| L1 | {len(by_layer["L1"])} | [[Слои/L1 — Individual cognitive]] |
| L2 | {len(by_layer["L2"])} | [[Слои/L2 — Group dynamic]] |
| L3 | {len(by_layer["L3"])} | [[Слои/L3 — Informational environment]] |
| L4 | {len(by_layer["L4"])} | [[Слои/L4 — Strategic incentive]] |
| L5 | {len(by_layer["L5"])} | [[Слои/L5 — Mechanism aggregation]] |

### По семейству

| family | count |
|--------|-------|
"""
        + "\n".join(f"| `{k}` | {v} |" for k, v in sorted(fam.items()))
        + """

→ [[Мета-измерения]]
""",
    )

    # --- PNO + GT ---
    pno = data.get("composite_patterns", {}).get("PNO", [])
    if isinstance(pno, dict):
        pno = pno.get("patterns", [])
    gt_rows = "\n".join(mode_row(m) for m in data.get("game_theory_patterns", []))
    pno_rows = ""
    if isinstance(pno, list):
        pno_rows = "\n".join(
            mode_row(m, def_field="definition")
            if isinstance(m, dict)
            else f"| ? | {m} | |"
            for m in pno
        )
    write(
        OUT / "Композиты и игровая теория.md",
        f"""# Композиты и игровая теория

## PNO — Persistent Non-Optimality (L6)

Счётчик JSON: **{counts.get("PNO", 7)}** композитных паттернов.

{table_header()}{pno_rows or "_См. composite_patterns.PNO в JSON._"}

## Game theory patterns (GT)

**{len(data.get("game_theory_patterns", []))}** паттернов.

{table_header()}{gt_rows}

→ [[00 — Индекс таксономии]]
""",
    )

    # --- Extended layers ---
    sections = [
        ("mechanism_pathologies_extended", "MP_EXT", "Механизмы расширенные"),
        ("game_theory_patterns_extended", "GT_EXT", "Игровая теория расширенная"),
        ("homo_mas_interaction_pathologies", "HM", "Homo-MAS pathologies"),
    ]
    ext_parts = []
    for json_key, layer_key, title in sections:
        items = data.get(json_key, [])
        rows = "\n".join(mode_row(m) for m in items)
        write(
            OUT / "Расширенные" / file_name(layer_key, title),
            f"""# {layer_key} — {title}

**{len(items)}** режимов · JSON: `{json_key}`

{layers.get(layer_key, "")}

{table_header()}{rows}

→ [[../Расширенные слои MAX]]
""",
        )
        ext_parts.append(
            f"- [[Расширенные/{file_name(layer_key, title)[:-3]}|{layer_key}]] ({len(items)})"
        )

    # Rich layer objects
    rich_layers = [
        ("weak_multisource_signal_layer", "WMS", "Weak Multisource Signals"),
        ("agent_contour_contribution_cluster_layer", "ACC", "Agent Contour Clusters"),
        ("echo_room_group_dynamics_layer", "EGD", "Echo-room / Small-group"),
        ("fuzzy_predictive_dynamics_layer", "FPD", "Fuzzy Predictive Dynamics"),
        ("temporal_spatial_topology_layer", "T4D", "Temporal-Spatial Topology"),
        ("catastrophe_theory_layer", "CAT", "Catastrophe / Bifurcation"),
        ("legal_juridical_contour_layer", "LCJ", "Legal / Juridical Contour"),
        ("betterment_improvement_layer", "LBI", "Betterment / Improvement"),
        ("agent_strategy_contribution_layer", "LAC", "Agent Strategy Contribution"),
        ("cognitive_competence_capacity_layer", "LCC", "Cognitive Competence Capacity"),
        ("methods_layer", "METHODS", "Methods / Inference"),
        ("generative_topology_layer", "LΩ", "Generative Topology"),
        ("social_media_layer", "SOCIAL_MEDIA", "Social Media Environment"),
    ]
    rich_parts = []
    for json_key, layer_key, title in rich_layers:
        section = data.get(json_key, {})
        if not isinstance(section, dict):
            continue
        principle = md_escape(
            section.get("core_principle")
            or section.get("principle")
            or section.get("central_thesis", "")
        )[:500]
        modes = extract_modes_list(section)
        rows = "\n".join(mode_row(m) for m in modes if isinstance(m, dict))
        methods = section.get("methods", [])
        method_lines = ""
        if isinstance(methods, list) and methods:
            method_lines = "\n### Methods\n\n" + "\n".join(
                f"- `{m.get('id', '?')}` — {m.get('name', '')}"
                if isinstance(m, dict)
                else f"- {m}"
                for m in methods[:20]
            )
            if len(methods) > 20:
                method_lines += f"\n- _…ещё {len(methods) - 20} в JSON_"

        modules = section.get("modules", [])
        mod_lines = ""
        if isinstance(modules, list) and modules:
            mod_lines = "\n### Modules\n\n" + "\n".join(
                f"- `{m.get('id', '?')}` — {m.get('name', '')}"
                if isinstance(m, dict)
                else f"- {m}"
                for m in modules
            )

        body = f"""# {layer_key} — {title}

{layers.get(layer_key, section.get("name", ""))}

## Принцип

{principle or "_см. JSON_"}

**Статус в JSON:** {section.get("status", "—")}
"""
        if modes:
            body += f"\n## Режимы / типы ({len(modes)})\n\n{table_header()}{rows}\n"
        body += method_lines + mod_lines
        body += "\n\n→ [[../Расширенные слои MAX]] · [[../00 — Индекс таксономии]]\n"
        write(OUT / "Слои MAX" / file_name(layer_key, title), body)
        rich_parts.append(
            f"- [[Слои MAX/{file_name(layer_key, title)[:-3]}|{layer_key}]]"
            + (f" — {len(modes)} modes" if modes else "")
        )

    write(
        OUT / "Расширенные слои MAX.md",
        f"""# Расширенные слои MAX

Слои v16 beyond atomic L1–L5: сигналы, кластеры, прогноз, топология, катастрофы, право, улучшение, методы.

## Расширенные списки (array в корне JSON)

{chr(10).join(ext_parts)}

## Объектные слои (nested JSON)

{chr(10).join(rich_parts)}

→ [[00 — Индекс таксономии]]
""",
    )

    # --- MAX universe summary by layer tag ---
    universe = data.get("max_mode_universe", [])
    u_by_layer: dict[str, list] = defaultdict(list)
    for m in universe:
        if isinstance(m, dict):
            u_by_layer[m.get("layer", m.get("source_layer", "?"))].append(m)

    u_summary = "\n".join(
        f"| `{k}` | {len(v)} |"
        for k, v in sorted(u_by_layer.items(), key=lambda x: -len(x[1]))
    )
    # Full table might be huge - write separate file with all IDs
    u_rows = "\n".join(
        f"| `{m.get('id','?')}` | {md_escape(m.get('name',''))} | `{m.get('layer','')}` |"
        for m in sorted(universe, key=lambda x: x.get("id", ""))
        if isinstance(m, dict)
    )
    write(
        OUT / "MAX mode universe — сводка.md",
        f"""# MAX mode universe — сводка

Консолидированная вселенная режимов: **{len(universe)}** записей (`max_mode_universe`).

### По полю layer / source_layer

| layer | count |
|-------|-------|
{u_summary}

## Полный каталог ID

| ID | Название | layer |
|----|----------|-------|
{u_rows}

> Полные определения — только в JSON (файл ~16k строк).

→ [[00 — Индекс таксономии]]
""",
    )

    # --- politic.bar link ---
    pb_counts = {}
    if POLITIC_CB.exists():
        for fname in [
            "cognitive_biases.json",
            "strategic_failure_modes.json",
            "mechanism_pathologies.json",
        ]:
            p = POLITIC_CB / fname
            if p.exists():
                j = json.loads(p.read_text(encoding="utf-8"))
                key = "biases"
                for alt in ("biases", "modes", "failure_modes", "strategic_failure_modes"):
                    if alt in j:
                        key = alt
                        break
                items = j.get(key, [])
                if isinstance(items, list):
                    pb_counts[Path(fname).stem] = len(items)

    write(
        OUT / "Связь с politic.bar v0.6.md",
        f"""# Связь с politic.bar v0.6

Два представления одной идеи:

| | politic.bar v0.6 | Unified v16 (эта ветка) |
|---|------------------|-------------------------|
| Файлы | 3× `taxonomy/*.json` | 1× `errorlogy_unified_taxonomy_v16_*.json` |
| Пайплайн | `politic_bar/pipeline.py` | AGIU `TaxonomyLoader` |
| Слои в прод-скетче | L1–L5 (+ методология L6, GT в docs) | L1–CAT, METHODS, MAX_UNIVERSE |
| Записей (pipeline) | CB ~{pb_counts.get("cognitive_biases", "?")}, SF/MP отдельно | atomic 217 + universe 381 |

**Не мержить автоматически.** ID режимов (CB-xxx, SF-xxx, MP-xxx) должны совпадать в atomic части, но v16 добавляет слои без поддержки в старом Classifier.

→ [[Источники и версии]] · [[../politic.bar — скетч MVP]]
""",
    )

    print(f"Generated taxonomy branch under {OUT}")


if __name__ == "__main__":
    main()
