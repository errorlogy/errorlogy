# TZ от Claude — индекс

Здесь хранятся технические задания, которые Claude пишет для Cursor.

Соглашение:
- Один файл = один атомарный блок работы
- `status: pending` → не начато
- `status: in_progress` → Cursor взял в работу
- `status: done` → принято, проверено
- `status: rejected` → отклонено, см. комментарий

| Файл | Описание | Приоритет | Статус |
|------|----------|-----------|--------|
| [TZ-001_engine-cleanup.md](TZ-001_engine-cleanup.md) | PNO dead code, T4D keywords, EGD fallback, CAT-002 rule | 1 | done |
| [TZ-002_sqlite-persistence.md](TZ-002_sqlite-persistence.md) | SQLite для истории кейсов + /api/cases + Globe из DB | 2 | done |
| [TZ-003_seed-corpus.md](TZ-003_seed-corpus.md) | 5 seed-кейсов: Challenger, Chernobyl, Iraq WMD, Horizon, Deepwater | 3 | done |
