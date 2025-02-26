-- 创建数据库
CREATE DATABASE IF NOT EXISTS wechat_contacts
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- 设置权限
GRANT ALL PRIVILEGES ON wechat_contacts.* TO 'gewechat'@'%';
FLUSH PRIVILEGES; 