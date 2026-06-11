import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Token - получи из @BotFather
BOT_TOKEN = os.getenv('BOT_TOKEN')

# DATABASE
DATABASE_PATH = os.getenv('DATABASE_PATH', 'planner.db')

# PRIORITY LEVELS
PRIORITIES = {
    '🔴': 'high',
    '🟡': 'medium',
    '🟢': 'low'
}

# CATEGORIES (emoji)
CATEGORIES = {
    '💼': 'work',
    '🏠': 'home',
    '🎓': 'learning',
    '💪': 'health',
    '🎯': 'personal',
    '🛒': 'shopping'
}

# TIME FORMAT
DATE_FORMAT = '%d.%m.%Y'
DATETIME_FORMAT = '%d.%m.%Y %H:%M'
