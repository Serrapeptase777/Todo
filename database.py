import sqlite3
from datetime import datetime

DB_NAME = "todo_list.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_text TEXT NOT NULL,
                date_text TEXT NOT NULL,
                time_text TEXT NOT NULL,
                is_completed INTEGER DEFAULT 0
            )
        """)
        conn.commit()

def add_task(text):
    now = datetime.now()
    date_str = now.strftime("%d.%m.%Y")
    time_str = now.strftime("%H:%M")
    
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (task_text, date_text, time_text, is_completed) VALUES (?, ?, ?, 0)",
            (text, date_str, time_str)
        )
        conn.commit()
        return cursor.lastrowid, date_str, time_str

def get_all_tasks():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks ORDER BY id ASC")
        return cursor.fetchall()

def update_task_status(task_id, is_completed):
    now = datetime.now()
    date_str = now.strftime("%d.%m.%Y")
    time_str = now.strftime("%H:%M")
    
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE tasks 
            SET is_completed = ?, date_text = ?, time_text = ? 
            WHERE id = ?
        """, (1 if is_completed else 0, date_str, time_str, task_id))
        conn.commit()
        return date_str, time_str

# ОСЬ ЦЯ ФУНКЦІЯ, ЯКОЇ НЕ ВИСТАЧАЛО:
def update_task_text(task_id, new_text):
    """Оновлює текст завдання за його ID при редагуванні."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET task_text = ? WHERE id = ?", (new_text, task_id))
        conn.commit()

def delete_task(task_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()