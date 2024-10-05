'''
This module make
Athor: Fetkulin Grigory, Fetkulin.G.R@yandex.ru
Starting 05/10/2024
Ending //

'''
from aiogram import types


# Function to create the main keyboard
def main_keyboard():
    """AI is creating summary for main_keyboard

    Returns:
        [type]: [description]
    """
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(
        types.InlineKeyboardButton("Добавить данные", callback_data='add_data'),
        types.InlineKeyboardButton("Получить данные", callback_data='get_data')
    )
    keyboard.add(
        types.InlineKeyboardButton("Показать упражнения на YouTube", url="https://www.youtube.com/@IgorVoitenkoWorkout")
    )
    return keyboard
