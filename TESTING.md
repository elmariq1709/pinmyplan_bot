# 🧪 Руководство по локальному тестированию

## Предварительная настройка

### 1. Установка Python 3.12 (рекомендуется)

**Windows:**
- Скачай с https://www.python.org/downloads/
- При установке галочка ✅ "Add Python to PATH"
- После установки проверь версию:
```bash
python --version
```

### 2. Создание виртуального окружения (опционально, но рекомендуется)

```bash
# Создай виртуальное окружение
python -m venv venv

# Активируй его
# На Windows:
venv\Scripts\activate

# На Linux/Mac:
source venv/bin/activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

Если есть проблемы с `python-telegram-bot`, установи отдельно:
```bash
pip install python-telegram-bot==21.0.1
pip install python-dotenv==1.0.0
```

---

## Получение BOT_TOKEN

### Шаг 1: BotFather в Telegram

1. Откройте Telegram
2. Найдите `@BotFather` (официальный бот для создания ботов)
3. Отправьте команду `/newbot`
4. Следуйте инструкциям:
   - Введите имя бота (например: "MyPlanner")
   - Введите username (должен заканчиваться на "_bot", например: "my_planner_bot")

### Шаг 2: Получение токена

BotFather вернёт сообщение вида:
```
Done! Congratulations on your new bot. You will find it at t.me/my_planner_bot. 
You can now add a description, about section and profile picture for your bot, see /help for a list of commands. By the way, when you've finished with your boring bot, remember that you can always create a list of commands, see /help_force_reply for a heavy armour example.

Use this token to access the HTTP API:
123456789:ABCDEFGhijklmnoPQRstuvwxyz_12345

For a description of the Bot API, see this page: https://core.telegram.org/bots/api
```

**Скопируй токен (строка вида `123456789:ABCDEFGhijklmnoPQRstuvwxyz_12345`)**

---

## Настройка .env файла

### 1. Создай файл `.env`

В корне проекта создай новый файл `.env`:

```
BOT_TOKEN=123456789:ABCDEFGhijklmnoPQRstuvwxyz_12345
DATABASE_PATH=planner.db
```

**⚠️ ВАЖНО:**
- Не загружай `.env` на GitHub (используй `.gitignore`)
- Никому не показывай токен - это как пароль к боту

### 2. Проверка структуры папки

```
telegram-planner/
├── .env                # ← Вставь сюда токен
├── .env.example        # Пример (без настоящего токена)
├── .gitignore          # Git ignore (защитит .env)
├── planner_bot.py      # Основной бот
├── database.py         # БД
├── config.py           # Конфиг
├── requirements.txt    # Зависимости
└── README.md
```

---

## Запуск и первое тестирование

### 1. Запустите бота

```bash
python planner_bot.py
```

Если всё ок, видишь:
```
2024-12-15 14:30:45,123 - telegram.ext.application - INFO - Initializing application
2024-12-15 14:30:46,456 - telegram.ext.application - INFO - Application initialized
2024-12-15 14:30:47,789 - root - INFO - 🚀 Бот запущен!
```

### 2. Протестируй в Telegram

1. Найди своего бота через поиск (по username, например `@my_planner_bot`)
2. Начни чат и отправь `/start`
3. Должен получить главное меню

### 3. Тестовые сценарии

#### Сценарий 1: Добавление задачи
```
Нажми: ➕ Новая задача
Введи: "Купить молоко"
Выбери категорию: 🛒 (покупки)
Выбери приоритет: 🟢 (низкий)
Пропусти дату
Пропусти время
Пропусти описание
Результат: ✅ Задача добавлена!
```

#### Сценарий 2: Просмотр задач
```
Нажми: 📋 Мои задачи
Результат: Должна отобразиться добавленная задача с ID
```

#### Сценарий 3: Завершение задачи
```
Отправь: /complete 1
Результат: ✅ Задача завершена!
```

#### Сценарий 4: Удаление задачи
```
Отправь: /delete 1
Результат: 🗗 Задача удалена!
```

#### Сценарий 5: Статус
```
Нажми: 📊 Статус
Результат: Должна показать статистику
```

---

## Отладка и проверка

### 1. Проверка логов

При запуске бота видишь логи - это помогает найти ошибки:

```
ERROR: 'config' - config.py - No module named 'telegram'
```
→ Нужно установить: `pip install python-telegram-bot`

```
ERROR: BOT_TOKEN is None
```
→ Проверь `.env` файл, правильно ли вставлен токен

### 2. Проверка БД

После добавления первой задачи в папке должен появиться файл `planner.db`.

Если нужно проверить содержимое БД:
```bash
# Установи sqlite3 (обычно идёт с Python)
python

