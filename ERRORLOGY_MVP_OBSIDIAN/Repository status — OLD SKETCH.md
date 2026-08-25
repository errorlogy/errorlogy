# Repository status — OLD SKETCH

> This note covers the **archive** `errorlogy_old_version/`.  
> Active MVP: [[errorlogy-mas — active MVP (Claude)]] (`errorlogy-mas/`, `errorlogy-gui/`).

## Decision

Materials in `ERRORLOGY/errorlogy_old_version/` are an **archive of ideas and sketches**, not the current product.

| Label | Meaning |
|-------|---------|
| **OLD** | Historical version, not maintained as prod |
| **SKETCH** | Prototype for concept and ontology exploration |

## Practical implications

1. **New code** does not go into `errorlogy_old_version/` by default — only when explicitly requested.
2. **Taxonomies** `errorlogy_unified_taxonomy_v*.json` — ontology drafts; v16 is the most complete but not a frozen API contract.
3. **politic.bar** in `Windows_old_MVP/` — methodology and seed-case reference, not mandatory base for new implementation.
4. **AGIU** — stub (health + demo analytics), not a "ready platform".
5. **Secrets** in old folders (e.g. `anthropic_api_key.txt`) — do not use or commit.

## Where documented in code

```
ERRORLOGY_MVP/
├── README.md
├── AGENTS.md
├── .cursor/rules/errorlogy-archive.mdc
└── ERRORLOGY/errorlogy_old_version/
    ├── README.md
    ├── AGIU/README.md
    ├── Windows_old_MVP/README.md
    └── Cursor_Project/README.md
```

## Next product

When "real" development starts — separate folder or branch; add link to new root in this note.

→ [[00 — Home]] · [[For AI agents]]

#old-sketch #meta
