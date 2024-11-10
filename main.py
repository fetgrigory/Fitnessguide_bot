'''
This bot make

Author: Fetkulin Grigory, Fetkulin.G.R@yandex.ru
Starting 15/04/2022
Ending //
'''
# Installing the necessary libraries
import os
import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
# from app.database.sqlite3_db import create_table, insert_workout_data, get_workout_data
from app.database.PostgreSQL_db import create_table, insert_workout_data, get_workout_data
from app.keyboards import main_keyboard
from dotenv import load_dotenv
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
# Load environment variables
load_dotenv()

# Initialization of the bot and dispatcher
bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(storage=MemoryStorage())


# Define states
class WorkoutStates(StatesGroup):
    BenchPress = State()
    DumbbellFly = State()
    Situps = State()
    Height = State()
    Weight = State()


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


# Handler for initiating the workout data collection process
@dp.callback_query(lambda c: c.data == 'add_data')
async def add_workout_data(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await ask_question(callback_query.message, state, WorkoutStates.BenchPress, questions[0])


# Handler to retrieve and display stored workout data
@dp.callback_query(lambda c: c.data == 'get_data')
async def get_workout_data_handler(callback_query: CallbackQuery):
    await callback_query.answer()
    data = get_workout_data()
    if not data:
        await bot.send_message(callback_query.message.chat.id, "Данных о тренировках нет!")
        return
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


# Function to ask a question and set the next state
async def ask_question(message: types.Message, state: FSMContext, next_state: State, question_text: str):
    await message.answer(question_text)
    await state.set_state(next_state)


# Handler to process Bench Press data
@dp.message(WorkoutStates.BenchPress)
async def process_bench_press(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите числовое значение.")
        return
    await state.update_data(bench_press=int(message.text))
    await ask_question(message, state, WorkoutStates.DumbbellFly, questions[1])


# Handler to process Dumbbell Fly data
@dp.message(WorkoutStates.DumbbellFly)
async def process_dumbbell_fly(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите числовое значение.")
        return
    await state.update_data(dumbbell_fly=int(message.text))
    await ask_question(message, state, WorkoutStates.Situps, questions[2])


# Handler to process Situps data
@dp.message(WorkoutStates.Situps)
async def process_situps(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите числовое значение.")
        return
    await state.update_data(situps=int(message.text))
    await ask_question(message, state, WorkoutStates.Height, questions[3])


# Handler to process height data
@dp.message(WorkoutStates.Height)
async def process_height(message: types.Message, state: FSMContext):
    try:
        height = float(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите числовое значение.")
        return
    await state.update_data(height=height)
    await ask_question(message, state, WorkoutStates.Weight, questions[4])


# Handler to process weight data and calculate BMI
@dp.message(WorkoutStates.Weight)
async def process_weight(message: types.Message, state: FSMContext):
    try:
        weight = float(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите числовое значение.")
        return
    await state.update_data(weight=weight)

    # Retrieve all user inputs
    user_data = await state.get_data()

    # Calculate BMI
    height_m = user_data['height'] / 100
    weight_kg = user_data['weight']
    bmi, category = calculate_bmi_category(height_m, weight_kg)

    # Prepare the data items list to store in the database
    current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data = [
        current_date,
        user_data['bench_press'],
        user_data['dumbbell_fly'],
        user_data['situps'],
        user_data['height'],
        user_data['weight'],
        bmi,
        category
    ]
    insert_workout_data(data)
    await message.answer(f"Данные о тренировке успешно сохранены!\nВаш ИМТ: {bmi:.2f} ({category})")
    # Finish the state
    await state.clear()


# Calculate BMI
def calculate_bmi_category(height_in_meters: float, weight_in_kg: float):
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
