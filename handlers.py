"""
Модуль с обработчиками команд и сообщений бота.
Здесь определяется логика ответов на команды пользователей.
"""

from aiogram import Router, types, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import database
import keyboards

router = Router()

# Определяем состояния (FSM - Finite State Machine)
# Это нужно для отслеживания, в каком состоянии находится диалог с пользователем
class TaskStates(StatesGroup):
    waiting_for_task = State()  # Состояние ожидания текста задачи

async def start_command(message: types.Message):
    """
    Обработчик команды /start.
    Приветствует пользователя и показывает доступные команды.
    """
    welcome_text = f"""
    👋 Привет, {message.from_user.full_name}!
    
    Я бот для управления задачами команды.
    
    📋 Доступные команды:
    /add - Добавить новую задачу
    /list - Показать все задачи
    /list_csv - Получить CSV файл со всеми задачами
    
    Выберите команду из меню или воспользуйтесь клавиатурой ниже 👇
    """
    
    await message.answer(
        welcome_text,
        reply_markup=keyboards.get_main_keyboard()
    )

async def add_command(message: types.Message, state: FSMContext):
    """
    Обработчик команды /add.
    Начинает процесс добавления новой задачи.
    """
    # Просим пользователя ввести текст задачи
    await message.answer("📝 Введите текст задачи:")
    
    # Устанавливаем состояние ожидания текста задачи
    await state.set_state(TaskStates.waiting_for_task)

async def process_task_text(message: types.Message, state: FSMContext):
    """
    Обработчик текста задачи после команды /add.
    Сохраняет задачу в базу данных.
    """
    task_text = message.text
    user_name = message.from_user.full_name
    
    # Добавляем задачу в базу данных
    task_id = database.add_task(task_text, user_name)
    
    # Получаем общее количество задач
    total_tasks = database.count_tasks()
    
    await message.answer(
        f"✅ Задача #{task_id} добавлена успешно!\n"
        f"📊 Всего задач в базе: {total_tasks}",
        reply_markup=keyboards.get_main_keyboard()
    )
    
    # Сбрасываем состояние (завершаем диалог добавления задачи)
    await state.clear()

async def list_command(message: types.Message):
    """
    Обработчик команды /list.
    Показывает все задачи из базы данных.
    """
    tasks = database.get_all_tasks()
    
    if not tasks:
        await message.answer("📭 Список задач пуст!")
        return
    
    # Формируем сообщение со всеми задачами
    tasks_text = "📋 Список всех задач:\n\n"
    
    for task in tasks:
        # task[0] - id, task[1] - text, task[2] - user, task[3] - created_at
        tasks_text += f"🔹 #{task[0]}\n"
        tasks_text += f"📝 {task[1]}\n"
        tasks_text += f"👤 Добавил: {task[2]}\n"
        tasks_text += f"🕐 {task[3]}\n"
        tasks_text += "─" * 30 + "\n"
    
    # Добавляем информацию о количестве задач
    tasks_text += f"\n📊 Всего задач: {len(tasks)}"
    
    # Telegram имеет ограничение на длину сообщения (4096 символов)
    # Разбиваем длинные сообщения на части
    if len(tasks_text) > 4000:
        parts = [tasks_text[i:i+4000] for i in range(0, len(tasks_text), 4000)]
        for part in parts:
            await message.answer(part)
    else:
        await message.answer(tasks_text)

async def list_csv_command(message: types.Message):
    """
    Обработчик команды /list_csv.
    Отправляет файл CSV со всеми задачами.
    """
    tasks = database.get_all_tasks()
    
    if not tasks:
        await message.answer("📭 Список задач пуст!")
        return
    
    # Получаем данные в формате CSV
    csv_data = database.get_tasks_csv()
    
    # Создаем временный файл и отправляем его пользователю
    # Используем InputFile для отправки файла
    from aiogram.types import BufferedInputFile
    import io
    
    # Создаем файл в памяти
    csv_file = io.BytesIO(csv_data.encode('utf-8-sig'))  # utf-8-sig для корректного отображения в Excel
    
    # Отправляем файл пользователю
    await message.answer_document(
        document=BufferedInputFile(csv_file.getvalue(), filename='tasks.csv'),
        caption="📁 CSV файл со всеми задачами"
    )

def register_handlers(dp: Dispatcher):
    """
    Регистрирует все обработчики команд.
    
    Аргументы:
    dp - диспетчер aiogram
    """
    # Регистрируем обработчики команд
    router.message.register(start_command, Command('start'))
    router.message.register(add_command, Command('add'))
    router.message.register(list_command, Command('list'))
    router.message.register(list_csv_command, Command('list_csv'))
    
    # Регистрируем обработчик текста для состояния waiting_for_task
    router.message.register(process_task_text, TaskStates.waiting_for_task)
    dp.include_router(router)