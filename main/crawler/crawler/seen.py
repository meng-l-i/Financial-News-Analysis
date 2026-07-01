"""
已抓取内容追踪 — 加载 NewsStore 中的已有链接
爬虫启动时加载，parse 阶段跳过已存在的条目
"""

import json
import logging
import os
from datetime import datetime, timedelta

logger = logging.getLogger("crawler.seen")

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
STORE_FILE = os.path.join(DATA_DIR, "news_store.json")
CUTOFF_DAYS = 5


class SeenTracker:
    """追踪已抓取条目的 (title, link) 和最早日期"""

    def __init__(self):
        self._seen_keys: set[str] = set()
        self._cutoff_date = (datetime.now() - timedelta(days=CUTOFF_DAYS)).strftime("%Y-%m-%d")
        self._load()

    def _key(self, title: str, link: str) -> str:
        return f"{title}||{link}"

    def is_new(self, title: str, link: str) -> bool:
        """判断条目是否为新的（未在 store 中）"""
        return self._key(title, link) not in self._seen_keys

    def is_within_5_days(self, date_str: str) -> bool:
        """判断日期是否在近5天内。格式：YYYY-MM-DD"""
        if not date_str:
            return True  # 无日期信息时保留（不过滤）
        try:
            return date_str >= self._cutoff_date
        except Exception:
            return True

    def _load(self):
        if os.path.exists(STORE_FILE):
            try:
                with open(STORE_FILE, "r", encoding="utf-8") as f:
                    items = json.load(f)
                for key, item in items.items():
                    title = item.get("title", "")
                    link = item.get("link", "")
                    if title and link:
                        self._seen_keys.add(self._key(title, link))
                logger.info("SeenTracker loaded %d existing entries", len(self._seen_keys))
            except (json.JSONDecodeError, IOError) as e:
                logger.warning("Failed to load seen store: %s", e)


# 全局单例
seen_tracker = SeenTracker()
