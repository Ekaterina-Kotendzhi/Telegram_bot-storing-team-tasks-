"""
Модуль для создания клавиатур Telegram бота.
Клавиатуры - это кнопки под сообщением в чате.
"""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard():
    """
    Создает главную клавиатуру с основными командами.
    
    Возвращает:
    ReplyKeyboardMarkup - клавиатуру с кнопками команд
    """
    # Создаем кнопки для основных команд
    add_button = KeyboardButton(text='/add')
    list_button = KeyboardButton(text='/list')
    csv_button = KeyboardButton(text='/list_csv')
    
    # Создаем клавиатуру и добавляем кнопки
    # resize_keyboard=True - автоматически подгоняет размер клавиатуры
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [add_button, list_button],  # Первый ряд: /add и /list
            [csv_button]  # Второй ряд: /list_csv
        ]
    )
    
    return keyboard