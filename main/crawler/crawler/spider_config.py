"""从 conf/spiders.json 加载每个爬虫的 URL 配置"""
import json
import os

CONF_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "conf")
SPIDERS_FILE = os.path.join(CONF_DIR, "spiders.json")


def load() -> dict:
    if os.path.exists(SPIDERS_FILE):
        with open(SPIDERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def spider_url(spider_name: str) -> str | None:
    data = load()
    spider = data.get("spiders", {}).get(spider_name, {})
    enabled = spider.get("enabled", True)
    url = spider.get("url", "")
    return url if enabled and url else None


def enabled_spiders() -> list[str]:
    """返回 spiders.json 中 enabled=true 的爬虫名称列表"""
    data = load()
    spiders = data.get("spiders", {})
    return [name for name, cfg in spiders.items() if cfg.get("enabled", True)]
