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

# Ensuring that the bot is running
print('Бот успешно запущен!')


@dp.message(Command("start"))
async def start(message: Message):
    USER_DATA.clear()
    keyboard = main_keyboard()
    me = await bot.me()
    await message.answer(f"Здравствуйте, {message.from_user.first_name}!\n"
                         f"Меня зовут {me.first_name}, Я помогу вам вести учет фитнес-тренировок.",
                         reply_markup=keyboard)


# Begin asking questions to collect workout data
@dp.callback_query(lambda c: c.data == 'add_data')
async def add_workout_data(callback_query: CallbackQuery):
    await ask_next_question(callback_query.message)


@dp.callback_query(lambda c: c.data == 'get_data')
async def get_workout_data_handler(callback_query: CallbackQuery):
    await callback_query.answer()
    data = get_workout_data()
    if not data:
        # No workout data available
        await bot.send_message(callback_query.message.chat.id, "Данных о тренировках нет!")
        return
        # Prepare a formatted string of workout data
    result = ''
    for record in data:
        result += (f"Дата: {record[1]}\n"
                   f"Отжимания: {record[2]}\n"
                   f"Жим лёжа: {record[3]}\n"
                   f"Разведение гантелей на грудь: {record[4]}\n"
                   f"Рост: {record[5]} см\n"
                   f"Вес: {record[6]} кг\n"
                   f"ИМТ: {record[7]:.2f} ({record[8]})\n\n")
    await bot.send_message(callback_query.message.chat.id, f"Данные о тренировках:\n{result}")


async def ask_next_question(message: Message):
    # Ask the next question if all questions haven't been answered yet
    if len(USER_DATA) < len(questions):
        question = questions[len(USER_DATA)]
        await message.answer(question)
        USER_DATA['current_question'] = question
    else:
        # Save the user's workout data after all questions are answered
        await save_workout_data(message)


@dp.message()
async def add_workout(message: Message):
    answer = message.text
    if 'current_question' in USER_DATA:
        question_index = questions.index(USER_DATA['current_question'])
        # Exercise counts need to be integers
        if question_index in {0, 1, 2}:
            if not answer.isdigit():
                await message.answer("Пожалуйста, введите числовое значение.")
                return
            # Height and weight need to be floats
        elif question_index in {3, 4}:
            try:
                float(answer)
            except ValueError:
                await message.answer("Пожалуйста, введите числовое значение.")
                return
# Store the answer and proceed to the next question
        USER_DATA[USER_DATA['current_question']] = answer
        del USER_DATA['current_question']
        await ask_next_question(message)


async def save_workout_data(message: Message):
    # Current date and time for the record
    current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # Convert to meters for BMI calculation
    height = float(USER_DATA.get(questions[3], 0)) / 100
    weight = float(USER_DATA.get(questions[4], 0))
    bmi, category = calculate_bmi_category(height, weight)
    # Prepare the data items list to store in database
    data = [
        current_date,
        USER_DATA.get(questions[0], ""),
        USER_DATA.get(questions[1], ""),
        USER_DATA.get(questions[2], ""),
        USER_DATA.get(questions[3], ""),
        USER_DATA.get(questions[4], ""),
        bmi,
        category
    ]
    insert_workout_data(data)
    await message.answer(f"Данные о тренировке успешно сохранены!\nВаш ИМТ: {bmi:.2f} ({category})")


def calculate_bmi_category(height_in_meters: float, weight_in_kg: float):
    # Calculate BMI
    bmi = weight_in_kg / height_in_meters**2
    # Determine BMI category based on the calculated value
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
    # Start polling to keep the bot running and listening for messages
    await dp.start_polling(bot)
if __name__ == '__main__':
    asyncio.run(main())
