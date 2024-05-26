'''
This bot make

Athor: Fetkulin Grigory, Fetkulin.G.R@yandex.ru
Starting 15/04/2022
Ending 25/05/2024

'''
# Installing the necessary libraries
from aiogram import Bot, Dispatcher, types
import sqlite3
import datetime
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from a .env file.

# Initialize telegram bot, dispatcher, and database connection.
bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher(bot=bot)


conn = sqlite3.connect('fitness.db')
cursor = conn.cursor()

# Create a table to store fitness data if it doesn't already exist.
cursor.execute('''CREATE TABLE IF NOT EXISTS fitness
               (id INTEGER PRIMARY KEY AUTOINCREMENT,
               date VARCHAR(50),
               hands VARCHAR(50),
               breast VARCHAR(50),
               press VARCHAR(50))''')
conn.commit()

USER_DATA = {}  # Dictionary to store user input data.
questions = [  # List of questions for the user input.
    "Введите количество жима лёжа:",
    "Введите количество разведения гантелей на грудь:",
    "Введите количество подъёмов туловища из положения лёжа на спине:"
]

# Handler for the /start command to welcome users and provide options.
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    # Clear user data and create a keyboard with options.
    USER_DATA.clear()
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(
        types.InlineKeyboardButton("Добавить данные", callback_data='add_data'),
        types.InlineKeyboardButton("Получить данные", callback_data='get_data')
    )
    # Add a button to show workout exercises on YouTube.
    keyboard.add(
        types.InlineKeyboardButton("Показать упражнения на YouTube", url="https://www.youtube.com/@IgorVoitenkoWorkout")
    )
    me = await bot.get_me()
    await message.answer(f"Здравствуйте, {message.from_user.first_name}!\n"
                         f"Меня зовут {me.first_name}, Я помогу вам вести учет фитнес-тренировок.",
                         parse_mode='html', reply_markup=keyboard)

# Handler when user chooses to add workout data.
@dp.callback_query_handler(lambda c: c.data == 'add_data')
async def add_workout_data(callback_query: types.CallbackQuery):
    await ask_next_question(callback_query.message)

# Handler when user chooses to get workout data.
@dp.callback_query_handler(lambda c: c.data == 'get_data')
async def get_workout_data(callback_query: types.CallbackQuery):
    # Retrieve data from the database and send it back to the user.
    await callback_query.answer()
    conn = sqlite3.connect('fitness.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM fitness")
    data = cursor.fetchall()
    conn.close()

    result = ''
    for record in data:
        result += f"Дата: {record[1]}\nОтжимания: {record[2]}\nЖим лёжа: {record[3]}\nРазведение гантелей на грудь: {record[4]}\n\n"

    await bot.send_message(callback_query.message.chat.id, f"Данные о тренировках:\n{result}")

# Handler for asking the next question in the user input flow.
async def ask_next_question(message: types.Message):
    if len(USER_DATA) < len(questions):
        question = questions[len(USER_DATA)]
        await message.answer(question)
        USER_DATA['current_question'] = question
    else:
        await save_workout_data(message)

# Handler for adding workout data based on user input.
@dp.message_handler()
async def add_workout(message: types.Message):
    answer = message.text
    if 'current_question' in USER_DATA:
        USER_DATA[USER_DATA['current_question']] = answer
        del USER_DATA['current_question']
        await ask_next_question(message)

# Function to save workout data to the database.
async def save_workout_data(message: types.Message):
    current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data = [current_date, USER_DATA.get(questions[0], ""), USER_DATA.get(questions[1], ""), USER_DATA.get(questions[2], "")]
    cursor.execute("INSERT INTO fitness (date, hands, breast, press) VALUES (?, ?, ?, ?)", data)
    conn.commit()
    await message.answer("Данные о тренировке успешно сохранены!")

# Start the polling loop for the dispatcher.
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(dp.start_polling())
