# 🔄 Руководство по миграции с SQLite на MariaDB

## 📋 Обзор изменений

Этот документ описывает процесс миграции Bot Creator Platform с SQLite на MariaDB для улучшения производительности и масштабируемости.

## 🔄 Что изменилось

### База данных
- **Было**: SQLite (файловая база)
- **Стало**: MariaDB (серверная база)

### Модели данных
- Добавлены поля `updated_at` и `is_active`
- Улучшена структура таблиц
- Добавлены индексы для производительности
- Добавлена таблица `bot_sessions`

### Сессии
- **Было**: Flask session (временные)
- **Стало**: Сохранение в базе данных

## 🚀 Процесс миграции

### Шаг 1: Подготовка

#### Создайте резервную копию SQLite
```bash
# Остановите приложение
# Скопируйте файл базы данных
cp instance/bot_creator.db backup_bot_creator.db
```

#### Установите MariaDB
```bash
sudo apt update
sudo apt install -y mariadb-server mariadb-client
sudo systemctl start mariadb
sudo systemctl enable mariadb
```

### Шаг 2: Настройка MariaDB

#### Автоматическая настройка
```bash
chmod +x database/setup_database.sh
./database/setup_database.sh
```

#### Ручная настройка
```bash
# Подключение к MariaDB
sudo mysql

# Создание базы и пользователя
CREATE DATABASE botcreator CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'botcreator'@'localhost' IDENTIFIED BY 'botcreator123';
GRANT ALL PRIVILEGES ON botcreator.* TO 'botcreator'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Шаг 3: Миграция данных

#### Создайте скрипт миграции
```python
# migration_script.py
import sqlite3
import mysql.connector
import json
from datetime import datetime

# Подключение к SQLite
sqlite_conn = sqlite3.connect('instance/bot_creator.db')
sqlite_cursor = sqlite_conn.cursor()

# Подключение к MariaDB
mariadb_conn = mysql.connector.connect(
    host='localhost',
    user='botcreator',
    password='botcreator123',
    database='botcreator'
)
mariadb_cursor = mariadb_conn.cursor()

# Миграция пользователей
sqlite_cursor.execute("SELECT id, email, name, google_id, password_hash, created_at FROM user")
users = sqlite_cursor.fetchall()

for user in users:
    user_id, email, name, google_id, password_hash, created_at = user
    
    # Преобразование даты
    if isinstance(created_at, str):
        created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
    
    mariadb_cursor.execute("""
        INSERT INTO users (id, email, name, google_id, password_hash, created_at, updated_at, is_active)
        VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE)
    """, (user_id, email, name, google_id, password_hash, created_at, created_at))

# Миграция ботов
sqlite_cursor.execute("SELECT id, name, token, config, python_code, created_at, user_id FROM bot")
bots = sqlite_cursor.fetchall()

for bot in bots:
    bot_id, name, token, config, python_code, created_at, user_id = bot
    
    # Преобразование даты
    if isinstance(created_at, str):
        created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
    
    mariadb_cursor.execute("""
        INSERT INTO bots (id, name, token, config, python_code, created_at, updated_at, is_active, user_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE, %s)
    """, (bot_id, name, token, config, python_code, created_at, created_at, user_id))

# Сохранение изменений
mariadb_conn.commit()

# Закрытие соединений
sqlite_cursor.close()
sqlite_conn.close()
mariadb_cursor.close()
mariadb_conn.close()

print("Миграция завершена успешно!")
```

#### Запустите миграцию
```bash
python3 migration_script.py
```

### Шаг 4: Обновление приложения

#### Обновите зависимости
```bash
pip install -r requirements.txt
```

#### Создайте .env файл
```bash
cp .env.example .env
# Отредактируйте файл с вашими настройками
```

#### Проверьте подключение
```bash
python3 database/manage_db.py show
```

### Шаг 5: Тестирование

#### Запустите приложение
```bash
python3 app.py
```

#### Проверьте функциональность
- Регистрация/вход
- Создание ботов
- Сохранение сессий
- Генерация кода

## 🔧 Устранение проблем

### Проблема: Ошибка подключения к MariaDB
```bash
# Проверьте статус сервиса
sudo systemctl status mariadb

