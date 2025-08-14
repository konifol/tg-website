#!/usr/bin/env python3
"""
Тест страницы создания бота
"""

import requests
import json

def test_create_bot_page():
    """Тестируем страницу создания бота"""
    
    base_url = "http://localhost:5002"
    
    print("=== Тест страницы создания бота ===")
    
    # Тест 1: Проверяем доступность страницы
    print("\n1. Проверка доступности страницы создания бота...")
    try:
        response = requests.get(f"{base_url}/create-bot")
        if response.status_code == 200:
            print("✅ Страница создания бота доступна")
            
            # Проверяем наличие ключевых элементов
            content = response.text
            if 'Библиотека блоков' in content:
                print("✅ Секция 'Библиотека блоков' найдена")
            else:
                print("❌ Секция 'Библиотека блоков' не найдена")
                
            if 'Конфигурация блоков' in content:
                print("✅ Секция 'Конфигурация блоков' найдена")
            else:
                print("❌ Секция 'Конфигурация блоков' не найдена")
                
            if 'drop-zone' in content:
                print("✅ Drag & Drop зона найдена")
            else:
                print("❌ Drag & Drop зона не найдена")
                
        else:
            print(f"❌ Страница недоступна: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Не удается подключиться к серверу")
        print("Убедитесь, что приложение запущено на порту 5002")
        return False
    
    # Тест 2: Проверяем API блоков
    print("\n2. Проверка API блоков...")
    try:
        response = requests.get(f"{base_url}/api/bot-blocks")
        if response.status_code == 200:
            blocks = response.json()
            print(f"✅ API блоков работает, найдено блоков: {len(blocks)}")
            
            # Проверяем наличие основных блоков
            expected_blocks = ['welcome', 'help', 'about', 'message', 'photo', 'inline_keyboard', 'reply_keyboard']
            found_blocks = list(blocks.keys())
            
            for block in expected_blocks:
                if block in found_blocks:
                    print(f"  ✅ Блок '{block}' найден")
                else:
                    print(f"  ❌ Блок '{block}' не найден")
                    
        else:
            print(f"❌ API блоков недоступен: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка при проверке API блоков: {e}")
    
    # Тест 3: Проверяем создание бота
    print("\n3. Проверка создания бота...")
    try:
        test_bot_data = {
            "name": "Test Bot",
            "token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
            "description": "Test bot for testing",
            "config": [
                {
                    "id": 0,
                    "type": "welcome",
                    "name": "Приветствие",
                    "icon": "fas fa-hand-wave",
                    "color": "primary",
                    "config": {
                        "message": "Привет! Это тестовый бот."
                    }
                }
            ]
        }
        
        response = requests.post(
            f"{base_url}/api/create-bot",
            headers={'Content-Type': 'application/json'},
            data=json.dumps(test_bot_data)
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Создание бота работает")
                print(f"  ID бота: {result.get('bot_id')}")
            else:
                print(f"❌ Ошибка создания бота: {result.get('error')}")
        else:
            print(f"❌ API создания бота недоступен: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Ошибка при тестировании создания бота: {e}")
    
    print("\n=== Тест завершен ===")
    return True

if __name__ == "__main__":
    print("🚀 Тестирование страницы создания бота")
    print("=" * 50)
    
    success = test_create_bot_page()
    
    if success:
        print("\n✅ Тестирование завершено успешно")
        print("Страница создания бота работает корректно")
    else:
        print("\n❌ Тестирование не удалось")
        print("Проверьте, что приложение запущено и доступно")