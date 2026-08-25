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
OUT = Path(__file__).resolve().parents[1] / ""
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
    return "| ID | Name | Definition (brief) |\n|----|----------|----------------------|\n"


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
"L1": "/L1 — Individual cognitive",
"L2": "/L2 — Group dynamic",
"L3": "/L3 — Informational environment",
"L4": "/L4 — Strategic incentive",
"L5": "/L5 — Mechanism aggregation",
"L6": "Composites game theory",
"GT": "Composites game theory",
"MP_EXT": "/MP_EXT — ",
"GT_EXT": "/GT_EXT — ",
"HM": "/HM — Homo-MAS pathologies",
"METHODS": " MAX/METHODS — Methods - Inference",
"LΩ": " MAX/LΩ — Generative Topology",
"SOCIAL_MEDIA": " MAX/SOCIAL_MEDIA — Social Media Environment",
"LCJ": " MAX/LCJ — Legal - Juridical Contour",
"LBI": " MAX/LBI — Betterment - Improvement",
"LAC": " MAX/LAC — Agent Strategy Contribution",
"LCC": " MAX/LCC — Cognitive Competence Capacity",
"MAX_UNIVERSE": "MAX mode universe — ",
"WMS": " MAX/WMS — Weak Multisource Signals",
"ACC": " MAX/ACC — Agent Contour Clusters",
"EGD": " MAX/EGD — Echo-room - Small-group",
"FPD": " MAX/FPD — Fuzzy Predictive Dynamics",
"T4D": " MAX/T4D — Temporal-Spatial Topology",
"CAT": " MAX/CAT — Catastrophe - Bifurcation",
    }
    layer_links = "\n".join(
f"- [[{LAYER_NOTE.get(k, ' — ')}|{k}]] — {v}"
        for k, v in layers.items()
    )
    write(
        OUT / "00 — Taxonomy index.md",
        f"""# Taxonomy index Errorlogy

> **Source:** unified JSON v16 (OLD SKETCH).  
> : `ERRORLOGY/errorlogy_old_version/AGIU/errorlogy_unified_taxonomy_v16_max_catastrophe_2.json`

**Version:** `{data.get("version", "")}`  
**Ontology:** {data.get("ontology", "")}

## Branch navigation

- [[Sources and versions]]
- [[Meta-dimensions]]
- [[Layers — overview]]
- [[Atomic modes — summary]]
- [[Composites and game theory]]
- [[Extended MAX layers]]
- [[MAX mode universe — summary]]
- [[Link to politic.bar v0.6]]

## Layers (24 keys in JSON)

{layer_links}

## Counters (from JSON)

| Key | Count |
|------|-------|
"""
        + "\n".join(f"| `{k}` | {v} |" for k, v in counts.items())
        + """

## Analysis formula (from spec)

```text
DATA → WMS → μ → α → ACC → PNO → FPD → LBI → public card
```

→ [[../00 — |Obsidian home]] · [[../ ]]

#taxonomy #errorlogy #v16
""",
    )

    # --- Sources ---
    write(
OUT / " .md",
f"""#

## Unified taxonomy v16 (this branch)

| | |
|---|---|
| Version | `{data.get("version")}` |
| Path in repo | `AGIU/errorlogy_unified_taxonomy_v16_max_catastrophe_2.json` |
| Status | **OLD SKETCH** — ontology draft |

{data.get("description", "")[:1200]}…

### Source files (atomic L1–L5)

| File | Role |
|------|------|
| `cognitive_biases.json` | CB, layers L1–L3 |
| `strategic_failure_modes.json` | SF, L4 |
| `mechanism_pathologies.json` | MP, L5 |

## politic.bar pipeline (parallel world)

JSON `Windows_old_MVP/.../taxonomy/` — **v0.6**, used by pipeline `politic_bar/`, not merged v16 automatically.

→ [[Link to politic.bar v0.6]] · [[00 — Taxonomy index]]
""",
    )

    # --- Meta dimensions ---
    rows = "\n".join(
        f"| `{k}` | {md_escape(v)} |" for k, v in meta.items()
    )
    write(
        OUT / "Meta-dimensions.md",
        f"""# Meta-dimensions (R, O, A, C, T, X)

Cross-cutting axes, by which error modes `atomic_modes.meta_dimensions`.

| | Meaning |
|-----|--------|
{rows}

→ [[00 — Taxonomy index]] · [[Atomic modes — summary]]
""",
    )

    # --- Layers overview ---
    write(
OUT / " — .md",
"""# —

Errorlogy v16 **layers** — .

##

### (L1–L5)
| | |
|------|--------|
| [[Layers/L1 — Individual cognitive|L1]] | (166) |
| [[Layers/L2 — Group dynamic|L2]] | (17) |
| [[Layers/L3 — Informational environment|L3]] | (6) |
| [[Layers/L4 — Strategic incentive|L4]] | / incentive (14) |
| [[Layers/L5 — Mechanism aggregation|L5]] | (14) |

### Composites
- **L6 / PNO** — → [[Composites and game theory]]
- **GT** — → [[Composites and game theory]]

###
- **LCJ** —
- **LBI** — counterfactual / « »
- **LAC** —
- **LCC** —

### MAS
- **SOCIAL_MEDIA**, **HM** — Homo-MAS
- **MP_EXT**, **GT_EXT** —

### , ,
- **WMS** —
- **ACC** —
- **EGD** — -
- **FPD** — fuzzy-
- **T4D** — + (3D+1D)
- **CAT** — /

### -layers
- **METHODS** — , ,
- **LΩ** — ( )
- **MAX_UNIVERSE** — (381)

→ [[00 — Taxonomy index]]
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
OUT / "" / file_name(layer_id, title),
            f"""# {layer_id} — {title}

{desc}

**Modes in v16:** {len(modes)} (: CB / SF / MP `family`)

{table_header()}{rows}

→ [[../Layers — overview]] · [[../00 — Taxonomy index]]
""",
        )

    # --- Atomic summary ---
    fam = defaultdict(int)
    for m in data.get("atomic_modes", []):
        fam[m.get("family", "?")] += 1
    write(
OUT / " — .md",
f"""# —

**{len(data.get("atomic_modes", []))}** `atomic_modes` ( atomic_total: {counts.get("atomic_total")}).

| | | Note |
|------|-------|---------|
| L1 | {len(by_layer["L1"])} | [[Layers/L1 — Individual cognitive]] |
| L2 | {len(by_layer["L2"])} | [[Layers/L2 — Group dynamic]] |
| L3 | {len(by_layer["L3"])} | [[Layers/L3 — Informational environment]] |
| L4 | {len(by_layer["L4"])} | [[Layers/L4 — Strategic incentive]] |
| L5 | {len(by_layer["L5"])} | [[Layers/L5 — Mechanism aggregation]] |

###

| family | count |
|--------|-------|
"""
        + "\n".join(f"| `{k}` | {v} |" for k, v in sorted(fam.items()))
        + """

→ [[Meta-dimensions]]
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
OUT / "Composites game theory.md",
f"""# Composites game theory

## PNO — Persistent Non-Optimality (L6)

JSON: **{counts.get("PNO", 7)}** .

{table_header()}{pno_rows or "_See composite_patterns.PNO JSON._"}

## Game theory patterns (GT)

**{len(data.get("game_theory_patterns", []))}** .

{table_header()}{gt_rows}

→ [[00 — Taxonomy index]]
""",
    )

    # --- Extended layers ---
    sections = [
("mechanism_pathologies_extended", "MP_EXT", " "),
("game_theory_patterns_extended", "GT_EXT", " "),
        ("homo_mas_interaction_pathologies", "HM", "Homo-MAS pathologies"),
    ]
    ext_parts = []
    for json_key, layer_key, title in sections:
        items = data.get(json_key, [])
        rows = "\n".join(mode_row(m) for m in items)
        write(
OUT / "" / file_name(layer_key, title),
            f"""# {layer_key} — {title}

**{len(items)}** · JSON: `{json_key}`

{layers.get(layer_key, "")}

{table_header()}{rows}

→ [[../Extended layers MAX]]
""",
        )
        ext_parts.append(
            f"- [[Extended/{file_name(layer_key, title)[:-3]}|{layer_key}]] ({len(items)})"
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
method_lines += f"\n- _… {len(methods) - 20} JSON_"

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

##

{principle or "_. JSON_"}

** JSON:** {section.get("status", "—")}
"""
        if modes:
body += f"\n## / ({len(modes)})\n\n{table_header()}{rows}\n"
        body += method_lines + mod_lines
        body += "\n\n→ [[../Extended layers MAX]] · [[../00 — Taxonomy index]]\n"
write(OUT / " MAX" / file_name(layer_key, title), body)
        rich_parts.append(
            f"- [[Layers MAX/{file_name(layer_key, title)[:-3]}|{layer_key}]]"
            + (f" — {len(modes)} modes" if modes else "")
        )

    write(
        OUT / "Extended layers MAX.md",
        f"""# Extended layers MAX

v16 beyond atomic L1–L5: , , , , , , , .

## (array JSON)

{chr(10).join(ext_parts)}

## layers (nested JSON)

{chr(10).join(rich_parts)}

→ [[00 — Taxonomy index]]
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
OUT / "MAX mode universe — .md",
f"""# MAX mode universe —

: **{len(universe)}** (`max_mode_universe`).

### layer / source_layer

| layer | count |
|-------|-------|
{u_summary}

## ID

| ID | Name | layer |
|----|----------|-------|
{u_rows}

> — JSON ( ~16k ).

→ [[00 — Taxonomy index]]
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
        OUT / "Link to politic.bar v0.6.md",
        f"""# Link to politic.bar v0.6

:

| | politic.bar v0.6 | Unified v16 (this branch) |
|---|------------------|-------------------------|
| | 3× `taxonomy/*.json` | 1× `errorlogy_unified_taxonomy_v16_*.json` |
| | `politic_bar/pipeline.py` | AGIU `TaxonomyLoader` |
| -sketch | L1–L5 (+ methodology L6, GT docs) | L1–CAT, METHODS, MAX_UNIVERSE |
| (pipeline) | CB ~{pb_counts.get("cognitive_biases", "?")}, SF/MP | atomic 217 + universe 381 |

** automatically.** ID (CB-xxx, SF-xxx, MP-xxx) atomic , v16 layers Classifier.

→ [[Sources and versions]] · [[../politic.bar — sketch MVP]]
""",
    )

    print(f"Generated taxonomy branch under {OUT}")


if __name__ == "__main__":
    main()
