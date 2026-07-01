"""
数据存储模块 — 内存 + JSON 持久化
跟踪已抓取条目，只保留新出现的新闻
"""

import json
import os
from datetime import datetime
from typing import Dict, List

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
STORE_FILE = os.path.join(DATA_DIR, "news_store.json")


class NewsStore:
    """以 (source, title, link) 为唯一键存储新闻条目"""

    def __init__(self):
        self._items: Dict[str, dict] = {}
        self._load()

    def _key(self, source: str, title: str, link: str) -> str:
        return f"{source}||{title}||{link}"

    def add(self, source: str, title: str, link: str, date: str = "", data: str = "") -> bool:
        k = self._key(source, title, link)
        if k in self._items:
            return False
        self._items[k] = {
            "source": source,
            "title": title,
            "link": link,
            "date": date,
            "data": data,
            "crawled_at": datetime.now().isoformat(),
        }
        return True

    def add_batch(self, items: List[dict]) -> int:
        added = 0
        for item in items:
            if self.add(
                item.get("source", ""),
                item.get("title", ""),
                item.get("link", ""),
                item.get("date", ""),
                item.get("data", ""),
            ):
                added += 1
        if added > 0:
            self._save()
        return added

    def get_all(self) -> List[dict]:
        return list(self._items.values())

    def count(self) -> int:
        return len(self._items)

    def _save(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(STORE_FILE, "w", encoding="utf-8") as f:
            json.dump(self._items, f, ensure_ascii=False, indent=2)

    def _load(self):
        if os.path.exists(STORE_FILE):
            try:
                with open(STORE_FILE, "r", encoding="utf-8") as f:
                    self._items = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._items = {}


# 全局单例
news_store = NewsStore()
