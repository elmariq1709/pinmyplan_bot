# 📋 Telegram Planner Bot - Инструкция

Бот-планнер с поддержкой задач, категорий, приоритетов, сроков и напоминаний.

---

## 🚀 БЫСТРЫЙ СТАРТ (Локально)

### 1. Создай бота в Telegram

1. Найди в Telegram `@BotFather`
2. Отправь `/newbot`
3. Придумай название бота (например, "MyPlanner")
4. Придумай username (например, "my_planner_bot")
5. 🎉 Скопируй **API Token** (будет выглядеть как: `123456:ABC-DEF...`)

### 2. Установка на локальной машине (Windows)

```bash
# 1. Создай папку для проекта
mkdir telegram-planner
cd telegram-planner

# 2. Скопируй все файлы сюда:
# - planner_bot.py
# - database.py
# - config.py
# - requirements.txt
# - .env.example

# 3. Переименуй .env.example в .env
rename .env.example .env

# 4. Отредактируй .env и вставь свой токен:
# BOT_TOKEN=123456:ABC-DEF...

# 5. Установи зависимости (Python 3.12+)
pip install -r requirements.txt

# 6. Запусти бота
python planner_bot.py
```

Если всё ок, увидишь: `🚀 Бот запущен!`

### 3. Протестируй локально

1. Найди бота в Telegram (по username, который задавал)
2. Отправь `/start`
3. Попробуй кнопки:
   - ➕ Новая задача - добавь задачу
   - 📋 Мои задачи - посмотри все задачи
   - ✅ Сегодня - задачи на сегодня
   - 📊 Статус - статистика

**Готово! Бот работает локально. 🎉**

---

## ☁️ ДЕПЛОЙ НА RENDER (Бесплатный хостинг)

### Шаг 1: Подготовка

1. Создай **GitHub** аккаунт (если нет)
2. Создай новый публичный репозиторий `telegram-planner`

### Шаг 2: Загрузи код на GitHub

```bash
# В папке проекта:
git init
git add .
git commit -m "Initial commit: Telegram Planner Bot"
git remote add origin https://github.com/YOUR_USERNAME/telegram-planner.git
git push -u origin main
```

**ВАЖНО:** 
- Убедись что `.env` в `.gitignore` (не загружай реальные токены!)
- Файл `.env.example` может быть в репозитории (без настоящего токена)

### Шаг 3: Создай `.gitignore`

Создай файл `.gitignore` в корне проекта:

```
.env
planner.db
__pycache__/
*.pyc
*.pyo
.DS_Store
```

### Шаг 4: Деплой на Render

1. Перейди на **https://render.com**
2. Нажми "New" → "Web Service"
3. Выбери свой GitHub репозиторий
4. Укажи параметры:
   - **Name:** `telegram-planner`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python planner_bot.py`

5. В разделе **Environment** добавь переменные:
   - `BOT_TOKEN` = твой токен от @BotFather
   - `DATABASE_PATH` = `planner.db`

6. Нажми **Create Web Service**

⏳ Ждите 2-3 минуты деплоя...

### Шаг 5: Проверка

После деплоя:
- Найди бота в Telegram
- Отправь `/start`
- Проверь, что всё работает

✅ **Бот живёт в облаке!**

---

## 🔄 АЛЬТЕРНАТИВА: ДЕПЛОЙ НА RAILWAY

1. Перейди на **https://railway.app**
2. Нажми "New Project"
3. Выбери "Deploy from GitHub"
4. Авторизируй GitHub и выбери репозиторий
5. Добавь переменные окружения:
   - `BOT_TOKEN=твой_токен`
   - `DATABASE_PATH=planner.db`
6. Railway автоматически прочтёт `Procfile` и запустит команду

---

## 📱 КОМАНДЫ БОТА

```
/start - главное меню
/add - добавить новую задачу
/tasks - все активные задачи
/today - задачи на сегодня
/status - статистика
/complete [ID] - завершить задачу
/delete [ID] - удалить задачу
/help - справка
```

---

## 🎯 ФУНКЦИОНАЛ

✅ **Добавление задач:**
- Название
- Категория (💼 работа, 🏠 дом, 🎓 учеба, 💪 здоровье, 🎯 личное, 🛒 покупки)
- Приоритет (🔴 высокий, 🟡 средний, 🟢 низкий)
- Дата (формат: ДД.МММ.ГГГГ)
- Время (формат: ЧЧ:ММ)
- Описание

✅ **Управление:**
- Просмотр всех задач
- Просмотр задач на сегодня
- Завершение задач
- Удаление задач
- Статистика (активные/выполненные)

✅ **Сохранение данных:**
- SQLite база данных
- Все задачи сохраняются

---

## 🐛 РЕШЕНИЕ ПРОБЛЕМ

### "ModuleNotFoundError: No module named 'telegram'"
```bash
pip install python-telegram-bot
```

### "BOT_TOKEN not found"
Убедись что:
1. Создал файл `.env`
2. Вставил токен: `BOT_TOKEN=123456:ABC-DEF...`
3. Сохранил файл

### "database.db не создаётся"
Бот создаёт БД автоматически при первом запуске. Если ошибка:
1. Убедись что у папки есть права на запись
2. Удали `planner.db` если он есть
3. Запусти бота снова

### Бот не отвечает на Render
1. Проверь что BOT_TOKEN корректный
2. Посмотри логи на Render (нажми "Logs")
3. Убедись что сервис всё ещё running

---

## 💡 СОВЕТЫ

1. **Резервная копия данных:** SQLite файл `planner.db` содержит все задачи. Скачай его через Render файловую систему если нужна резервная копия.

2. **Персонализация:** Отредактируй `config.py` чтобы добавить свои категории или изменить эмодзи.

3. **Мониторинг:** На Render можешь видеть логи работы бота в реальном времени.

4. **Обновления:** Чтобы обновить бота, отправь изменения в GitHub, и Render автоматически переразвернёт.

---

## 📞 КОНТАКТЫ ПОДДЕРЖКИ

- Telegram Bot API: https://core.telegram.org/bots
- python-telegram-bot: https://github.com/python-telegram-bot/python-telegram-bot
- Render docs: https://render.com/docs

---

**Happy planning! 🚀📋**
