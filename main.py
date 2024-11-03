# Installing the necessary libraries
import os
import datetime
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from app.database import create_table, insert_workout_data, get_workout_data
from app.keyboards import main_keyboard
import asyncio

# Load environment variables
load_dotenv()

# Initialization of the bot and dispatcher
bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(storage=MemoryStorage())

# Global variable to store user data
USER_DATA = {}
questions = [
    "Введите количество жима лёжа:",
    "Введите количество разведения гантелей на грудь:",
    "Введите количество подъёмов туловища из положения лёжа на спине:",
    "Введите ваш рост (в см):",
    "Введите ваш вес (в кг):"
]

# Creating a table in the database
create_table()
# Making sure that the bot is running
print('Бот успешно запущен!')

@dp.message(Command("start"))
async def start(message: Message):
    USER_DATA.clear()
    keyboard = main_keyboard()
    me = await bot.me()
    await message.answer(f"Здравствуйте, {message.from_user.first_name}!\n"
                         f"Меня зовут {me.first_name}, Я помогу вам вести учет фитнес-тренировок.",
                         reply_markup=keyboard)

@dp.callback_query(lambda c: c.data == 'add_data')
async def add_workout_data(callback_query: CallbackQuery):
    await ask_next_question(callback_query.message)

@dp.callback_query(lambda c: c.data == 'get_data')
async def get_workout_data_handler(callback_query: CallbackQuery):
    await callback_query.answer()
    data = get_workout_data()
    result = ''
    for record in data:
        bmi, category = calculate_bmi_category(float(record[5]), float(record[6]))
        result += (f"Дата: {record[1]}\n"
                   f"Отжимания: {record[2]}\n"
                   f"Жим лёжа: {record[3]}\n"
                   f"Разведение гантелей на грудь: {record[4]}\n"
                   f"Рост: {record[5]} см\n"
                   f"Вес: {record[6]} кг\n"
                   f"ИМТ: {bmi:.2f} ({category})\n\n")
    await bot.send_message(callback_query.message.chat.id, f"Данные о тренировках:\n{result}")

async def ask_next_question(message: Message):
    if len(USER_DATA) < len(questions):
        question = questions[len(USER_DATA)]
        await message.answer(question)
        USER_DATA['current_question'] = question
    else:
        await save_workout_data(message)

@dp.message()
async def add_workout(message: Message):
    answer = message.text
    if 'current_question' in USER_DATA:
        USER_DATA[USER_DATA['current_question']] = answer
        del USER_DATA['current_question']
        await ask_next_question(message)

async def save_workout_data(message: Message):
    current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data = [
        current_date,
        USER_DATA.get(questions[0], ""),
        USER_DATA.get(questions[1], ""),
        USER_DATA.get(questions[2], ""),
        USER_DATA.get(questions[3], ""),
        USER_DATA.get(questions[4], "")
    ]
    insert_workout_data(data)
    height = float(USER_DATA.get(questions[3], 0)) / 100
    weight = float(USER_DATA.get(questions[4], 0))
    bmi, category = calculate_bmi_category(height, weight)
    await message.answer(f"Данные о тренировке успешно сохранены!\nВаш ИМТ: {bmi:.2f} ({category})")

def calculate_bmi_category(height_in_meters: float, weight_in_kg: float):
    bmi = weight_in_kg / height_in_meters**2
    if bmi <= 16:
        category = "Выраженный дефицит массы тела"
    elif 16 < bmi <= 18.5:
        category = "Недостаточная (дефицит) масса тела"
    elif 18.5 < bmi <= 25:
        category = "Норма"
    elif 25 < bmi <= 30:
        category = "Избыточная масса тела (предожирение)"
    elif 30 < bmi <= 35:
        category = "Ожирение первой степени"
    elif 35 < bmi <= 40:
        category = "Ожирение второй степени"
    else:
        category = "Ожирение третьей степени (морбидное)"
    return bmi, category

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())