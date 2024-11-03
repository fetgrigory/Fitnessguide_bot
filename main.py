'''
This bot make

Author: Fetkulin Grigory, Fetkulin.G.R@yandex.ru
Starting 15/04/2022
Ending //
'''
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
load_dotenv()
# Initialization of the board and the dispatcher.
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


# Handler when user chooses to add workout data
@dp.callback_query(lambda c: c.data == 'add_data')
async def add_workout_data(callback_query: CallbackQuery):
    await ask_next_question(callback_query.message)


# Handler when user chooses to get workout data
@dp.callback_query(lambda c: c.data == 'get_data')
async def get_workout_data_handler(callback_query: CallbackQuery):
    await callback_query.answer()
    data = get_workout_data()
    result = ''
    for record in data:
        result += (f"Дата: {record[1]}\n"
                   f"Отжимания: {record[2]}\n"
                   f"Жим лёжа: {record[3]}\n"
                   f"Разведение гантелей на грудь: {record[4]}\n"
                   f"Рост: {record[5]}\n"
                   f"Вес: {record[6]}\n\n")
    await bot.send_message(callback_query.message.chat.id, f"Данные о тренировках:\n{result}")


# Handler for asking the next question in the user input flow
async def ask_next_question(message: Message):
    if len(USER_DATA) < len(questions):
        question = questions[len(USER_DATA)]
        await message.answer(question)
        USER_DATA['current_question'] = question
    else:
        await save_workout_data(message)


# Handler for adding workout data based on user input
@dp.message()
async def add_workout(message: Message):
    answer = message.text
    if 'current_question' in USER_DATA:
        USER_DATA[USER_DATA['current_question']] = answer
        del USER_DATA['current_question']
        await ask_next_question(message)


# Function to save workout data to the database
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
    await message.answer("Данные о тренировке успешно сохранены!")

# Start the polling loop for the dispatcher
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())