# 🚀 Быстрый запуск Bot Creator Platform с MariaDB

## ⚡ За 5 минут

### 1. Установите MariaDB
```bash
sudo apt update
sudo apt install -y mariadb-server mariadb-client
sudo systemctl start mariadb
sudo systemctl enable mariadb
```

### 2. Настройте базу данных
```bash
# Автоматическая настройка
chmod +x database/setup_database.sh
./database/setup_database.sh
```

### 3. Активируйте окружение
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Запустите приложение
```bash
python3 app.py
```

### 5. Откройте браузер
http://localhost:5000

---

## 🔐 Вход в админ-панель

### Учетные данные по умолчанию
- **Логин**: `admin`
- **Пароль**: `password`

---

## 🔧 Управление базой

### Создание таблиц:
```bash
python3 database/manage_db.py create
```

### Создание админа:
```bash
python3 database/manage_db.py admin --email admin@example.com --name Admin --password secret123
```

### Резервная копия:
```bash
python3 database/manage_db.py backup --backup-file backup.sql
```

---

## 📊 Структура базы

- **users** - пользователи и аутентификация
- **bots** - созданные боты
- **bot_sessions** - сохраненные сессии

---

## 🎯 Что получите

✅ **Веб-сайт для создания Telegram ботов**  
✅ **MariaDB вместо SQLite**  
✅ **Блочный интерфейс без программирования**  
✅ **Автоматическая генерация Python кода**  
✅ **Сохранение сессий в базе данных**  
✅ **Готовность к продакшену**  
✅ **Полноценная админ-панель**  

---

**Готово! Создавайте умных ботов с надежной базой данных! 🤖✨**