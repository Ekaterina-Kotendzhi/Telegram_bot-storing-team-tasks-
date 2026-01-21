"""
Модуль для работы с базой данных SQLite.
Создает таблицу tasks и предоставляет функции для работы с задачами.
"""

import sqlite3
from datetime import datetime

# Создаем подключение к базе данных
def create_connection():
    """
    Создает соединение с базой данных SQLite.
    База данных будет храниться в файле tasks.db
    """
    conn = sqlite3.connect('tasks.db')
    return conn

def init_database():
    """
    Инициализирует базу данных: создает таблицу tasks, если она не существует.
    """
    conn = create_connection()
    cursor = conn.cursor()
    
    # Создаем таблицу tasks с полями:
    # id - уникальный идентификатор задачи
    # text - текст задачи
    # user - имя пользователя, который добавил задачу
    # created_at - дата и время создания задачи
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT NOT NULL,
        user TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    ''')
    
    conn.commit()
    conn.close()

def add_task(text, user):
    """
    Добавляет новую задачу в базу данных.
    
    Аргументы:
    text - текст задачи
    user - имя пользователя
    
    Возвращает:
    ID добавленной задачи
    """
    conn = create_connection()
    cursor = conn.cursor()
    
    # Получаем текущую дату и время
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Вставляем новую задачу в таблицу
    cursor.execute('''
    INSERT INTO tasks (text, user, created_at)
    VALUES (?, ?, ?)
    ''', (text, user, current_time))
    
    task_id = cursor.lastrowid  # Получаем ID добавленной задачи
    conn.commit()
    conn.close()
    
    return task_id

def get_all_tasks():
    """
    Получает все задачи из базы данных.
    
    Возвращает:
    Список всех задач в виде кортежей (id, text, user, created_at)
    """
    conn = create_connection()
    cursor = conn.cursor()
    
    # Выбираем все задачи, отсортированные по дате создания (сначала новые)
    cursor.execute('SELECT * FROM tasks ORDER BY created_at DESC')
    tasks = cursor.fetchall()
    
    conn.close()
    return tasks

def get_tasks_csv():
    """
    Получает все задачи и форматирует их в CSV строку.
    
    Возвращает:
    Строку в формате CSV с заголовками
    """
    tasks = get_all_tasks()
    
    # Создаем CSV строку с заголовками
    csv_data = "ID,Задача,Пользователь,Дата создания,Статус,Категория\n"
    
    for task in tasks:
        # Экранируем кавычки в тексте задачи
        text = str(task[1]).replace('"', '""')
        status = "Новая"
        category = "Без категории"
        csv_data += f'{task[0]},"{text}","{task[2]}","{task[3]}","{status}","{category}"\n'
    
    return csv_data

def count_tasks():
    """
    Подсчитывает общее количество задач в базе данных.
    
    Возвращает:
    Количество задач
    """
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM tasks')
    count = cursor.fetchone()[0]
    
    conn.close()
    return count