# В Python консоли:
import sqlite3
conn = sqlite3.connect('planner.db')
cursor = conn.cursor()
cursor.execute('SELECT * FROM tasks')
print(cursor.fetchall())
```

### 3. Очистка между тестами

Если нужно очистить все задачи и начать с нуля:
```bash
# Просто удали файл
del planner.db

# Или в Python:
import os
os.remove('planner.db')
```

При следующем запуске БД создастся заново пустой.

---

## Частые ошибки и решения

### ❌ "ModuleNotFoundError: No module named 'telegram'"
**Решение:**
```bash
pip install python-telegram-bot==21.0.1
```

### ❌ "No such file or directory: '.env'"
**Решение:** 
1. Создай файл `.env` в корне проекта
2. Вставь: `BOT_TOKEN=твой_токен`

### ❌ "BOT_TOKEN is None"
**Решение:**
1. Проверь что `.env` создан
2. Проверь что в нём есть: `BOT_TOKEN=123456...`
3. Не должно быть пробелов: `BOT_TOKEN = ...` ❌, `BOT_TOKEN=...` ✅

### ❌ Бот не отвечает на сообщения
**Решение:**
1. Проверь что токен правильный (скопируй с BotFather снова)
2. Посмотри консоль - может быть ошибка
3. Перезагрузи бота (Ctrl+C и заново `python planner_bot.py`)

### ❌ "sqlite3.IntegrityError: UNIQUE constraint failed"
**Решение:**
Попробался добавить задачу с тем же названием и датой. Измени название или дату.

---

## Профессиональные советы

### 1. Использование виртуального окружения

Всегда используй `venv`:
```bash
python -m venv venv
venv\Scripts\activate  # Windows

# Или на Linux/Mac:
source venv/bin/activate

# Затем установи зависимости
pip install -r requirements.txt
```

Плюсы:
- Зависимости изолированы
- Не конфликтуют с другими проектами
- Легче деплоить

### 2. Отладочный режим

Добавь в `planner_bot.py` после `logger.basicConfig`:
```python
import sys
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)  # Больше логов
```

### 3. Тестирование разных сценариев

Создай тестового юзера и:
- Добавь 5 задач с разными приоритетами
- Добавь задачи с разными категориями
- Проверь сортировку (высокий приоритет сверху)
- Добавь описания и проверь отображение

### 4. Резервная копия БД

Перед деплоем скопируй `planner.db`:
```bash
copy planner.db planner_backup.db
```

---

## Готовность к деплою

Перед тем как деплоить на облако, убедись что:

- ✅ Локально бот работает без ошибок
- ✅ Все команды работают: `/start`, `/add`, `/tasks`, `/complete`, `/delete`
- ✅ БД создаётся и сохраняет данные
- ✅ `.env` с токеном не загружен на GitHub
- ✅ `.gitignore` содержит `.env` и `planner.db`
- ✅ `requirements.txt` содержит все зависимости
- ✅ `Procfile` присутствует для деплоя

**Если всё ок → Можно деплоить! 🚀**

Для деплоя смотри [DEPLOY.md](./DEPLOY.md)
