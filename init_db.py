"""
Database Initializer Script for Inventory Management System
===========================================================
This script automatically connects to your MySQL server,
creates the database `inventory_db`, and initializes all
tables and sample seed data from `database/inventory.sql`.

Usage:
    python init_db.py
"""

import os
import sys
import mysql.connector
from config import Config

def init_database():
    print("=" * 60)
    print(" Inventory Management System — MySQL Database Setup")
    print("=" * 60)
    print(f"Connecting to MySQL Host: {Config.MYSQL_HOST}:{Config.MYSQL_PORT}")
    print(f"User: {Config.MYSQL_USER}")

    # First connect without specifying database to create inventory_db if needed
    try:
        conn = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            port=Config.MYSQL_PORT
        )
        print(" Connected to MySQL server successfully.")
    except mysql.connector.Error as err:
        print(f"\n[ERROR] Could not connect to MySQL server: {err}")
        print("\nPlease ensure:")
        print("1. MySQL Server is running (e.g., in Windows Services / MySQL Workbench).")
        print("2. Your MySQL password is correct in `config.py` or `.env`.")
        sys.exit(1)

    cursor = conn.cursor()

    sql_file_path = os.path.join(os.path.dirname(__file__), 'database', 'inventory.sql')
    if not os.path.exists(sql_file_path):
        print(f"\n[ERROR] Schema file not found at: {sql_file_path}")
        sys.exit(1)

    print(f"Reading SQL script from: {sql_file_path}...")
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        sql_commands = f.read()

    # Split commands by semicolon, ignoring empty lines and comments
    statements = sql_commands.split(';')

    print("Executing database schema and seed data...")
    executed_count = 0

    for stmt in statements:
        cleaned_stmt = stmt.strip()
        if cleaned_stmt:
            try:
                cursor.execute(cleaned_stmt)
                executed_count += 1
            except mysql.connector.Error as err:
                print(f"Warning/Error on statement:\n{cleaned_stmt[:80]}...\nDetails: {err}\n")

    conn.commit()
    cursor.close()
    conn.close()

    print("=" * 60)
    print(f" Database `inventory_db` initialized successfully! ({executed_count} statements executed)")
    print(" You can now run `python app.py` to start the website.")
    print("=" * 60)

if __name__ == '__main__':
    init_database()
