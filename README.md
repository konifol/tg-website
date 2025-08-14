# Bot Creator Platform

Веб-платформа для создания Telegram ботов с помощью простого блочного интерфейса. Не требует знаний программирования!

## 🚀 Возможности

- **Блочный интерфейс** - создавайте ботов, перетаскивая готовые блоки
- **Автоматическая генерация Python кода** - получайте готовый скрипт для запуска
- **Сохранение сессий** - ваша работа автоматически сохраняется
- **Регистрация и авторизация** - поддержка обычной регистрации и Google OAuth
- **Современный дизайн** - красивый и интуитивно понятный интерфейс
- **MariaDB поддержка** - надежная база данных для продакшена
- **Админ-панель** - полное управление пользователями и ботами

## 🛠️ Технологии

- **Backend**: Flask, SQLAlchemy, Flask-Login
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5, jQuery
- **База данных**: MariaDB/MySQL
- **Аутентификация**: Flask-Login с поддержкой Google OAuth
- **Контейнеризация**: Docker & Docker Compose
- **Администрирование**: Встроенная панель управления

## 📋 Требования

- Python 3.7+
- MariaDB 10.5+ или MySQL 8.0+
- pip
- Docker & Docker Compose (опционально)
- Веб-браузер

## 🚀 Установка и запуск

### Способ 1: Локальная установка

#### 1. Клонирование репозитория
```bash
git clone <repository-url>
cd bot-creator-platform
```

#### 2. Создание виртуального окружения
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

#### 3. Установка зависимостей
```bash
pip install -r requirements.txt
```

#### 4. Настройка MariaDB
```bash
# Установка MariaDB (Ubuntu/Debian)
sudo apt update
sudo apt install -y mariadb-server mariadb-client

# Запуск сервиса
sudo systemctl start mariadb
sudo systemctl enable mariadb

# Безопасная установка
sudo mysql_secure_installation
```

#### 5. Создание базы данных
```bash
# Автоматическая настройка
chmod +x database/setup_database.sh
./database/setup_database.sh

# Или вручную через Python
python3 database/manage_db.py create
```

#### 6. Настройка переменных окружения
Создайте файл `.env` на основе `.env.example`:
```env
SECRET_KEY=your-secret-key-here
DB_HOST=localhost
DB_PORT=3306
DB_USER=botcreator
DB_PASSWORD=botcreator123
DB_NAME=botcreator
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

#### 7. Запуск приложения
```bash
python3 app.py
```

### Способ 2: Docker Compose (рекомендуется)

#### 1. Клонирование и настройка
```bash
git clone <repository-url>
cd bot-creator-platform

# Создание .env файла
cp .env.example .env
# Отредактируйте .env файл
```

#### 2. Запуск с Docker Compose
```bash
# Запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

#### 3. Только база данных
```bash
# Запуск только MariaDB
docker-compose up -d mariadb

# Подключение к базе
docker-compose exec mariadb mysql -u botcreator -p botcreator
```

## 🔐 Доступ к админ-панели

### Учетные данные по умолчанию
- **Логин**: `admin`
- **Пароль**: `password`

### Вход в админ-панель
1. Войдите в систему с учетными данными администратора
2. В навигации появится меню "Админ"
3. Перейдите в "Панель управления"

### Возможности админ-панели
- **Панель управления** - обзор системы и статистика
- **Управление пользователями** - просмотр, активация/деактивация, изменение прав
- **Управление ботами** - просмотр всех ботов, конфигураций, токенов
- **Статистика** - графики и аналитика использования платформы

## 🔧 Управление базой данных

### Python скрипт управления
```bash
# Создание таблиц
python3 database/manage_db.py create

# Просмотр структуры
python3 database/manage_db.py show

# Создание админа
python3 database/manage_db.py admin --email admin@example.com --name Admin --password secret123

# Резервная копия
python3 database/manage_db.py backup --backup-file backup.sql

# Восстановление
python3 database/manage_db.py restore --backup-file backup.sql
```

### SQL команды
```sql
-- Подключение к базе
mysql -u botcreator -p botcreator

-- Просмотр таблиц
SHOW TABLES;

-- Структура таблицы
DESCRIBE users;

-- Создание пользователя
INSERT INTO users (email, name, password_hash, created_at, updated_at, is_active) 
VALUES ('admin@example.com', 'Admin', 'hashed_password', NOW(), NOW(), TRUE);
```

## 🔐 Настройка Google OAuth

Для полной функциональности Google OAuth:

1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте новый проект
3. Включите Google+ API
4. Создайте OAuth 2.0 credentials
5. Добавьте разрешенные redirect URIs:
   - http://localhost:5000/google-callback (для разработки)
   - https://yourdomain.com/google-callback (для продакшена)
6. Скопируйте Client ID и Client Secret в `.env` файл

## 📱 Использование

### 1. Регистрация/Вход
- Создайте аккаунт или войдите через Google
- Заполните основную информацию

