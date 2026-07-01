#!/usr/bin/env python3
"""
CC Platform Crawler Server — FastAPI
接口:
  GET /health — 检查爬虫运行状态
  GET /get    — 获取所有已抓取数据
"""

import logging
import sys
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse

# 确保项目根目录在 sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from crawler.store import news_store
from crawler.tracker import crawl_tracker
from crawler.scheduler import CrawlScheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("crawler.server")

scheduler = CrawlScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动时初始化调度器，关闭时清理"""
    logger.info("CC Crawler Server starting on port 5080")
    await scheduler.start()
    yield
    scheduler.shutdown()
    logger.info("CC Crawler Server stopped")


app = FastAPI(
    title="CC Crawler Server",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health():
    """检查所有爬虫是否成功运行过"""
    status = crawl_tracker.get_all()
    all_ok = crawl_tracker.all_ok()

    return JSONResponse({
        "status": "ok" if all_ok else "degraded",
        "spiders": status,
        "store_count": news_store.count(),
        "crawl_count": scheduler.run_count,
    })


@app.get("/get")
async def get_data(source: str = None):
    """
    返回 AI 处理后的分析数据（来自 output/analyzed_*.json）
    可选参数 source 过滤: 财联社 / 证券时报 / 中国证券报 / 证监会
    """
    import glob
    import json

    output_dir = os.path.join(os.path.dirname(__file__), "output")
    files = sorted(glob.glob(os.path.join(output_dir, "analyzed_*.json")), reverse=True)
    if not files:
        return JSONResponse({"count": 0, "data": [], "note": "no analyzed data yet"})

    with open(files[0], "r", encoding="utf-8") as f:
        items = json.load(f)

    if source:
        items = [it for it in items if it.get("source") == source]

    return JSONResponse({
        "count": len(items),
        "source_file": os.path.basename(files[0]),
        "data": items,
    })
