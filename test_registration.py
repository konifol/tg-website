#!/usr/bin/env python3
"""
Тест регистрации пользователей
"""

import requests
import json

def test_registration():
    """Тестируем регистрацию пользователя"""
    
    base_url = "http://localhost:5002"
    
    # Тест 1: Проверяем доступность страницы регистрации
    print("=== Тест 1: Доступность страницы регистрации ===")
    try:
        response = requests.get(f"{base_url}/register")
        if response.status_code == 200:
            print("✅ Страница регистрации доступна")
        else:
            print(f"❌ Страница регистрации недоступна: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Не удается подключиться к серверу")
        print("Убедитесь, что приложение запущено на порту 5002")
        return False
    
    # Тест 2: Проверяем форму регистрации
    print("\n=== Тест 2: Форма регистрации ===")
    try:
        # Данные для регистрации
        test_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        }
        
        # Отправляем POST запрос с form данными
        response = requests.post(
            f"{base_url}/register",
            data=test_data,  # Используем data вместо json
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        print(f"Статус ответа: {response.status_code}")
        print(f"Заголовки ответа: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Регистрация прошла успешно")
            print("Содержимое ответа:")
            print(response.text[:500])  # Первые 500 символов
        elif response.status_code == 302:  # Redirect
            print("✅ Регистрация прошла успешно (редирект)")
            print(f"Редирект на: {response.headers.get('Location', 'Неизвестно')}")
        else:
            print(f"❌ Ошибка регистрации: {response.status_code}")
            print("Содержимое ответа:")
            print(response.text[:500])
            
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
    
    # Тест 3: Проверяем страницу входа
    print("\n=== Тест 3: Доступность страницы входа ===")
    try:
        response = requests.get(f"{base_url}/login")
        if response.status_code == 200:
            print("✅ Страница входа доступна")
        else:
            print(f"❌ Страница входа недоступна: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    return True

if __name__ == "__main__":
    print("🚀 Тестирование регистрации Bot Creator Platform")
    print("=" * 50)
    
    success = test_registration()
    
    if success:
        print("\n✅ Тестирование завершено")
        print("Теперь можете открыть http://localhost:5002 в браузере")
    else:
        print("\n❌ Тестирование не удалось")
        print("Проверьте, что приложение запущено")