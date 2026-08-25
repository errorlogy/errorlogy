# Qwen Desktop — Obsidian MCP

Configured: 2026-06-18.

## Qwen Desktop configuration

| Parameter | Value |
|-----------|-------|
| File | `~/AppData/Roaming/Qwen/settings.json` (local — not in repo) |
| Key | `mcp_config` (not `mcpServers` — that is Qwen Code CLI format) |
| HTTP transport | `transportType: "httpStream"` + `url` field |

Qwen Desktop (Electron) supports three transport types:

| transportType | When to use | Fields |
|---------------|-------------|--------|
| `httpStream` | Local HTTP MCP (our case) | `url` |
| `sse` | Legacy SSE servers | `url` |
| `stdio` | Local process | `command`, `args` |

Stdio bridge **not needed** — obsidian-kimi-mcp already serves Streamable HTTP on `POST /mcp`.

## Connected vaults

| Name in Qwen | Port | Vault | Tools |
|--------------|------|-------|-------|
| `obsidian-errorlogy` | 3005 | `ERRORLOGY_MVP_OBSIDIAN` | list_vault, read_from_obsidian, save_to_obsidian, sync_kimi_session |
| `obsidian-obsidian2026` | 3002 | `OBSIDIAN2026` | same |

Separately (for Cursor, not added to Qwen): `obsidian-cursor-mcp` on port 3004 → `OBSIDIAN_CURSOR`.

## Health check (2026-06-18)

```
GET http://localhost:3002/health → ok, vault OBSIDIAN2026
GET http://localhost:3004/health → ok, vault OBSIDIAN2026 (cursor entity)
GET http://localhost:3005/health → ok, vault ERRORLOGY_MVP_OBSIDIAN
```

PM2: `obsidian-kimi-mcp`, `obsidian-cursor-mcp`, `obsidian-errorlogy-mcp` — online.

## UI: My MCP → Add MCP

To add manually via UI (**My MCP** tab → **+ Add MCP**):

### ERRORLOGY (primary)

| Field | Value |
|-------|-------|
| Name | `obsidian-errorlogy` |
| Transport / Type | HTTP Stream (`httpStream`) |
| URL | `http://localhost:3005/mcp` |

### OBSIDIAN2026 (secondary)

| Field | Value |
|-------|-------|
| Name | `obsidian-obsidian2026` |
| Transport / Type | HTTP Stream (`httpStream`) |
| URL | `http://localhost:3002/mcp` |

For stdio (if HTTP unavailable in UI) — not recommended; use JSON below.

## JSON (already written to settings.json)

```json
{
  "mcp_config": {
    "obsidian-errorlogy": {
      "transportType": "httpStream",
      "url": "http://localhost:3005/mcp"
    },
    "obsidian-obsidian2026": {
      "transportType": "httpStream",
      "url": "http://localhost:3002/mcp"
    }
  }
}
```

After changes — **restart Qwen Desktop** (MCP settings load at startup).

## Infrastructure

| Component | Path |
|-----------|------|
| MCP server | `<local-path>/obsidian-kimi-mcp/server.js` |
| PM2 registry | `<local-path>/mcp-servers.json` |
| Ecosystem | `<local-path>/mcp-ecosystem.config.cjs` |
| Cluster start | `<local-path>/obsidian-kimi-mcp/start-server.bat` |

New instance `obsidian-errorlogy-mcp` (port 3005) added to `mcp-servers.json`:

- `OBSIDIAN_VAULT`: `<repo-root>/ERRORLOGY_MVP_OBSIDIAN`
- `OBSIDIAN_DEFAULT_SUBFOLDER`: `Qwen/Generated`
- `MCP_ENTITY`: `qwen`

Start ERRORLOGY instance only:

```bat
cd <local-mcp-dir>
pm2 start mcp-ecosystem.config.cjs --only obsidian-errorlogy-mcp
pm2 save
```

## Qwen Code CLI (separate)

CLI uses a different file: `~/.qwen/settings.json`, key `mcpServers`, field `httpUrl`.

```bash
qwen mcp add --scope user --transport http obsidian-errorlogy http://localhost:3005/mcp
qwen mcp list
```

## Chat verification

After restarting Qwen, ask: "use obsidian-errorlogy, call list_vault" or "read For AI agents.md from Obsidian".
