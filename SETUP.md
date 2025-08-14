# Инструкция по запуску Bot Creator Platform

## 🚀 Быстрый запуск

### 1. Активация виртуального окружения
```bash
source venv/bin/activate
```

### 2. Запуск приложения
```bash
python3 app.py
```

### 3. Открытие в браузере
Перейдите по адресу: http://localhost:5000

## 🔧 Альтернативные способы запуска

### Способ 1: Через основной файл
```bash
cd /workspace
source venv/bin/activate
python3 app.py
```

### Способ 2: Через тестовый файл
```bash
cd /workspace
source venv/bin/activate
python3 test_app.py
```

### Способ 3: Через Gunicorn (для продакшена)
```bash
cd /workspace
source venv/bin/activate
gunicorn -w 4 -b 0.00.0:5000 app:app
```

## 📋 Проверка работы

### Проверка порта
```bash
netstat -tlnp | grep :5000
```

### Тест через curl
```bash
curl http://localhost:5000
```

### Проверка процессов
```bash
ps aux | grep python
```

## 🐛 Устранение проблем

### Проблема: Порт 5000 занят
```bash
# Найти процесс
lsof -i :5000

# Завершить процесс
kill -9 <PID>
```

### Проблема: Виртуальное окружение не активируется
```bash
# Пересоздать окружение
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Проблема: Зависимости не установлены
```bash
source venv/bin/activate
pip install -r requirements.txt
```

## 🌐 Доступ к приложению

После успешного запуска:
- **Локально**: http://localhost:5000
- **В сети**: http://YOUR_IP:5000
- **В Docker**: http://localhost:5000

## 📱 Функции платформы

1. **Регистрация и вход** - создание аккаунта или вход через Google
2. **Создание ботов** - блочный интерфейс для настройки
3. **Генерация кода** - автоматическое создание Python скриптов
4. **Сохранение сессий** - автоматическое сохранение прогресса
5. **Управление ботами** - просмотр и редактирование созданных ботов

## 🔐 Настройка Google OAuth

1. Создайте файл `.env` на основе `.env.example`
2. Получите Client ID и Client Secret в Google Cloud Console
3. Добавьте их в `.env` файл
4. Перезапустите приложение

## 📊 Структура проекта

```
bot-creator-platform/
├── app.py              # Основное Flask приложение
├── run.py              # Скрипт запуска
├── test_app.py         # Тестовое приложение
├── requirements.txt    # Зависимости Python
├── .env.example       # Пример переменных окружения
├── templates/          # HTML шаблоны
├── static/            # CSS, JS, изображения
└── README.md          # Документация
```

## 🎯 Следующие шаги

1. Запустите приложение
2. Зарегистрируйтесь или войдите
3. Создайте своего первого бота
4. Изучите сгенерированный код
5. Настройте Google OAuth для полной функциональности

---

**Успешного создания ботов! 🚀**