import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

# Load environment variables from .env file if present
load_dotenv()

class Config:
    """
    Database and Application Configuration
    
    You can easily change your MySQL credentials here or in the .env file.
    Default settings:
      Host: localhost
      User: root
      Password: (empty by default, update if your MySQL has a password)
      Database: inventory_db
      Port: 3306
    """
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'inventory_db')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    SECRET_KEY = os.environ.get('SECRET_KEY', 'inventory_secret_key_2026')


def get_db_connection():
    """
    Establishes and returns a connection to the MySQL database.
    Returns:
        mysql.connector.connection.MySQLConnection or None if connection fails.
    """
    try:
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            port=Config.MYSQL_PORT,
            autocommit=False  # We manage transactions explicitly
        )
        return connection
    except Error as e:
        print(f"[ERROR] Database connection failed: {e}")
        return None