### 2. Создание бота
- Перейдите в раздел "Создать бота"
- Перетащите нужные блоки в рабочую область
- Настройте параметры каждого блока
- Введите название и описание бота

### 3. Доступные блоки
- **Приветствие** - команда /start
- **Помощь** - команда /help
- **О боте** - команда /about
- **Кастомный ответ** - ответ на ключевые слова
- **Эхо** - повторение всех сообщений

### 4. Генерация кода
- Нажмите "Сгенерировать код"
- Получите готовый Python скрипт
- Скопируйте код и запустите на своем сервере

### 5. Сохранение
- Нажмите "Сохранить бота"
- Введите название
- Бот будет сохранен в вашем профиле

## 🗄️ Структура базы данных

### Таблица Users
- `id` - уникальный идентификатор
- `email` - email пользователя (уникальный)
- `name` - имя пользователя
- `google_id` - ID Google аккаунта (уникальный)
- `password_hash` - хеш пароля
- `created_at` - дата создания
- `updated_at` - дата обновления
- `is_active` - активность пользователя
- `is_admin` - права администратора

### Таблица Bots
- `id` - уникальный идентификатор
- `name` - название бота
- `token` - токен Telegram бота
- `config` - конфигурация в формате JSON
- `python_code` - сгенерированный Python код
- `created_at` - дата создания
- `updated_at` - дата обновления
- `is_active` - активность бота
- `user_id` - ID пользователя-создателя (внешний ключ)

### Таблица BotSessions
- `id` - уникальный идентификатор
- `user_id` - ID пользователя (внешний ключ)
- `session_data` - данные сессии в формате JSON
- `created_at` - дата создания
- `updated_at` - дата обновления

## 🔒 Безопасность

- Пароли хешируются с помощью Werkzeug
- Сессии защищены секретным ключом
- CSRF защита для форм
- Аутентификация через Flask-Login
- Подключение к базе данных через SSL (опционально)
- Soft delete для данных
- Проверка прав администратора для критических операций

## 🚀 Развертывание в продакшене

### 1. Настройка сервера
```bash
# Установка Gunicorn
pip install gunicorn

# Запуск через Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### 2. Настройка Nginx
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. Переменные окружения для продакшена
```env
FLASK_ENV=production
SECRET_KEY=very-secure-secret-key
DB_HOST=localhost
DB_PORT=3306
DB_USER=botcreator
DB_PASSWORD=secure-password
DB_NAME=botcreator
```

### 4. Docker Compose для продакшена
```bash
# Запуск с Nginx
docker-compose --profile production up -d

# Мониторинг
docker-compose ps
docker-compose logs -f
```

## 🐛 Устранение неполадок

### Проблема: Не удается подключиться к MariaDB
**Решение**: 
```bash
# Проверка статуса сервиса
sudo systemctl status mariadb

# Перезапуск сервиса
sudo systemctl restart mariadb

# Проверка подключения
mysql -u botcreator -p -h localhost
```

### Проблема: Ошибка доступа к базе данных
**Решение**:
```bash
# Создание пользователя заново
sudo mysql
CREATE USER 'botcreator'@'localhost' IDENTIFIED BY 'botcreator123';
GRANT ALL PRIVILEGES ON botcreator.* TO 'botcreator'@'localhost';
FLUSH PRIVILEGES;
```

### Проблема: Зависимости не установлены
**Решение**:
```bash
# Переустановка зависимостей
pip install -r requirements.txt

# Проверка версии Python
python3 --version
```

### Проблема: Не работает админ-панель
**Решение**:
```bash
# Проверка прав пользователя
python3 database/manage_db.py show --table users

# Создание нового админа
python3 database/manage_db.py admin --email newadmin@example.com --name NewAdmin --password secret123
```

## 📊 Мониторинг и резервное копирование

### Автоматическое резервное копирование
```bash
# Создание cron задачи
0 2 * * * /path/to/project/database/manage_db.py backup --backup-file /backups/backup_$(date +\%Y\%m\%d).sql
```

### Мониторинг через Docker
```bash
# Статус контейнеров
docker-compose ps

# Логи приложения
docker-compose logs -f app

# Логи базы данных
docker-compose logs -f mariadb
```

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции
3. Внесите изменения
4. Создайте Pull Request

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. См. файл `LICENSE` для подробностей.

## 📞 Поддержка

Если у вас есть вопросы или проблемы:
- Создайте Issue в GitHub
- Обратитесь к документации
- Проверьте раздел "Устранение неполадок"

## 🔮 Планы на будущее

- [ ] Поддержка большего количества блоков
- [ ] Интеграция с другими мессенджерами
- [ ] API для внешних интеграций
- [ ] Мобильное приложение
- [ ] Аналитика использования ботов
- [ ] Шаблоны готовых ботов
- [ ] Кластеризация базы данных
- [ ] Автоматическое масштабирование
- [ ] Расширенная админ-панель с мониторингом
- [ ] Система уведомлений для администраторов

---

**Создавайте умных Telegram ботов без программирования! 🚀**