# Статус репозитория — OLD SKETCH

> Эта заметка про **архив** `errorlogy_old_version/`.  
> Активный MVP: [[errorlogy-mas — активный MVP (Claude)]] (`errorlogy-mas/`, `errorlogy-gui/`).

## Решение

Материалы в `ERRORLOGY/errorlogy_old_version/` — **архив идей и скетчей**, а не текущий продукт.

| Метка | Значение |
|-------|----------|
| **OLD** | Историческая версия, не поддерживается как prod |
| **SKETCH** | Прототип для проработки концепции и онтологии |

## Что это значит на практике

1. **Новый код** по умолчанию не кладём в `errorlogy_old_version/` — только если явно попросили.
2. **Таксономии** `errorlogy_unified_taxonomy_v*.json` — черновики онтологии; v16 самый полный, но не замороженный контракт API.
3. **politic.bar** в `Windows_old_MVP/` — эталон методологии и seed-кейсов, не обязательная база для новой реализации.
4. **AGIU** — заготовка (health + demo analytics), не «готовая платформа».
5. **Секреты** в старых папках (например `anthropic_api_key.txt`) не использовать и не коммитить.

## Где зафиксировано в коде

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

## Следующий продукт

Когда начнётся «настоящая» разработка — отдельная папка или ветка; в этой заметке можно добавить ссылку на новый root.

→ [[00 — Главная]] · [[Для AI-агентов]]

#old-sketch #meta
