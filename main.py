'''
This module make

Athor: Fetkulin Grigory, Fetkulin.G.R@yandex.ru
Starting 2022/04/15
Ending 2022/04/16

'''
# Установка необходимых библиотек
import sqlite3
import telebot
from telebot import types
from datetime import datetime
from settings import TG_TOKEN
# Подключение API ключа
bot = telebot.TeleBot(TG_TOKEN)


# Создание таблицы fitness в базе данных, если ее нет
conn = sqlite3.connect('fitness.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS fitness 
               (id INTEGER PRIMARY KEY AUTOINCREMENT, 
               date VARCHAR(50),
               hands VARCHAR(50), 
               breast VARCHAR(50), 
               press VARCHAR(50), 
               back VARCHAR(50), 
               legs VARCHAR(50))''')
conn.commit()
conn.close()


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    # клавиатура
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("Добавить данные", callback_data='hands'),
        types.InlineKeyboardButton("Получить данные", callback_data='get_data')
    )
    markup.add(
        types.InlineKeyboardButton("Показать упражнения на YouTube", url="https://www.youtube.com/@IgorVoitenkoWorkout")
    )
    # Отправка сообщения с кнопками
    bot.send_message(message.chat.id, "Здравствуйте, {0.first_name}!\nМеня зовут<b> {1.first_name}</b>, Я помогу тебе вести учёт фитнес-тренировок.\n".format(
                         message.from_user, bot.get_me()), parse_mode='html', reply_markup=markup)


# Функция для записи данных в базу данных
def record_data(date, hands, breast, press, back, legs):
    # Подключение к базе данных
    conn = sqlite3.connect('fitness.db')
    cursor = conn.cursor()
    # Вставка данных в таблицу fitness
    cursor.execute(f"INSERT INTO fitness (date, hands, breast, press, back, legs) VALUES ('{date}', '{hands}', '{breast}', '{press}', '{back}', '{legs}')")
    # Сохранение изменений
    conn.commit()
    # Закрытие соединения с базой данных
    conn.close()


# Функция для записи данных об отжиманиях
def record_hands(message):
    hands = message.text
    # Просьба ввести количество жима лёжа
    bot.send_message(message.chat.id, 'Введите количество жима лёжа')
    bot.register_next_step_handler(message, record_breast, hands)


# Функция для записи данных о жиме лежа
def record_breast(message, hands):
    breast = message.text
    # Просьба ввести количество разведения гантелей на грудь
    bot.send_message(message.chat.id, 'Введите количество разведения гантелей на грудь')
    bot.register_next_step_handler(message, record_press, hands, breast)


# Функция для записи данных о разведении гантелей
def record_press(message, hands, breast):
    press = message.text
    # Просьба ввести количество подъёмов туловища из положения лёжа на спине
    bot.send_message(message.chat.id, 'Введите количество подъёмов туловища из положения лёжа на спине')
    bot.register_next_step_handler(message, record_back, hands, breast, press)


# Функция для записи данных о подъёмах туловища
def record_back(message, hands, breast, press):
    back = message.text
    # Просьба ввести количество подтягиваний на перекладине
    bot.send_message(message.chat.id, 'Введите количество подтягиваний на перекладине')
    bot.register_next_step_handler(message, record_legs, hands, breast, press, back)


# Функция для записи данных о подтягиваниях на перекладине
def record_legs(message, hands, breast, press, back):
    legs = message.text
    # Запись данных в базу данных
    date = datetime.now().strftime("%d-%m-%Y")
    record_data(date, hands, breast, press, back, legs)
    # Отправка сообщения об успешном сохранении данных
    bot.send_message(message.chat.id, 'Данные успешно сохранены!')


# Обработчик нажатий на кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "hands":
        # Просьба ввести количество отжиманий
        bot.answer_callback_query(callback_query_id=call.id)
        bot.send_message(call.message.chat.id, "Введите количество отжиманий:")
        bot.register_next_step_handler(call.message, record_hands)
    elif call.data == 'breast':
        # Просьба ввести количество жима лёжа
        bot.answer_callback_query(callback_query_id=call.id)
        bot.send_message(call.message.chat.id, 'Введите количество жима лёжа:')
        bot.register_next_step_handler(call.message, record_breast, '')
    elif call.data == 'press':
        # Просьба ввести количество разведения гантелей на грудь
        bot.answer_callback_query(callback_query_id=call.id)
        bot.send_message(call.message.chat.id, 'Введите количество разведения гантелей на грудь:')
        bot.register_next_step_handler(call.message, record_press, '', '')
    elif call.data == 'back':
        # Просьба ввести количество подъёмов туловища из положения лёжа на спине
        bot.answer_callback_query(callback_query_id=call.id)
        bot.send_message(call.message.chat.id, 'Введите количество подъёмов туловища из положения лёжа на спине:')
        bot.register_next_step_handler(call.message, record_back, '', '', '')
    elif call.data == 'legs':
        # Просьба ввести количество подтягиваний на перекладине
        bot.answer_callback_query(callback_query_id=call.id)
        bot.send_message(call.message.chat.id, 'Введите количество подтягиваний на перекладине:')
        bot.register_next_step_handler(call.message, record_legs, '', '', '', '')
    elif call.data == 'get_data':
        # Получение данных из базы данных
        bot.answer_callback_query(callback_query_id=call.id)
        conn = sqlite3.connect('fitness.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM fitness")
        data = cursor.fetchall()
        conn.close()
        # Формирование строк со значениями данных в таблице
        result = ''
        for record in data:
            date = datetime.strptime(record[1], "%d-%m-%Y").strftime("%d.%m.%Y")
            result += f'Дата: {date}\nОтжимания: {record[2]},\n Жим лёжа: {record[3]},\n Разведение гантелей на грудь: {record[4]},\n Подъёмы туловища из положения лёжа на спине: {record[5]},\n Подтягивания на перекладине: {record[6]}\n\n'
        # Отправка сообщения с данными
        bot.send_message(call.message.chat.id, f'Таблица fitness:\n{result}')


# Чтение новых сообщений
bot.polling(none_stop=True)
