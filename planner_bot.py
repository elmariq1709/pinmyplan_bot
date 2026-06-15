import logging
import sqlite3
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, filters, ContextTypes
)
from config import BOT_TOKEN, CATEGORIES, PRIORITIES, DATE_FORMAT, DATETIME_FORMAT
from database import Database

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# States for conversations
ADD_TITLE, ADD_CATEGORY, ADD_PRIORITY, ADD_DATE, ADD_TIME, ADD_DESCRIPTION = range(6)

# Database
db = Database()

# ==================== HELPER FUNCTIONS ====================

def get_priority_emoji(priority: str) -> str:
    """Получить emoji по приоритету"""
    for emoji, prio in PRIORITIES.items():
        if prio == priority:
            return emoji
    return '🟡'

def get_category_emoji(category: str) -> str:
    """Получить emoji по категории"""
    for emoji, cat in CATEGORIES.items():
        if cat == category:
            return emoji
    return '📋'

def format_task(task: dict) -> str:
    """Форматировать задачу для отображения"""
    title = task['title']
    priority_emoji = get_priority_emoji(task['priority'])
    category_emoji = get_category_emoji(task['category']) if task['category'] else '📋'
    
    text = f"{priority_emoji} {category_emoji} • {title}"
    
    if task['due_date']:
        text += f"\n📅 {task['due_date']}"
    
    if task['due_time']:
        text += f" ⏰ {task['due_time']}"
    
    if task['description']:
        text += f"\n📝 {task['description']}"
    
    return text

def get_main_keyboard():
    """Получить главное меню"""
    return ReplyKeyboardMarkup([
        ['➕ Новая задача', '📋 Мои задачи'],
        ['✅ Сегодня', '📊 Статус'],
        ['❓ Помощь']
    ], resize_keyboard=True)

def get_category_keyboard():
    """Получить клавиатуру выбора категории"""
    buttons = [[]]
    for i, (emoji, category) in enumerate(CATEGORIES.items()):
        buttons[-1].append(f"{emoji}")
        if (i + 1) % 3 == 0:
            buttons.append([])
    
    buttons.append(['Без категории', '⬅️ Отмена'])
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

def get_priority_keyboard():
    """Получить клавиатуру выбора приоритета"""
    buttons = [[emoji for emoji in PRIORITIES.keys()]]
    buttons.append(['⬅️ Отмена'])
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

