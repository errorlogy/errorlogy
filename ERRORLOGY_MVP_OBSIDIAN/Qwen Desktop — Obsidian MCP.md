# Qwen Desktop — Obsidian MCP

Настроено: 2026-06-18.

## Конфигурация Qwen Desktop

| Параметр | Значение |
|----------|----------|
| Файл | `~/AppData/Roaming/Qwen/settings.json` (local — not in repo) |
| Ключ | `mcp_config` (не `mcpServers` — это формат Qwen Code CLI) |
| Транспорт HTTP | `transportType: "httpStream"` + поле `url` |

Qwen Desktop (Electron) поддерживает три типа транспорта:

| transportType | Когда использовать | Поля |
|---------------|-------------------|------|
| `httpStream` | Локальные HTTP MCP (наш случай) | `url` |
| `sse` | Legacy SSE-серверы | `url` |
| `stdio` | Локальный процесс | `command`, `args` |

Stdio-мост **не нужен** — obsidian-kimi-mcp уже отдаёт Streamable HTTP на `POST /mcp`.

## Подключённые валюты

| Имя в Qwen | Порт | Валют | Инструменты |
|------------|------|-------|-------------|
| `obsidian-errorlogy` | 3005 | `ERRORLOGY_MVP_OBSIDIAN` | list_vault, read_from_obsidian, save_to_obsidian, sync_kimi_session |
| `obsidian-obsidian2026` | 3002 | `OBSIDIAN2026` | те же |

Отдельно (для Cursor, не добавлен в Qwen): `obsidian-cursor-mcp` на порту 3004 → `OBSIDIAN_CURSOR`.

## Health check (2026-06-18)

```
GET http://localhost:3002/health → ok, vault OBSIDIAN2026
GET http://localhost:3004/health → ok, vault OBSIDIAN2026 (cursor entity)
GET http://localhost:3005/health → ok, vault ERRORLOGY_MVP_OBSIDIAN
```

PM2: `obsidian-kimi-mcp`, `obsidian-cursor-mcp`, `obsidian-errorlogy-mcp` — online.

## UI: My MCP → Add MCP

Если нужно добавить вручную через интерфейс (вкладка **My MCP** → **+ Add MCP**):

### ERRORLOGY (основной)

| Поле | Значение |
|------|----------|
| Name | `obsidian-errorlogy` |
| Transport / Type | HTTP Stream (`httpStream`) |
| URL | `http://localhost:3005/mcp` |

### OBSIDIAN2026 (дополнительный)

| Поле | Значение |
|------|----------|
| Name | `obsidian-obsidian2026` |
| Transport / Type | HTTP Stream (`httpStream`) |
| URL | `http://localhost:3002/mcp` |

Для stdio (если HTTP недоступен в UI) — не рекомендуется; используйте JSON ниже.

## JSON (уже записан в settings.json)

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

После изменения — **перезапустить Qwen Desktop** (настройки MCP загружаются при старте).

## Инфраструктура

| Компонент | Путь |
|-----------|------|
| MCP-сервер | `<local-path>/obsidian-kimi-mcp/server.js` |
| Реестр PM2 | `<local-path>/mcp-servers.json` |
| Ecosystem | `<local-path>/mcp-ecosystem.config.cjs` |
| Старт кластера | `<local-path>/obsidian-kimi-mcp/start-server.bat` |

Новый инстанс `obsidian-errorlogy-mcp` (порт 3005) добавлен в `mcp-servers.json`:

- `OBSIDIAN_VAULT`: `<repo-root>/ERRORLOGY_MVP_OBSIDIAN`
- `OBSIDIAN_DEFAULT_SUBFOLDER`: `Qwen/Generated`
- `MCP_ENTITY`: `qwen`

Запуск только ERRORLOGY-инстанса:

```bat
cd <local-mcp-dir>
pm2 start mcp-ecosystem.config.cjs --only obsidian-errorlogy-mcp
pm2 save
```

## Qwen Code CLI (отдельно)

CLI использует другой файл: `~/.qwen/settings.json`, ключ `mcpServers`, поле `httpUrl`.

```bash
qwen mcp add --scope user --transport http obsidian-errorlogy http://localhost:3005/mcp
qwen mcp list
```

## Проверка в чате

После перезапуска Qwen попросите: «используй obsidian-errorlogy, вызови list_vault» или «прочитай файл Для AI-агентов.md из Obsidian».
