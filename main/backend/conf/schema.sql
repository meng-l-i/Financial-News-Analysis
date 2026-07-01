-- ============================================
-- CC Platform — 数据库 schema
-- 数据库: news
-- ============================================

-- ============================================
-- 初始化已经有创建了。
-- CREATE DATABASE IF NOT EXISTS news
--   DEFAULT CHARACTER SET utf8mb4
--   DEFAULT COLLATE utf8mb4_unicode_ci;
-- ============================================
USE news;
-- ============================================
-- 领域表
-- ============================================
CREATE TABLE IF NOT EXISTS t_field (
    field_id  INT          NOT NULL AUTO_INCREMENT,
    name      VARCHAR(128) NOT NULL,
    hotscore  INT          NOT NULL DEFAULT 0,
    PRIMARY KEY (field_id),
    UNIQUE KEY uk_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 公司表（外键 → 领域）
-- ============================================
CREATE TABLE IF NOT EXISTS t_company (
    company_id  INT NOT NULL AUTO_INCREMENT,
    name        VARCHAR(256) DEFAULT NULL,
    field_id    INT NOT NULL,
    hotscore    INT NOT NULL DEFAULT 0,
    PRIMARY KEY (company_id),
    CONSTRAINT fk_company_field FOREIGN KEY (field_id) REFERENCES t_field(field_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 新闻表
--   type = 'field'   → tarid → t_field.field_id
--   type = 'company' → tarid → t_company.company_id
-- ============================================
CREATE TABLE IF NOT EXISTS t_news (
    id       INT          NOT NULL AUTO_INCREMENT,
    source   VARCHAR(64)  DEFAULT NULL,
    title    VARCHAR(1024) DEFAULT NULL,
    link     VARCHAR(512) DEFAULT NULL,
    date     DATETIME     DEFAULT NULL,
    data     TEXT         DEFAULT NULL,
    name     VARCHAR(256) NOT NULL,
    type     VARCHAR(64)  NOT NULL,
    hotscore INT          DEFAULT 0,
    tarid    INT          DEFAULT NULL,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
