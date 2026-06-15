import sqlite3
import json
from datetime import datetime
from typing import List, Optional, Tuple
from config import DATABASE_PATH, DATE_FORMAT, DATETIME_FORMAT


class Database:
    def __init__(self):
        self.db_path = DATABASE_PATH
        self.init_db()

    def init_db(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Таблица задач
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                category TEXT,
                priority TEXT DEFAULT 'medium',
                due_date TEXT,
                due_time TEXT,
                completed BOOLEAN DEFAULT 0,
                is_recurring BOOLEAN DEFAULT 0,
                recurring_interval TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reminder_enabled BOOLEAN DEFAULT 0,
                reminder_type TEXT,
                UNIQUE(user_id, title, due_date)
            )
        ''')
        
        # Таблица напоминаний
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                reminder_time TEXT,
                sent BOOLEAN DEFAULT 0,
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
            )
        ''')
        
        conn.commit()
        conn.close()

    def add_task(self, user_id: int, title: str, category: str = None, 
                 priority: str = 'medium', due_date: str = None, 
                 due_time: str = None, is_recurring: bool = False,
                 recurring_interval: str = None, description: str = None,
                 reminder_enabled: bool = False, reminder_type: str = None) -> bool:
        """Добавить новую задачу"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO tasks 
                (user_id, title, category, priority, due_date, due_time, 
                 is_recurring, recurring_interval, description, reminder_enabled, reminder_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, title, category, priority, due_date, due_time,
                  is_recurring, recurring_interval, description, reminder_enabled, reminder_type))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_all_tasks(self, user_id: int, completed: bool = False) -> List[dict]:
        """Получить все задачи пользователя"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM tasks 
            WHERE user_id = ? AND completed = ?
            ORDER BY 
                CASE 
                    WHEN priority = 'high' THEN 1
                    WHEN priority = 'medium' THEN 2
                    ELSE 3
                END,
                due_date ASC,
                due_time ASC
        ''', (user_id, int(completed)))
        
        tasks = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return tasks

    def get_task_by_id(self, task_id: int) -> Optional[dict]:
        """Получить задачу по ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        task = cursor.fetchone()
        conn.close()
        
        return dict(task) if task else None

    def complete_task(self, task_id: int) -> bool:
        """Отметить задачу как выполненную"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE tasks SET completed = 1 WHERE id = ?', (task_id,))
        
        conn.commit()
        conn.close()
        return cursor.rowcount > 0

    def delete_task(self, task_id: int) -> bool:
        """Удалить задачу"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        
        conn.commit()
        conn.close()
        return cursor.rowcount > 0

    def get_tasks_by_category(self, user_id: int, category: str) -> List[dict]:
        """Получить задачи по категории"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM tasks 
            WHERE user_id = ? AND category = ? AND completed = 0
            ORDER BY due_date ASC
        ''', (user_id, category))
        
        tasks = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return tasks

    def get_today_tasks(self, user_id: int) -> List[dict]:
        """Получить задачи на сегодня"""
        today = datetime.now().strftime(DATE_FORMAT)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM tasks 
            WHERE user_id = ? AND due_date = ? AND completed = 0
            ORDER BY due_time ASC
        ''', (user_id, today))
        
        tasks = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return tasks

    def update_task(self, task_id: int, **kwargs) -> bool:
        """Обновить поля задачи"""
        allowed_fields = {
            'title', 'category', 'priority', 'due_date', 'due_time',
            'is_recurring', 'recurring_interval', 'description'
        }
        
        fields = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not fields:
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        set_clause = ', '.join([f'{k} = ?' for k in fields.keys()])
        query = f'UPDATE tasks SET {set_clause} WHERE id = ?'
        
        cursor.execute(query, (*fields.values(), task_id))
        
        conn.commit()
        conn.close()
        return cursor.rowcount > 0

    def get_tasks_count(self, user_id: int) -> Tuple[int, int]:
        """Получить количество активных и завершенных задач"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM tasks WHERE user_id = ? AND completed = 0', (user_id,))
        active = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM tasks WHERE user_id = ? AND completed = 1', (user_id,))
        completed = cursor.fetchone()[0]
        
        conn.close()
        return active, completed

    def get_daily_stats(self, user_id: int) -> dict:
        """Получить статистику выполнения задач на сегодня"""
        today = datetime.now().strftime(DATE_FORMAT)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Все задачи на сегодня
        cursor.execute(
            'SELECT COUNT(*) FROM tasks WHERE user_id = ? AND due_date = ?',
            (user_id, today)
        )
        total_today = cursor.fetchone()[0]
        
        # Выполненные на сегодня
        cursor.execute(
            'SELECT COUNT(*) FROM tasks WHERE user_id = ? AND due_date = ? AND completed = 1',
            (user_id, today)
        )
        completed_today = cursor.fetchone()[0]
        
        conn.close()
        
        percentage = 0
        if total_today > 0:
            percentage = int((completed_today / total_today) * 100)
        
        return {
            'total': total_today,
            'completed': completed_today,
            'percentage': percentage
        }

    def add_reminder(self, task_id: int, user_id: int, reminder_time: str) -> bool:
        """Добавить напоминание"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO reminders (task_id, user_id, reminder_time)
            VALUES (?, ?, ?)
        ''', (task_id, user_id, reminder_time))
        
        conn.commit()
        conn.close()
        return True

    def get_pending_reminders(self) -> List[dict]:
        """Получить неотправленные напоминания"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        now = datetime.now().strftime(DATETIME_FORMAT)
        
        cursor.execute('''
            SELECT r.*, t.title, t.due_date, t.due_time 
            FROM reminders r
            JOIN tasks t ON r.task_id = t.id
            WHERE r.sent = 0 AND r.reminder_time <= ?
            ORDER BY r.reminder_time ASC
        ''', (now,))
        
        reminders = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return reminders

    def mark_reminder_sent(self, reminder_id: int) -> bool:
        """Отметить напоминание как отправленное"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE reminders SET sent = 1 WHERE id = ?', (reminder_id,))
        
        conn.commit()
        conn.close()
        return cursor.rowcount > 0

    def get_tasks_with_reminders(self) -> List[dict]:
        """Получить все активные задачи с включенными напоминаниями"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM tasks 
            WHERE reminder_enabled = 1 AND completed = 0
            ORDER BY due_date, due_time
        ''')
        
        tasks = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return tasks
