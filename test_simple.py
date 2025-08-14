#!/usr/bin/env python3
"""
Простой тест подключения к базе данных и основных функций
"""

import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

print("=== Тест Bot Creator Platform ===")
print(f"DB_HOST: {os.getenv('DB_HOST')}")
print(f"DB_PORT: {os.getenv('DB_PORT')}")
print(f"DB_USER: {os.getenv('DB_USER')}")
print(f"DB_NAME: {os.getenv('DB_NAME')}")

try:
    import mysql.connector
    print("✅ mysql.connector импортирован успешно")
    
    # Тест подключения к базе
    config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'user': os.getenv('DB_USER', 'botcreator'),
        'password': os.getenv('DB_PASSWORD', 'botcreator123'),
        'database': os.getenv('DB_NAME', 'botcreator'),
        'charset': 'utf8mb4'
    }
    
    print("Подключение к базе данных...")
    connection = mysql.connector.connect(**config)
    
    if connection.is_connected():
        print("✅ Подключение к базе данных успешно!")
        
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        print(f"Таблицы в базе: {len(tables)}")
        for table in tables:
            print(f"  - {table[0]}")
        
        cursor.close()
        connection.close()
        print("✅ Соединение закрыто")
    
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
except Exception as e:
    print(f"❌ Ошибка: {e}")

print("\n=== Тест Flask ===")
try:
    from flask import Flask
    print("✅ Flask импортирован успешно")
    
    app = Flask(__name__)
    print("✅ Flask приложение создано")
    
    @app.route('/')
    def hello():
        return "Hello, World!"
    
    print("✅ Маршрут добавлен")
    
except Exception as e:
    print(f"❌ Ошибка Flask: {e}")

print("\n=== Тест завершен ===")