-- Bot Creator Platform Database Initialization Script
-- MariaDB/MySQL

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS `botcreator` 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- Use the database
USE `botcreator`;

-- Drop existing tables if they exist (for clean installation)
DROP TABLE IF EXISTS `bot_sessions`;
DROP TABLE IF EXISTS `bots`;
DROP TABLE IF EXISTS `users`;

-- Create users table
CREATE TABLE `users` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `email` VARCHAR(120) NOT NULL,
    `name` VARCHAR(120) NOT NULL,
    `google_id` VARCHAR(120) NULL,
    `password_hash` VARCHAR(200) NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `is_active` BOOLEAN NOT NULL DEFAULT TRUE,
    `is_admin` BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_email` (`email`),
    UNIQUE KEY `uk_google_id` (`google_id`),
    INDEX `idx_email` (`email`),
    INDEX `idx_google_id` (`google_id`),
    INDEX `idx_created_at` (`created_at`),
    INDEX `idx_is_admin` (`is_admin`),
    INDEX `idx_is_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create bots table
CREATE TABLE `bots` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(120) NOT NULL,
    `token` VARCHAR(200) NULL,
    `config` TEXT NOT NULL,
    `python_code` TEXT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `is_active` BOOLEAN NOT NULL DEFAULT TRUE,
    `user_id` INT NOT NULL,
    PRIMARY KEY (`id`),
    INDEX `idx_name` (`name`),
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_created_at` (`created_at`),
    INDEX `idx_is_active` (`is_active`),
    CONSTRAINT `fk_bots_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create bot_sessions table
CREATE TABLE `bot_sessions` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `user_id` INT NOT NULL,
    `session_data` TEXT NOT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_updated_at` (`updated_at`),
    CONSTRAINT `fk_bot_sessions_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert sample data (optional)
-- Note: The password hash below is for 'password' - you should change this in production
INSERT INTO `users` (`email`, `name`, `google_id`, `password_hash`, `created_at`, `updated_at`, `is_active`, `is_admin`) VALUES
('admin', 'Administrator', NULL, '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3bp.gS8sDi', NOW(), NOW(), TRUE, TRUE),
('demo@google.com', 'Demo Google User', 'google_123', NULL, NOW(), NOW(), TRUE, FALSE);

-- Insert sample bot
INSERT INTO `bots` (`name`, `token`, `config`, `python_code`, `created_at`, `updated_at`, `is_active`, `user_id`) VALUES
('Sample Bot', '1234567890:ABCdefGHIjklMNOpqrsTUVwxyz', '{"name": "Sample Bot", "description": "A sample bot for demonstration", "welcome_message": "Hello! Welcome to the sample bot!", "help_command": true, "about_command": true, "custom_responses": [], "echo_enabled": false}', 'import telebot\n\nTOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"\nbot = telebot.TeleBot(TOKEN)\n\n@bot.message_handler(commands=["start"])\ndef send_welcome(message):\n    bot.reply_to(message, "Hello! Welcome to the sample bot!")\n\nif __name__ == "__main__":\n    bot.polling(none_stop=True)', NOW(), NOW(), TRUE, 1);

-- Create indexes for better performance
CREATE INDEX `idx_users_active` ON `users` (`is_active`);
CREATE INDEX `idx_users_admin` ON `users` (`is_admin`);
CREATE INDEX `idx_bots_active_user` ON `bots` (`is_active`, `user_id`);
CREATE INDEX `idx_sessions_user_updated` ON `bot_sessions` (`user_id`, `updated_at`);

-- Show table structure
SHOW TABLES;
DESCRIBE users;
DESCRIBE bots;
DESCRIBE bot_sessions;