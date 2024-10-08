'''
This bot make

Athor: Fetkulin Grigory, Fetkulin.G.R@yandex.ru
Starting 15/04/2022
Ending //

'''
# Installing the necessary libraries
import os
import datetime
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from app.database import create_table, insert_workout_data, get_workout_data
from app.keyboards import main_keyboard

load_dotenv()
# Initialization of the board and the dispatcher.
bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# Global variable to store user data
USER_DATA = {}
questions = [
    "Введите количество жима лёжа:",
    "Введите количество разведения гантелей на грудь:",
    "Введите количество подъёмов туловища из положения лёжа на спине:"
]

# Creating a table in the database
create_table()
# Making sure that the bot is running
print('Бот успешно запущен!')


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    USER_DATA.clear()
    keyboard = main_keyboard()
    me = await bot.get_me()
    await message.answer(f"Здравствуйте, {message.from_user.first_name}!\n"
                         f"Меня зовут {me.first_name}, Я помогу вам вести учет фитнес-тренировок.",
                         parse_mode='html', reply_markup=keyboard)


# Handler when user chooses to add workout data
@dp.callback_query_handler(lambda c: c.data == 'add_data')
async def add_workout_data(callback_query: types.CallbackQuery):
    await ask_next_question(callback_query.message)
# Handler when user chooses to get workout data
@dp.callback_query_handler(lambda c: c.data == 'get_data')
async def get_workout_data_handler(callback_query: types.CallbackQuery):
    await callback_query.answer()
    data = get_workout_data()
    result = ''
    for record in data:
        result += f"Дата: {record[1]}\nОтжимания: {record[2]}\nЖим лёжа: {record[3]}\nРазведение гантелей на грудь: {record[4]}\n\n"
    await bot.send_message(callback_query.message.chat.id, f"Данные о тренировках:\n{result}")


# Handler for asking the next question in the user input flow
async def ask_next_question(message: types.Message):
    if len(USER_DATA) < len(questions):
        question = questions[len(USER_DATA)]
        await message.answer(question)
        USER_DATA['current_question'] = question
    else:
        await save_workout_data(message)


# Handler for adding workout data based on user input
@dp.message_handler()
async def add_workout(message: types.Message):
    answer = message.text
    if 'current_question' in USER_DATA:
        USER_DATA[USER_DATA['current_question']] = answer
        del USER_DATA['current_question']
        await ask_next_question(message)


# Function to save workout data to the database
async def save_workout_data(message: types.Message):
    current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data = [current_date, USER_DATA.get(questions[0], ""), USER_DATA.get(questions[1], ""), USER_DATA.get(questions[2], "")]
    insert_workout_data(data)
    await message.answer("Данные о тренировке успешно сохранены!")
# Start the polling loop for the dispatcher
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(dp.start_polling())
