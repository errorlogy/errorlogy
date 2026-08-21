# Cross-layer schemas (vendored)

Copies of AI Native Gov umbrella contracts for offline reference / future JSON Schema validation.

**Runtime consumer (MVP iter 1):** `mas.institutional.activation` — hardcoded enum + stub router; this folder is not imported yet.

**Prefer live umbrella path** via env:

```text
AI_NATIVE_GOV_SCHEMAS=C:\Users\Public\AI_NATIVE_GOV\schemas
```

or `CROSS_LAYER_SCHEMA_DIR`. When unset, prefer the Public sibling `AI_NATIVE_GOV/schemas`, then this directory.

Source of truth: https://github.com/errorlogy/ai-native-gov/tree/main/schemas

Do not treat these files as a new taxonomy; sync from umbrella when layer IDs change.

