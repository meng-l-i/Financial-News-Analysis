"""
爬虫执行器 — 通过 subprocess 调用 Scrapy，加载结果到 NewsStore
"""

import json
import os
import subprocess
from datetime import datetime
from crawler.store import news_store
from crawler.tracker import crawl_tracker, ALL_SPIDERS

PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))


def _run_spider(spider_name: str) -> list[dict]:
    """运行单个爬虫并返回抓取结果"""
    #the subthread will use the spider code in spiders folder.
    cmd = ["scrapy", "crawl", spider_name, "-L", "INFO"]

    result = subprocess.run(
        cmd,
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )

    # 无论成败都写日志
    if result.stderr:
        log_dir = os.path.join(PROJECT_DIR, "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"{spider_name}_{datetime.now().strftime('%Y%m%d')}.log")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"\n--- {datetime.now().isoformat()} ---\n")
            f.write(result.stderr)

    if result.returncode != 0:
        error_msg = (result.stderr + result.stdout).strip()
        raise RuntimeError(f"Scrapy exited with code {result.returncode}:\n{error_msg}")

    # 从 scrapy stdout 中提取 JSON feed
    items = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError:
                pass

    return items


def crawl_all() -> dict:
    """运行所有爬虫，增量存入 NewsStore，返回汇总"""
    summary = {}
    for spider_name in ALL_SPIDERS:
        try:
            items = _run_spider(spider_name)
            new_count = news_store.add_batch(items)
            summary[spider_name] = {
                "status": "ok",
                "fetched": len(items),
                "new": new_count,
                "total_store": news_store.count(),
            }
            crawl_tracker.mark_success(spider_name, new_count, news_store.count())
        except Exception as e:
            crawl_tracker.mark_error(spider_name, str(e))
            summary[spider_name] = {
                "status": "error",
                "error": str(e),
            }

    return summary


def crawl_single(spider_name: str) -> dict:
    """运行单个爬虫"""
    try:
        items = _run_spider(spider_name)
        new_count = news_store.add_batch(items)
        crawl_tracker.mark_success(spider_name, new_count, news_store.count())
        return {
            "status": "ok",
            "fetched": len(items),
            "new": new_count,
            "total_store": news_store.count(),
        }
    except Exception as e:
        crawl_tracker.mark_error(spider_name, str(e))
        return {"status": "error", "error": str(e)}
