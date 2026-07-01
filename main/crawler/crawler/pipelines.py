import json
import os
from datetime import datetime


class JsonOutputPipeline:
    """将 NewsItem 以标题-链接字典形式输出到 JSON 文件"""

    @classmethod
    def from_crawler(cls, crawler):
        pipe = cls()
        pipe._crawler = crawler
        return pipe

    def open_spider(self, spider):
        self._spider = spider
        self.items = []

    def process_item(self, item, spider=None):
        self.items.append({
            "source": item.get("source", ""),
            "title": item.get("title", ""),
            "link": item.get("link", ""),
            "date": item.get("date", ""),
        })
        return item

    def close_spider(self, spider=None):
        if not self.items:
            return
        spider = spider or getattr(self, "_spider", None)
        name = spider.name if spider else "unknown"
        os.makedirs("output", exist_ok=True)
        filename = f"output/{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.items, f, ensure_ascii=False, indent=2)
