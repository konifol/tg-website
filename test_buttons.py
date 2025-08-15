#!/usr/bin/env python3
"""
Тест функциональности кнопок для Bot Creator Platform
"""

import json
import requests

def test_button_blocks():
    """Тестируем блоки с кнопками"""
    print("🧪 Тестирование блоков с кнопками")
    print("=" * 50)
    
    # Тестируем API блоков
    try:
        response = requests.get('http://localhost:5002/api/bot-blocks')
        if response.status_code == 200:
            blocks = response.json()
            print("✅ API блоков работает")
            
            # Проверяем наличие блоков с кнопками
            if 'inline_keyboard' in blocks:
                inline_block = blocks['inline_keyboard']
                print(f"✅ Блок 'Инлайн кнопки' найден:")
                print(f"   - Название: {inline_block['name']}")
                print(f"   - Описание: {inline_block['description']}")
                print(f"   - Поля: {len(inline_block['fields'])}")
                
                for field in inline_block['fields']:
                    print(f"     - {field['name']}: {field['type']} ({'обязательное' if field['required'] else 'необязательное'})")
            
            if 'reply_keyboard' in blocks:
                reply_block = blocks['reply_keyboard']
                print(f"✅ Блок 'Клавиатура' найден:")
                print(f"   - Название: {reply_block['name']}")
                print(f"   - Описание: {reply_block['description']}")
                print(f"   - Поля: {len(reply_block['fields'])}")
                
                for field in reply_block['fields']:
                    print(f"     - {field['name']}: {field['type']} ({'обязательное' if field['required'] else 'необязательное'})")
            
            print(f"\n📊 Всего доступно блоков: {len(blocks)}")
            
        else:
            print(f"❌ API блоков вернул статус: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Не удалось подключиться к приложению")
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")

def test_json_validation():
    """Тестируем валидацию JSON для кнопок"""
    print("\n🔍 Тестирование валидации JSON")
    print("=" * 50)
    
    # Тестовые JSON структуры
    test_cases = [
        {
            'name': 'Правильная структура инлайн кнопок',
            'json': '[["Да", "Нет"], ["Отмена"]]',
            'should_be_valid': True
        },
        {
            'name': 'Правильная структура клавиатуры',
            'json': '[["Кнопка 1", "Кнопка 2"], ["Кнопка 3"]]',
            'should_be_valid': True
        },
        {
            'name': 'Неправильный JSON - отсутствует закрывающая скобка',
            'json': '[["Кнопка 1", "Кнопка 2"], ["Кнопка 3"',
            'should_be_valid': False
        },
        {
            'name': 'Неправильная структура - не массив',
            'json': '{"кнопка": "текст"}',
            'should_be_valid': False
        },
        {
            'name': 'Неправильная структура - не массив массивов',
            'json': '["Кнопка 1", "Кнопка 2"]',
            'should_be_valid': False
        },
        {
            'name': 'Пустые кнопки',
            'json': '[["", "Кнопка 2"], ["Кнопка 3"]]',
            'should_be_valid': False
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        try:
            parsed = json.loads(test_case['json'])
            is_valid = True
            
            # Дополнительная валидация для кнопок
            if isinstance(parsed, list):
                for row in parsed:
                    if not isinstance(row, list):
                        is_valid = False
                        break
                    for btn in row:
                        if not isinstance(btn, str) or btn.strip() == '':
                            is_valid = False
                            break
            else:
                is_valid = False
                
        except json.JSONDecodeError:
            is_valid = False
        
        status = "✅" if is_valid == test_case['should_be_valid'] else "❌"
        print(f"{status} {i}. {test_case['name']}")
        print(f"   JSON: {test_case['json']}")
        print(f"   Ожидалось: {'валиден' if test_case['should_be_valid'] else 'невалиден'}")
        print(f"   Результат: {'валиден' if is_valid else 'невалиден'}")
        print()

def main():
    """Основная функция тестирования"""
    print("🚀 Тестирование функциональности кнопок Bot Creator Platform")
    print("=" * 70)
    
    test_button_blocks()
    test_json_validation()
    
    print("🎯 Тестирование завершено!")
    print("\n💡 Для тестирования интерфейса откройте:")
    print("   http://localhost:5002/create-bot")

if __name__ == '__main__':
    main()