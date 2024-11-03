'''
This module make
Athor: Fetkulin Grigory, Fetkulin.G.R@yandex.ru
Starting 05/10/2024
Ending //

'''
import sqlite3


# Function for creating a database connection
def create_connection():
    """AI is creating summary for create_connection

    Returns:
        [type]: [description]
    """
    return sqlite3.connect('fitness.db')


# Function for creating a table in the database
def create_table():
    """AI is creating summary for create_table
    """
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS fitness
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       date VARCHAR(50),
                       hands VARCHAR(50),
                       breast VARCHAR(50),
                       press VARCHAR(50),
                       height VARCHAR(50),
                       weight VARCHAR(50))''')
    conn.commit()
    conn.close()


# Function for inserting training data
def insert_workout_data(data):
    """AI is creating summary for insert_workout_data

    Args:
        data ([type]): [description]
    """
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO fitness (date, hands, breast, press, height, weight) VALUES (?, ?, ?, ?, ?, ?)", data)
    conn.commit()
    conn.close()


# Function for getting training data
def get_workout_data():
    """AI is creating summary for get_workout_data

    Returns:
        [type]: [description]
    """
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM fitness")
    data = cursor.fetchall()
    conn.close()
    return data
