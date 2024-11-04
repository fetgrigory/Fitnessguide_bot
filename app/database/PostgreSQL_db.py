import psycopg2
import os


# Function for creating a database connection
def create_connection():
    """AI is creating summary for db_connect

    Returns:
        [type]: [description]
    """
    # Establish a connection to the PostgreSQL database using environment variables
    return psycopg2.connect(
        # Database host
        host=os.getenv('HOST'),
        # Name of the database
        dbname=os.getenv('DBNAME'),
        # Username for authentication
        user=os.getenv('USER'),
        # Password for authentication
        password=os.getenv('PASSWORD'),
        # Port number for database connection
        port=os.getenv('PORT')
    )

# Function for creating a table in the database
def create_table():
    """Creates the fitness table in the PostgreSQL database."""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fitness (
            id SERIAL PRIMARY KEY,
            date VARCHAR(255),
            hands INTEGER,
            breast INTEGER,
            press INTEGER,
            height REAL,
            weight REAL,
            bmi REAL,
            bmi_category VARCHAR(255)
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

# Function for inserting workout data
def insert_workout_data(data):
    """Inserts workout data into the fitness table.

    Args:
        data (tuple): A tuple containing the data to be inserted (date, hands, breast, press, height, weight, bmi, bmi_category).
    """
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO fitness (date, hands, breast, press, height, weight, bmi, bmi_category)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, data)
    conn.commit()
    cursor.close()
    conn.close()

# Function for getting training data
def get_workout_data():
    """Retrieves all workout data from the fitness table.

    Returns:
        data: A list of tuples containing the workout data.
    """
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM fitness")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data
