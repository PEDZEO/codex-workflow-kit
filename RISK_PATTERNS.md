# RISK_PATTERNS.md

Используй как короткий список типовых регрессий после изменений.

## Common Risks

- Config drift
  - код изменен, но env/config/schema не обновлены

- Contract drift
  - API, callback, event payload или response shape изменились не полностью

- Import/path breakage
  - файл переместили или переименовали, но зависимости не обновили

- Pagination/filter regressions
  - работает первый экран, но ломаются `next/prev`, фильтры или возврат в список

- Type/schema mismatch
  - runtime и типы/схемы расходятся

- Partial refactor
  - основной код обновлен, а соседние вызовы или тесты остались старыми

- Silent behavior change
  - код проходит, но поведение изменилось без явного решения

- Missing negative path
  - happy path покрыт, а edge cases и ошибки забыты

## Review Questions

- Не изменился ли внешний контракт?
- Не остался ли старый формат callback, route или response?
- Не затронута ли пагинация, фильтрация или возвратный переход?
- Не нужен ли update config, docs или tests?
- Не остались ли старые вызовы после точечного рефактора?

## Use

После любого изменения пройдись по релевантным рискам, а не по всему списку.