# Проверьте подключение
mysql -u botcreator -p -h localhost

# Проверьте права доступа
sudo mysql
SHOW GRANTS FOR 'botcreator'@'localhost';
```

### Проблема: Ошибка миграции данных
```bash
# Проверьте структуру таблиц
python3 database/manage_db.py show

# Проверьте данные
python3 database/manage_db.py show --table users
python3 database/manage_db.py show --table bots
```

### Проблема: Потеря данных
```bash
# Восстановите из резервной копии
cp backup_bot_creator.db instance/bot_creator.db

# Или восстановите из SQL дампа
mysql -u botcreator -p botcreator < backup.sql
```

## 📊 Проверка миграции

### SQL запросы для проверки
```sql
-- Подсчет пользователей
SELECT COUNT(*) as total_users FROM users;

-- Подсчет ботов
SELECT COUNT(*) as total_bots FROM bots;

-- Проверка целостности
SELECT 
    u.name as user_name,
    COUNT(b.id) as bot_count
FROM users u 
LEFT JOIN bots b ON u.id = b.user_id
GROUP BY u.id, u.name
ORDER BY bot_count DESC;
```

### Python проверка
```python
from app import app, db, User, Bot

with app.app_context():
    users_count = User.query.count()
    bots_count = Bot.query.count()
    
    print(f"Users: {users_count}")
    print(f"Bots: {bots_count}")
    
    # Проверка первого пользователя
    first_user = User.query.first()
    if first_user:
        print(f"First user: {first_user.name} ({first_user.email})")
        print(f"User bots: {len(first_user.bots)}")
```

## 🚀 Откат изменений

### Если что-то пошло не так

#### Восстановление SQLite
```bash
# Остановите приложение
# Восстановите файл базы
cp backup_bot_creator.db instance/bot_creator.db

# Обновите app.py (замените MariaDB на SQLite)
# Перезапустите приложение
```

#### Восстановление MariaDB
```bash
# Остановите приложение
# Удалите базу данных
mysql -u root -p
DROP DATABASE botcreator;
CREATE DATABASE botcreator;
EXIT;

# Пересоздайте таблицы
python3 database/manage_db.py create

# Восстановите данные из дампа
mysql -u botcreator -p botcreator < backup.sql
```

## 📈 Преимущества после миграции

### Производительность
- ✅ Быстрые запросы с индексами
- ✅ Поддержка множественных подключений
- ✅ Лучшая масштабируемость

### Надежность
- ✅ ACID транзакции
- ✅ Автоматическое резервное копирование
- ✅ Восстановление после сбоев

### Функциональность
- ✅ Сохранение сессий в базе
- ✅ Soft delete для данных
- ✅ Аудит изменений (updated_at)

## 🔮 Следующие шаги

### Оптимизация
```bash
# Создание дополнительных индексов
python3 database/manage_db.py show

# Мониторинг производительности
mysql -u botcreator -p -e "SHOW STATUS LIKE 'Slow_queries';"
```

### Резервное копирование
```bash
# Автоматическое резервное копирование
0 2 * * * /path/to/project/database/manage_db.py backup --backup-file /backups/backup_$(date +\%Y\%m\%d).sql
```

### Мониторинг
```bash
# Проверка состояния базы
python3 database/manage_db.py show

# Логи приложения
tail -f app.log
```

---

## ✅ Чек-лист миграции

- [ ] Создана резервная копия SQLite
- [ ] Установлен и настроен MariaDB
- [ ] Создана база данных и пользователь
- [ ] Выполнена миграция данных
- [ ] Обновлены зависимости
- [ ] Настроен .env файл
- [ ] Протестировано приложение
- [ ] Проверена целостность данных
- [ ] Настроено резервное копирование

---

**Миграция завершена! 🎉 Теперь у вас надежная и масштабируемая система!**