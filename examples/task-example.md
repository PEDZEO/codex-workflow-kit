# Example Task Brief

## Task

Починить пагинацию списка сессий в Telegram-боте без изменения остальной навигации.

## Good Local Plan

- Прочитать `CODEBASE_INDEX.md` и `current-task.md`.
- Найти callback handlers и keyboard builders по `sessions`.
- Найти тесты, связанные с pagination и navigation.
- Локально держать критический путь: обработчики и callback flow.
- Отдать агенту `explorer` только поиск релевантных тестов, если это не блокирует следующий шаг.

## Good Delegated Task

- Role: `worker`
- Objective: обновить только построение клавиатуры для `sessions`
- Owned files: `bot/keyboards/sessions.py`
- Out of scope: `bot/handlers/`, `server/`, общие navigation helper'ы
- Done criteria: кнопки `prev/next` работают корректно, формат callback не ломает совместимость
- Return format: changed files, summary, risks, verification

## Good Memory Update

- Подтверждено, что ошибка находится в keyboard builder, а не в handler.
- Навигационный helper уже поддерживает page-aware callbacks.
- Следующий шаг: исправить builder и прогнать точечные тесты по sessions/navigation.