# ==================== COMMAND HANDLERS ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    user = update.effective_user
    await update.message.reply_text(
        f"👋 Привет, {user.first_name}!\n\n"
        f"Я бот-планнер, помогу организовать твои дела.\n\n"
        f"Используй кнопки ниже или команды:\n"
        f"/help - справка\n"
        f"/tasks - все задачи\n"
        f"/today - задачи на сегодня\n"
        f"/add - добавить задачу",
        reply_markup=get_main_keyboard()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help"""
    help_text = """
📋 *КОМАНДЫ БОТА:*
/start - главное меню
/add - добавить новую задачу
/tasks - показать все активные задачи
/today - задачи на сегодня
/status - статистика
/help - эта справка

🎯 *КАК ИСПОЛЬЗОВАТЬ:*
1. Нажми "➕ Новая задача" или используй /add
2. Введи название задачи
3. Выбери категорию (опционально)
4. Выбери приоритет
5. Укажи дату (опционально)
6. Укажи время (опционально)
7. Добавь описание (опционально)

✅ *ПРИОРИТЕТЫ:*
🔴 - высокий
🟡 - средний
🟢 - низкий

🏷️ *КАТЕГОРИИ:*
💼 - работа
🏠 - дом
🎓 - учеба
💪 - здоровье
🎯 - личное
🛒 - покупки
"""
    await update.message.reply_text(help_text, reply_markup=get_main_keyboard())

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /status"""
    user_id = update.effective_user.id
    active, completed = db.get_tasks_count(user_id)
    daily_stats = db.get_daily_stats(user_id)
    
    # Прогресс-бар
    percentage = daily_stats['percentage']
    bar_length = 10
    filled = int(bar_length * percentage / 100)
    bar = '█' * filled + '░' * (bar_length - filled)
    
    text = f"""
📊 *ОБЩАЯ СТАТИСТИКА:*
✅ Выполнено: {completed}
📌 Активных: {active}
━━━━━━━━━━━━━━
📈 Итого: {active + completed}

📅 *СЕГОДНЯШНЯЯ СТАТИСТИКА:*
Задач на сегодня: {daily_stats['total']}
Выполнено: {daily_stats['completed']}
Прогресс: [{bar}] {percentage}%
"""
    await update.message.reply_text(text, reply_markup=get_main_keyboard())

# ==================== ADD TASK CONVERSATION ====================

async def add_task_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало добавления задачи"""
    await update.message.reply_text(
        "📝 Введи название задачи:\n\n(или нажми /cancel чтобы отменить)",
        reply_markup=ReplyKeyboardMarkup([['⬅️ Отмена']], resize_keyboard=True)
    )
    return ADD_TITLE

async def add_task_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получить название задачи"""
    title = update.message.text
    
    if title == '⬅️ Отмена':
        await update.message.reply_text("❌ Отменено", reply_markup=get_main_keyboard())
        return ConversationHandler.END
    
    context.user_data['task_title'] = title
    await update.message.reply_text(
        "🏷️ Выбери категорию:",
        reply_markup=get_category_keyboard()
    )
    return ADD_CATEGORY

async def add_task_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получить категорию"""
    text = update.message.text
    
    if text == '⬅️ Отмена':
        await update.message.reply_text("❌ Отменено", reply_markup=get_main_keyboard())
        return ConversationHandler.END
    
    category = None
    if text != 'Без категории':
        for emoji, cat in CATEGORIES.items():
            if emoji == text:
                category = cat
                break
    
    context.user_data['task_category'] = category
    await update.message.reply_text(
        "⚡ Выбери приоритет:",
        reply_markup=get_priority_keyboard()
    )
    return ADD_PRIORITY

async def add_task_priority(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получить приоритет"""
    emoji = update.message.text
    
    if emoji == '⬅️ Отмена':
        await update.message.reply_text("❌ Отменено", reply_markup=get_main_keyboard())
        return ConversationHandler.END
    
    priority = PRIORITIES.get(emoji, 'medium')
    context.user_data['task_priority'] = priority
    
    keyboard = [
        ['📅 Сегодня', '📅 Завтра'],
        ['✍️ Ввести дату', '⬅️ Пропустить']
    ]
    
    await update.message.reply_text(
        "📅 Выбери дату или ввести вручную:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return ADD_DATE

async def add_task_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получить дату"""
    text = update.message.text
    
    if text == '⬅️ Отмена':
        await update.message.reply_text("❌ Отменено", reply_markup=get_main_keyboard())
        return ConversationHandler.END
    
    due_date = None
    
    if text == '📅 Сегодня':
        due_date = datetime.now().strftime(DATE_FORMAT)
    elif text == '📅 Завтра':
        due_date = (datetime.now() + timedelta(days=1)).strftime(DATE_FORMAT)
    elif text == '✍️ Ввести дату':
        await update.message.reply_text(
            "📅 Введи дату (ДД.МММ.ГГГГ):\n\n(например: 15.12.2024)",
            reply_markup=ReplyKeyboardMarkup([['⬅️ Отмена']], resize_keyboard=True)
        )
        context.user_data['waiting_for_manual_date'] = True
        return ADD_DATE
    elif text == '⬅️ Пропустить':
        due_date = None
    elif context.user_data.get('waiting_for_manual_date'):
        try:
            datetime.strptime(text, DATE_FORMAT)
            due_date = text
            context.user_data['waiting_for_manual_date'] = False
        except ValueError:
            await update.message.reply_text(
                "❌ Неверный формат. Используй ДД.МММ.ГГГГ (например: 15.12.2024)"
            )
            return ADD_DATE
    else:
        await update.message.reply_text(
            "❌ Выбери один из вариантов или нажми ⬅️ Отмена"
        )
        return ADD_DATE
    
    context.user_data['task_date'] = due_date
    
    await update.message.reply_text(
        "⏰ Укажи время (ЧЧ:ММ) или пропусти:",
        reply_markup=ReplyKeyboardMarkup([
            ['Пропустить'],
            ['⬅️ Отмена']
        ], resize_keyboard=True)
    )
    return ADD_TIME

async def add_task_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получить время"""
    text = update.message.text
    
    if text == '⬅️ Отмена':
        await update.message.reply_text("❌ Отменено", reply_markup=get_main_keyboard())
        return ConversationHandler.END
    
    due_time = None
    if text != 'Пропустить':
        try:
            datetime.strptime(text, '%H:%M')
            due_time = text
        except ValueError:
            await update.message.reply_text(
                "❌ Неверный формат. Используй ЧЧ:ММ (например: 14:30)"
            )
            return ADD_TIME
    
    context.user_data['task_time'] = due_time
    
    await update.message.reply_text(
        "📝 Добавь описание (опционально) или пропусти:",
        reply_markup=ReplyKeyboardMarkup([
            ['Пропустить'],
            ['⬅️ Отмена']
        ], resize_keyboard=True)
    )
    return ADD_DESCRIPTION

async def add_task_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получить описание и сохранить задачу"""
    text = update.message.text
    
    if text == '⬅️ Отмена':
        await update.message.reply_text("❌ Отменено", reply_markup=get_main_keyboard())
        return ConversationHandler.END
    
    description = None if text == 'Пропустить' else text
    context.user_data['task_description'] = description
    
    # Сохраняем задачу
    user_id = update.effective_user.id
    success = db.add_task(
        user_id=user_id,
        title=context.user_data['task_title'],
        category=context.user_data['task_category'],
        priority=context.user_data['task_priority'],
        due_date=context.user_data['task_date'],
        due_time=context.user_data['task_time'],
        description=description
    )
    
    if success:
        await update.message.reply_text(
            "✅ Задача добавлена!",
            reply_markup=get_main_keyboard()
        )
    else:
        await update.message.reply_text(
            "⚠️ Такая задача уже существует или произошла ошибка.",
            reply_markup=get_main_keyboard()
        )
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена разговора"""
    await update.message.reply_text("❌ Отменено", reply_markup=get_main_keyboard())
    return ConversationHandler.END

# ==================== SHOW TASKS ====================

async def show_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать все активные задачи с кнопками"""
    user_id = update.effective_user.id
    tasks = db.get_all_tasks(user_id, completed=False)
    
    if not tasks:
        await update.message.reply_text(
            "📭 У тебя нет активных задач!",
            reply_markup=get_main_keyboard()
        )
        return
    
    await update.message.reply_text("Вот твой список задач: 👇")
    
    for task in tasks:
        text = format_task(task)
        
        keyboard = [
            [
                InlineKeyboardButton("✅ Завершить", callback_data=f'complete_{task["id"]}'),
                InlineKeyboardButton("❌ Удалить", callback_data=f'delete_{task["id"]}')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="HTML")

async def show_today_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать задачи на сегодня с кнопками"""
    user_id = update.effective_user.id
    tasks = db.get_today_tasks(user_id)
    
    if not tasks:
        await update.message.reply_text(
            "🎉 Все задачи на сегодня выполнены!",
            reply_markup=get_main_keyboard()
        )
        return
    
    await update.message.reply_text("📅 *ЗАДАЧИ НА СЕГОДНЯ:*", parse_mode="HTML")
    
    for task in tasks:
        text = format_task(task)
        
        keyboard = [
            [
                InlineKeyboardButton("✅ Завершить", callback_data=f'complete_{task["id"]}'),
                InlineKeyboardButton("❌ Удалить", callback_data=f'delete_{task["id"]}')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="HTML")

# ==================== COMPLETE/DELETE ====================

async def complete_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Завершить задачу (для /complete команды)"""
    try:
        task_id = int(context.args[0])
        if db.complete_task(task_id):
            await update.message.reply_text(
                "✅ Задача завершена!",
                reply_markup=get_main_keyboard()
            )
        else:
            await update.message.reply_text(
                "❌ Задача не найдена",
                reply_markup=get_main_keyboard()
            )
    except (IndexError, ValueError):
        await update.message.reply_text(
            "❌ Используй: /complete [ID задачи]",
            reply_markup=get_main_keyboard()
        )

async def delete_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Удалить задачу (для /delete команды)"""
    try:
        task_id = int(context.args[0])
        if db.delete_task(task_id):
            await update.message.reply_text(
                "🗑️ Задача удалена!",
                reply_markup=get_main_keyboard()
            )
        else:
            await update.message.reply_text(
                "❌ Задача не найдена",
                reply_markup=get_main_keyboard()
            )
    except (IndexError, ValueError):
        await update.message.reply_text(
            "❌ Используй: /delete [ID задачи]",
            reply_markup=get_main_keyboard()
        )

# ==================== BUTTON CALLBACK ====================

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопок завершения и удаления"""
    query = update.callback_query
    data = query.data
    
    await query.answer()
    
    try:
        if data.startswith('complete_'):
            task_id = int(data.split('_')[1])
            if db.complete_task(task_id):
                await query.edit_message_text(
                    text="✅ Задача завершена!",
                    parse_mode="HTML"
                )
            else:
                await query.answer("❌ Задача не найдена", show_alert=True)
        
        elif data.startswith('delete_'):
            task_id = int(data.split('_')[1])
            if db.delete_task(task_id):
                await query.edit_message_text(
                    text="🗑️ Задача удалена!",
                    parse_mode="HTML"
                )
            else:
                await query.answer("❌ Задача не найдена", show_alert=True)
    except (ValueError, IndexError):
        await query.answer("❌ Ошибка при обработке", show_alert=True)

# ==================== HANDLE TEXT ====================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений из меню"""
    text = update.message.text
    
    if text == '➕ Новая задача':
        return await add_task_start(update, context)
    elif text == '📋 Мои задачи':
        return await show_tasks(update, context)
    elif text == '✅ Сегодня':
        return await show_today_tasks(update, context)
    elif text == '📊 Статус':
        return await status_command(update, context)
    elif text == '❓ Помощь':
        return await help_command(update, context)
    else:
        await update.message.reply_text(
            "❓ Команда не распознана. Используй меню или /help",
            reply_markup=get_main_keyboard()
        )

# ==================== ERROR HANDLER ====================

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

# ==================== MAIN ====================

def main():
    """Запуск бота"""
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Callback обработчик для кнопок (должен быть первым!)
    app.add_handler(CallbackQueryHandler(button_callback))
    
    # Команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("tasks", show_tasks))
    app.add_handler(CommandHandler("today", show_today_tasks))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("complete", complete_task))
    app.add_handler(CommandHandler("delete", delete_task))
    
    # Conversation для добавления задачи
    add_task_handler = ConversationHandler(
        entry_points=[
            CommandHandler("add", add_task_start),
            MessageHandler(filters.TEXT & filters.Regex("^➕ Новая задача$"), add_task_start)
        ],
        states={
            ADD_TITLE: [MessageHandler(filters.TEXT, add_task_title)],
            ADD_CATEGORY: [MessageHandler(filters.TEXT, add_task_category)],
            ADD_PRIORITY: [MessageHandler(filters.TEXT, add_task_priority)],
            ADD_DATE: [MessageHandler(filters.TEXT, add_task_date)],
            ADD_TIME: [MessageHandler(filters.TEXT, add_task_time)],
            ADD_DESCRIPTION: [MessageHandler(filters.TEXT, add_task_description)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    app.add_handler(add_task_handler)
    
    # Обработка других сообщений
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    
    # Error handler
    app.add_error_handler(error_handler)
    
    # Запуск
    logger.info("🚀 Бот запущен!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
