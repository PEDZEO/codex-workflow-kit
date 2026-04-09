# SEARCH_PLAYBOOK.md

Используй как шпаргалку, чтобы не начинать поиск с хаотичного чтения дерева.

## Base Rules

- Сначала `CODEBASE_INDEX.md`, потом поиск.
- Сначала `rg --files`, потом `rg`.
- Сначала точечные кандидаты, потом чтение.
- Не открывай большие файлы полностью без подтвержденной причины.

## Common Search Patterns

### Найти entrypoint

```powershell
rg --files -g "*main*" -g "*app*" -g "*server*" -g "*index*"
```

### Найти роуты или обработчики

```powershell
rg "router|route|endpoint|handler|callback" .
```

### Найти конфиг или ключ настройки

```powershell
rg "SETTING_NAME|ENV_NAME|config_key" .
```

### Найти реализацию функции или символа

```powershell
rg "function_name|ClassName|symbol_name" .
```

### Найти связанные тесты

```powershell
rg "feature_name|handler_name|route_name" tests
```

### Найти точки интеграции

```powershell
rg "client|service|repository|notifier|publisher|consumer" .
```

## Search Sequence

1. Найти кандидатов по именам файлов.
2. Найти прямые упоминания символа или фичи.
3. Найти тесты по тому же ключевому слову.
4. Прочитать минимальный набор файлов.
5. Зафиксировать вывод в памяти.

## Stop Conditions

Остановить поиск и перейти к работе, если:

- найден entrypoint;
- найден основной обработчик;
- найден связанный тест или подтверждено его отсутствие;
- понятна зона изменения.
