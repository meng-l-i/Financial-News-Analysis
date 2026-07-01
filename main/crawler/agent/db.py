"""
MySQL 持久化 — 写入 t_news / t_field / t_company
连接参数优先从环境变量读取
"""

import logging
import os
from typing import List

logger = logging.getLogger("agent.db")


def _env(key: str, default: str) -> str:
    return os.getenv(key, default)


class NewsDB:

    def __init__(self):
        self._host = _env("MYSQL_HOST", "localhost")
        self._port = int(_env("MYSQL_PORT", "3306"))
        self._user = _env("MYSQL_USER", "root")
        self._password = _env("MYSQL_PASSWORD", "root")
        self._database = _env("MYSQL_DATABASE", "news")
        self._conn = None

    def _get_conn(self):
        if self._conn is None:
            try:
                import pymysql
                self._conn = pymysql.connect(
                    host=self._host, port=self._port,
                    user=self._user, password=self._password,
                    database=self._database, charset="utf8mb4",
                )
                self._ensure_tables()
            except ImportError:
                logger.warning("pymysql not installed, MySQL persistence disabled")
                return None
            except Exception as e:
                logger.warning("MySQL connection failed (%s:%s): %s", self._host, self._port, e)
                return None
        return self._conn

    def _ensure_tables(self):
        conn = self._conn
        if conn is None:
            return
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS t_field (
                        field_id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(128) NOT NULL UNIQUE,
                        hotscore INT NOT NULL DEFAULT 0
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS t_company (
                        company_id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(256) DEFAULT NULL,
                        field_id INT NOT NULL,
                        hotscore INT NOT NULL DEFAULT 0,
                        CONSTRAINT fk_company_field FOREIGN KEY (field_id)
                            REFERENCES t_field(field_id)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS t_news (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        source VARCHAR(64),
                        title VARCHAR(1024),
                        link VARCHAR(512),
                        date DATETIME,
                        data TEXT,
                        name VARCHAR(256) NOT NULL,
                        type VARCHAR(64) NOT NULL,
                        hotscore INT DEFAULT 0,
                        tarid INT DEFAULT NULL
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """)
            conn.commit()
        except Exception as e:
            logger.warning("Failed to ensure tables: %s", e)

    def upsert_field(self, name: str, hotscore: int) -> int | None:
        conn = self._get_conn()
        if conn is None:
            return None
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO t_field (name, hotscore) VALUES (%s, %s) "
                    "ON DUPLICATE KEY UPDATE hotscore = GREATEST(hotscore, VALUES(hotscore))",
                    (name[:128], hotscore),
                )
                cur.execute("SELECT field_id FROM t_field WHERE name = %s", (name[:128],))
                row = cur.fetchone()
            conn.commit()
            return row[0] if row else None
        except Exception as e:
            logger.error("upsert_field failed: %s", e)
            return None

    def upsert_company(self, name: str, field_id: int, hotscore: int) -> int | None:
        """写入或更新 t_company，返回 company_id"""
        conn = self._get_conn()
        if conn is None:
            return None
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO t_company (name, field_id, hotscore) VALUES (%s, %s, %s)",
                    (name[:256], field_id, hotscore),
                )
                cid = cur.lastrowid
            conn.commit()
            return cid
        except Exception as e:
            logger.error("upsert_company failed: %s", e)
            return None

    def insert_news(self, items: List[dict]) -> int:
        conn = self._get_conn()
        if conn is None:
            return 0
        count = 0
        try:
            with conn.cursor() as cur:
                for item in items:
                    cur.execute(
                        "INSERT INTO t_news (source, title, link, date, data, name, type, hotscore, tarid) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (
                            item.get("source", "")[:64],
                            item.get("title", "")[:1024],
                            item.get("link", "")[:512],
                            item.get("date", "")[:32],
                            item.get("data", ""),
                            item.get("name", "")[:256],
                            item.get("type", "field"),
                            item.get("hotscore", 0),
                            item.get("tarid"),
                        ),
                    )
                    count += 1
            conn.commit()
            logger.info("Inserted %d rows into t_news", count)
        except Exception as e:
            logger.error("MySQL insert failed: %s", e)
            try:
                conn.rollback()
            except Exception:
                pass
        return count

    def close(self):
        if self._conn:
            try:
                self._conn.close()
            except Exception:
                pass
            self._conn = None


news_db = NewsDB()
