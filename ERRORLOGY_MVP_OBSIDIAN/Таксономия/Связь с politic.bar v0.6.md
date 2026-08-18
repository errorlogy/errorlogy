# Связь с politic.bar v0.6

Два представления одной идеи:

| | politic.bar v0.6 | Unified v16 (эта ветка) |
|---|------------------|-------------------------|
| Файлы | 3× `taxonomy/*.json` | 1× `errorlogy_unified_taxonomy_v16_*.json` |
| Пайплайн | `politic_bar/pipeline.py` | AGIU `TaxonomyLoader` |
| Слои в прод-скетче | L1–L5 (+ методология L6, GT в docs) | L1–CAT, METHODS, MAX_UNIVERSE |
| Записей (pipeline) | CB ~189, SF/MP отдельно | atomic 217 + universe 381 |

**Не мержить автоматически.** ID режимов (CB-xxx, SF-xxx, MP-xxx) должны совпадать в atomic части, но v16 добавляет слои без поддержки в старом Classifier.

→ [[Источники и версии]] · [[../politic.bar — скетч MVP]]
