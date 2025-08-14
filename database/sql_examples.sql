-- Bot Creator Platform - SQL Examples
-- Примеры SQL запросов для управления базой данных

-- =============================================
-- ПОЛЬЗОВАТЕЛИ (USERS)
-- =============================================

-- Создание нового пользователя
INSERT INTO users (email, name, password_hash, created_at, updated_at, is_active) 
VALUES ('user@example.com', 'John Doe', 'hashed_password_here', NOW(), NOW(), TRUE);

-- Поиск пользователя по email
SELECT * FROM users WHERE email = 'user@example.com';

-- Поиск пользователя по Google ID
SELECT * FROM users WHERE google_id = 'google_123';

-- Обновление имени пользователя
UPDATE users SET name = 'Jane Doe', updated_at = NOW() WHERE email = 'user@example.com';

-- Деактивация пользователя (soft delete)
UPDATE users SET is_active = FALSE, updated_at = NOW() WHERE email = 'user@example.com';

-- Получение всех активных пользователей
SELECT id, email, name, created_at FROM users WHERE is_active = TRUE ORDER BY created_at DESC;

-- Подсчет общего количества пользователей
SELECT COUNT(*) as total_users FROM users;

-- Подсчет пользователей по месяцам
SELECT 
    DATE_FORMAT(created_at, '%Y-%m') as month,
    COUNT(*) as new_users
FROM users 
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 12 MONTH)
GROUP BY DATE_FORMAT(created_at, '%Y-%m')
ORDER BY month;

-- =============================================
-- БОТЫ (BOTS)
-- =============================================

-- Создание нового бота
INSERT INTO bots (name, token, config, python_code, created_at, updated_at, is_active, user_id) 
VALUES (
    'My Awesome Bot',
    '1234567890:ABCdefGHIjklMNOpqrsTUVwxyz',
    '{"name": "My Awesome Bot", "description": "A helpful bot", "welcome_message": "Hello!", "help_command": true}',
    'import telebot\n\nTOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"\nbot = telebot.TeleBot(TOKEN)\n\n@bot.message_handler(commands=["start"])\ndef send_welcome(message):\n    bot.reply_to(message, "Hello!")\n\nif __name__ == "__main__":\n    bot.polling(none_stop=True)',
    NOW(),
    NOW(),
    TRUE,
    1
);

-- Получение всех ботов пользователя
SELECT b.*, u.name as user_name 
FROM bots b 
JOIN users u ON b.user_id = u.id 
WHERE b.user_id = 1 AND b.is_active = TRUE 
ORDER BY b.created_at DESC;

-- Поиск ботов по названию
SELECT * FROM bots WHERE name LIKE '%bot%' AND is_active = TRUE;

-- Получение ботов с токенами
SELECT id, name, token, created_at FROM bots WHERE token IS NOT NULL AND is_active = TRUE;

-- Обновление конфигурации бота
UPDATE bots 
SET config = '{"name": "Updated Bot", "description": "Updated description"}', 
    updated_at = NOW() 
WHERE id = 1;

-- Деактивация бота
UPDATE bots SET is_active = FALSE, updated_at = NOW() WHERE id = 1;

-- Подсчет ботов по пользователям
SELECT 
    u.name as user_name,
    COUNT(b.id) as bot_count
FROM users u 
LEFT JOIN bots b ON u.id = b.user_id AND b.is_active = TRUE
GROUP BY u.id, u.name
ORDER BY bot_count DESC;

-- =============================================
-- СЕССИИ (BOT_SESSIONS)
-- =============================================

-- Создание новой сессии
INSERT INTO bot_sessions (user_id, session_data, created_at, updated_at) 
VALUES (1, '{"name": "New Bot", "description": "Bot description"}', NOW(), NOW());

-- Обновление существующей сессии
UPDATE bot_sessions 
SET session_data = '{"name": "Updated Bot", "description": "Updated description"}', 
    updated_at = NOW() 
WHERE user_id = 1;

-- Получение сессии пользователя
SELECT * FROM bot_sessions WHERE user_id = 1;

-- Очистка старых сессий (старше 7 дней)
DELETE FROM bot_sessions 
WHERE updated_at < DATE_SUB(NOW(), INTERVAL 7 DAY);

