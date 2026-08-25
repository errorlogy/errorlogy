# politic.bar (pre-Errorlogy) — Claude notes

> **STATUS: OLD SKETCH**

## Path hygiene

- Any path under a OneDrive-synced folder (Documents, Desktop, Pictures when redirected by OneDrive)
- Avoid syncing dev secrets or API keys

```bash
grep -rniE 'onedrive|documents\\claude' . 2>/dev/null || true
```

Use repo-local paths only. See `errorlogy-mas/.env.example` for keys (gitignored).
