"""
MySQL 数据持久化导出 — 定时 dump 到 data/ 文件夹
连接参数优先从环境变量读取
"""

import logging
import os
import subprocess
from datetime import datetime

logger = logging.getLogger("agent.dump")

PROJECT_DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
)


def _get_config() -> dict:
    return {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": os.getenv("MYSQL_PORT", "3306"),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", "root"),
        "database": os.getenv("MYSQL_DATABASE", "news"),
    }


def dump_database(config: dict = None) -> str | None:
    cfg = config or _get_config()
    os.makedirs(PROJECT_DATA_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(PROJECT_DATA_DIR, f"news_dump_{timestamp}.sql")

    cmd = [
        "mysqldump",
        f"--host={cfg['host']}", f"--port={cfg['port']}",
        f"--user={cfg['user']}", f"--password={cfg['password']}",
        "--single-transaction", "--routines", "--triggers",
        "--default-character-set=utf8mb4",
        cfg["database"],
    ]

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True, timeout=60)
        if result.returncode != 0:
            logger.error("mysqldump failed: %s", result.stderr.strip()[:200])
            os.remove(filepath)
            return None
        logger.info("Database dumped to %s (%d bytes)", filepath, os.path.getsize(filepath))
        _cleanup_old(PROJECT_DATA_DIR, keep=7)
        return filepath
    except FileNotFoundError:
        logger.warning("mysqldump not found, skipping DB dump")
        return None
    except Exception as e:
        logger.error("Dump failed: %s", e)
        return None


def _cleanup_old(directory: str, keep: int = 7):
    files = sorted(
        [f for f in os.listdir(directory) if f.startswith("news_dump_") and f.endswith(".sql")],
        reverse=True,
    )
    for old in files[keep:]:
        os.remove(os.path.join(directory, old))