-- =============================================
-- АНАЛИТИКА И СТАТИСТИКА
-- =============================================

-- Общая статистика
SELECT 
    (SELECT COUNT(*) FROM users WHERE is_active = TRUE) as active_users,
    (SELECT COUNT(*) FROM bots WHERE is_active = TRUE) as active_bots,
    (SELECT COUNT(*) FROM bot_sessions) as active_sessions;

-- Статистика по дням
SELECT 
    DATE(created_at) as date,
    COUNT(*) as new_users
FROM users 
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY DATE(created_at)
ORDER BY date;

-- Топ пользователей по количеству ботов
SELECT 
    u.name,
    u.email,
    COUNT(b.id) as bot_count,
    MAX(b.created_at) as last_bot_created
FROM users u 
LEFT JOIN bots b ON u.id = b.user_id AND b.is_active = TRUE
GROUP BY u.id, u.name, u.email
HAVING bot_count > 0
ORDER BY bot_count DESC
LIMIT 10;

-- Статистика по типам ботов (на основе конфигурации)
SELECT 
    CASE 
        WHEN JSON_EXTRACT(config, '$.welcome_message') IS NOT NULL THEN 'Welcome Bot'
        WHEN JSON_EXTRACT(config, '$.help_command') = true THEN 'Help Bot'
        WHEN JSON_EXTRACT(config, '$.echo_enabled') = true THEN 'Echo Bot'
        ELSE 'Custom Bot'
    END as bot_type,
    COUNT(*) as count
FROM bots 
WHERE is_active = TRUE
GROUP BY bot_type;

-- =============================================
-- ОЧИСТКА И ОБСЛУЖИВАНИЕ
-- =============================================

-- Очистка неактивных пользователей (старше 1 года)
UPDATE users 
SET is_active = FALSE 
WHERE is_active = TRUE 
AND created_at < DATE_SUB(NOW(), INTERVAL 1 YEAR)
AND id NOT IN (SELECT DISTINCT user_id FROM bots WHERE is_active = TRUE);

-- Очистка неактивных ботов (старше 6 месяцев)
UPDATE bots 
SET is_active = FALSE 
WHERE is_active = TRUE 
AND created_at < DATE_SUB(NOW(), INTERVAL 6 MONTH)
AND updated_at < DATE_SUB(NOW(), INTERVAL 6 MONTH);

-- Оптимизация таблиц
OPTIMIZE TABLE users;
OPTIMIZE TABLE bots;
OPTIMIZE TABLE bot_sessions;

-- Проверка целостности данных
SELECT 
    'users' as table_name,
    COUNT(*) as total_records,
    COUNT(CASE WHEN is_active = TRUE THEN 1 END) as active_records
FROM users
UNION ALL
SELECT 
    'bots' as table_name,
    COUNT(*) as total_records,
    COUNT(CASE WHEN is_active = TRUE THEN 1 END) as active_records
FROM bots
UNION ALL
SELECT 
    'bot_sessions' as table_name,
    COUNT(*) as total_records,
    COUNT(*) as active_records
FROM bot_sessions;

-- =============================================
-- РЕЗЕРВНОЕ КОПИРОВАНИЕ
-- =============================================

-- Создание резервной копии (выполнить в командной строке)
-- mysqldump -u botcreator -p botcreator > backup_$(date +%Y%m%d_%H%M%S).sql

-- Восстановление из резервной копии (выполнить в командной строке)
-- mysql -u botcreator -p botcreator < backup_file.sql

-- =============================================
-- ИНДЕКСЫ ДЛЯ ПРОИЗВОДИТЕЛЬНОСТИ
-- =============================================

-- Создание дополнительных индексов для производительности
CREATE INDEX idx_users_email_active ON users(email, is_active);
CREATE INDEX idx_bots_user_active ON bots(user_id, is_active);
CREATE INDEX idx_bots_created_active ON bots(created_at, is_active);
CREATE INDEX idx_sessions_user_updated ON bot_sessions(user_id, updated_at);

-- Проверка использования индексов
EXPLAIN SELECT * FROM users WHERE email = 'user@example.com' AND is_active = TRUE;
EXPLAIN SELECT * FROM bots WHERE user_id = 1 AND is_active = TRUE ORDER BY created_at DESC;