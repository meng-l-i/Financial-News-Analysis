"""
爬虫运行追踪 — 记录每个爬虫的上次运行时间和状态
"""

import json
import os
from datetime import datetime
from typing import Dict

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
TRACKER_FILE = os.path.join(DATA_DIR, "crawl_tracker.json")

from crawler.spider_config import enabled_spiders

ALL_SPIDERS = enabled_spiders()


class CrawlTracker:
    """追踪每个爬虫的运行状态"""

    def __init__(self):
        self._records: Dict[str, dict] = {}
        self._load()
        # 初始化未记录的爬虫
        for name in ALL_SPIDERS:
            if name not in self._records:
                self._records[name] = {
                    "last_success": None,
                    "last_status": "never",
                    "last_error": None,
                    "new_items": 0,
                    "total_items": 0,
                }

    def mark_success(self, spider_name: str, new_items: int, total_items: int):
        self._records[spider_name] = {
            "last_success": datetime.now().isoformat(),
            "last_status": "ok",
            "last_error": None,
            "new_items": new_items,
            "total_items": total_items,
        }
        self._save()

    def mark_error(self, spider_name: str, error: str):
        if spider_name in self._records:
            self._records[spider_name]["last_status"] = "error"
            self._records[spider_name]["last_error"] = error
        self._save()

    def last_success(self, spider_name: str) -> str | None:
        return self._records.get(spider_name, {}).get("last_success")

    def all_ok(self) -> bool:
        """检查所有爬虫是否至少成功过一次"""
        for name in ALL_SPIDERS:
            if self._records.get(name, {}).get("last_status") != "ok":
                return False
        return True

    def get_all(self) -> dict:
        return dict(self._records)

    def _save(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(TRACKER_FILE, "w", encoding="utf-8") as f:
            json.dump(self._records, f, ensure_ascii=False, indent=2)

    def _load(self):
        if os.path.exists(TRACKER_FILE):
            try:
                with open(TRACKER_FILE, "r", encoding="utf-8") as f:
                    self._records = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._records = {}


# 全局单例
crawl_tracker = CrawlTracker()
