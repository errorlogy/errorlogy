# Cross-layer schemas (vendored)

Copies of AI Native Gov umbrella contracts for offline reference / future JSON Schema validation.

**Runtime consumer (MVP iter 1–3):** `mas.institutional.activation` — hardcoded enum + stub router; this folder is not imported yet.

| File | Phase | Notes |
|------|-------|-------|
| `cross-layer-event.json` | iter 1 + Phase A | Institutional envelope; fin_crypto + memetic `event_type` examples |
| `signal-envelope.json` | Phase A | Graded stream item + `memetic_metrics` half-life fields |
| `institution-layer-id.json` | iter 1 | Layer enum |

**Prefer live umbrella path** via env:

```text
AI_NATIVE_GOV_SCHEMAS=C:\Users\Public\AI_NATIVE_GOV\schemas
```

or `CROSS_LAYER_SCHEMA_DIR`. When unset, prefer the Public sibling `AI_NATIVE_GOV/schemas`, then this directory.

Source of truth: https://github.com/errorlogy/ai-native-gov/tree/main/schemas

Do not treat these files as a new taxonomy; sync from umbrella when layer IDs or Phase A memetic contracts change.
