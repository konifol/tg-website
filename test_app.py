#!/usr/bin/env python3
"""
Тест Flask приложения Bot Creator Platform
"""

import os
import sys
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

print("=== Тест Flask приложения ===")

try:
    # Импортируем приложение
    from app import app, db, User, Bot, BotSession
    
    print("✅ Все модули импортированы успешно")
    
    # Создаем контекст приложения
    with app.app_context():
        print("✅ Контекст приложения создан")
        
        # Проверяем подключение к базе
        try:
            with db.engine.connect() as conn:
                result = conn.execute(db.text("SELECT 1"))
                result.fetchone()
            print("✅ Подключение к базе данных работает")
        except Exception as e:
            print(f"❌ Ошибка подключения к базе: {e}")
            sys.exit(1)
        
        # Проверяем таблицы
        try:
            users_count = User.query.count()
            bots_count = Bot.query.count()
            sessions_count = BotSession.query.count()
            
            print(f"✅ Таблицы доступны:")
            print(f"  - Users: {users_count}")
            print(f"  - Bots: {bots_count}")
            print(f"  - Sessions: {sessions_count}")
            
        except Exception as e:
            print(f"❌ Ошибка доступа к таблицам: {e}")
            sys.exit(1)
        
        # Проверяем маршруты
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(rule.rule)
        
        print(f"✅ Маршруты зарегистрированы: {len(routes)}")
        for route in routes[:10]:  # Показываем первые 10
            print(f"  - {route}")
        
        if len(routes) > 10:
            print(f"  ... и еще {len(routes) - 10} маршрутов")
        
        print("\n=== Тест завершен успешно! ===")
        print("Приложение готово к работе!")
        
except Exception as e:
    print(f"❌ Критическая ошибка: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)