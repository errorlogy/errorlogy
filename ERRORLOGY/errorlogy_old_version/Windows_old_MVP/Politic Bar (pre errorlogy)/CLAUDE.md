# Project policies — politic.bar / errorlogy

This file is loaded automatically by Claude (Cowork, Code, API).
Treat the rules below as hard constraints for any agent touching this repo.

## Canonical project location

**Only correct root:**

```
C:\Users\Public\CLAUDE_PROJECTS\Claude\Projects\POLITIC.BAR (1)
```

Linux bash mount (Cowork): `/sessions/<session-id>/mnt/Projects--POLITIC.BAR (1)/`

## Hard ban — OneDrive is forbidden

**Never** place this project — or any file belonging to it — under any
OneDrive path. This includes but is not limited to:

- `C:\Users\<user>\OneDrive\**`
- `C:\Users\<user>\OneDrive - <org>\**`
- Any path under a folder that is OneDrive-synced (Документы, Documents,
  Рабочий стол, Desktop, Изображения, Pictures when redirected by OneDrive)
- Any symlink or junction whose target resolves under OneDrive

### Why

1. OneDrive introduces async sync between Windows FS and agent sandbox
   mounts. Observed 2026-04-24: multi-hour lag between `Write` landing on
   Windows and the Linux bash mount updating; mid-sync reads returned
   truncated files (e.g. `models.py` 4155B instead of 11784B) causing
   `SyntaxError` and `JSONDecodeError` in the pipeline.
2. OneDrive file-locks intermittently block robocopy/pytest/git operations
   with "file in use" errors that have no deterministic retry window.
3. OneDrive Files-On-Demand can stub files to 0 bytes on disk; any tool
   that `read_bytes`-s without triggering hydration will see corrupt data.
4. The project's design invariant is that any checkout should produce the
   same byte-identical tree; OneDrive violates this by injecting cloud
   state into the working copy.

### If an agent detects OneDrive contamination

1. Stop any write operation in progress.
2. Report the full path that triggered the detection.
3. Propose migration to the canonical location above (one-shot robocopy
   with `/E /COPY:DAT /DCOPY:DAT /R:3 /W:5 /XJ /MT:8`).
4. Do NOT resume writes until the user confirms the new mount is live.

### Verification command

Run from repo root; must emit nothing. `CLAUDE.md` is excluded because it
is the policy file itself and legitimately names the banned paths.

```bash
grep -rniE 'onedrive|\\\\lawye\\\\|документы\\\\claude|documents\\\\claude' \
  --include='*.py' --include='*.md' --include='*.json' \
  --include='*.html' --include='*.txt' --include='*.yml' \
  --exclude='CLAUDE.md' .
```

## Path discipline inside the code

- Python modules resolve paths via `Path(__file__).resolve().parent.parent`
  or `Path(__file__).resolve().parents[N]`. No absolute Windows paths in
  source files ever.
- Test fixtures and sample data live under `cases/` and `taxonomy/`
  relative to the repo root. Never reference them by absolute path.
- Persisted pipeline outputs go to `cases/<case_id>/_pipeline/`. The
  orchestrator creates this directory; agents must not hardcode it.

## Methodology version pin

Code and prompts are currently pinned to **METHODOLOGY.md v0.6**. When
bumping to v0.7, update in lockstep:

1. `METHODOLOGY.md` headline version
2. `politic_bar/__init__.py` `__version__`
3. Docstrings in `politic_bar/models.py`, `pipeline.py`, `prompts.py`
4. `README.md` status block
5. `ARCHITECTURE.md` if pipeline shape changes

No silent version drift between methodology and code.
