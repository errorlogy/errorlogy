# Contributing

Thank you for contributing to Errorlogy. This monorepo mixes **active product code**,
**research experiments**, and **historical sketches** — route changes to the right zone.

## Where to work

| Label | Paths | When to edit |
|-------|-------|--------------|
| **ACTIVE** | `errorlogy-mas/`, `errorlogy-gui/`, `errorlogy-gui-v2/` | Default for features, API, UI |
| **RESEARCH** | `errorlogy-trn-sim/` | Synthetic simulation only — not the 14-agent pipeline |
| **OLD SKETCH** | `ERRORLOGY/errorlogy_old_version/` | Reference / retrospective — only when explicitly asked |
| **Docs vault** | `ERRORLOGY_MVP_OBSIDIAN/` | Concept notes — not runtime source of truth |

Read `AGENTS.md` (root) and `errorlogy-mas/AGENTS.md` before editing MAS code.

## Umbrella integration

Institutional topology and JSON schema contracts live in
[ai-native-gov](https://github.com/errorlogy/ai-native-gov). Runtime implementations belong here;
copy schema changes from umbrella into `errorlogy-mas/schemas/` when contracts update.

## Development setup

```bash
cd errorlogy-mas
python -m venv .venv && source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env                                 # local only — never commit
pytest tests/ -m "not llm_eval"
python api/main.py
```

## Pull requests

- One logical change per PR when possible.
- Run `pytest tests/` in `errorlogy-mas/` (exclude live LLM evals unless you intend them).
- Do not commit `.env`, API keys, or personal machine paths.
- Use non-accusatory language in user-facing copy (see `errorlogy-mas/AGENTS.md`).

## License

By contributing, you agree that your contributions are licensed under the
Creative Commons Attribution 4.0 International License (CC BY 4.0) (see `LICENSE`).
