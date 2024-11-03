'''
This module make

Athor: Fetkulin Grigory, Fetkulin.G.R@yandex.ru
Starting 05/10/2024
Ending //

'''

from aiogram import types

# Function to create the main keyboard
def main_keyboard() -> types.InlineKeyboardMarkup:
    """Creates the main inline keyboard

    Returns:
        types.InlineKeyboardMarkup: Main keyboard markup
    """
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(text="Добавить данные", callback_data='add_data'),
            types.InlineKeyboardButton(text="Получить данные", callback_data='get_data')
        ],
        [
            types.InlineKeyboardButton(text="Показать упражнения на YouTube", url="https://www.youtube.com/@IgorVoitenkoWorkout")
        ]
    ])
    return keyboard