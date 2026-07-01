"""
爬虫调度器 — 启动时立即执行，30min后第二次，之后每1h
每次爬取后自动触发 Agent 处理管线
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from crawler.runner import crawl_all
from crawler.store import news_store

logger = logging.getLogger("crawler.scheduler")

FIRST_RERUN_DELAY = 30 * 60       # 第二次：30 分钟
SUBSEQUENT_INTERVAL = 60 * 60     # 之后：每 1 小时


class CrawlScheduler:
    """管理爬虫调度 + 自动触发 Agent 管线"""

    def __init__(self):
        self._scheduler = AsyncIOScheduler()
        self._run_count = 0
        self._running = False

    @property
    def run_count(self) -> int:
        return self._run_count

    async def start(self):
        logger.info("Scheduler starting — immediate first crawl")
        self._scheduler.start()
        await self._do_crawl()

        # 启动时立即 dump 一次数据库
        await self._do_db_dump()

        self._scheduler.add_job(
            self._do_crawl,
            "date",
            run_date=datetime.now() + timedelta(seconds=FIRST_RERUN_DELAY),
            id="second_crawl",
        )
        logger.info("Second crawl scheduled in %d min", FIRST_RERUN_DELAY // 60)

    async def _do_crawl(self):
        self._run_count += 1
        self._running = True
        logger.info("Crawl #%d starting...", self._run_count)

        try:
            summary = await asyncio.to_thread(crawl_all)
            for name, result in summary.items():
                if result.get("status") == "ok":
                    logger.info(
                        "  [%s] fetched=%d new=%d",
                        name, result.get("fetched", 0), result.get("new", 0),
                    )
                else:
                    logger.warning("  [%s] ERROR: %s", name, result.get("error", ""))

            # 爬取完成后，触发 Agent 处理管线
            await self._run_agent_pipeline()

        except Exception as e:
            logger.error("Crawl #%d failed: %s", self._run_count, e)
        finally:
            self._running = False

        if self._run_count == 2:
            self._scheduler.add_job(
                self._do_crawl,
                "interval",
                seconds=SUBSEQUENT_INTERVAL,
                id="regular_crawl",
                replace_existing=True,
            )
            # 每小时 dump 一次数据库到 data/
            self._scheduler.add_job(
                self._do_db_dump,
                "interval",
                seconds=SUBSEQUENT_INTERVAL,
                id="db_dump",
            )
            logger.info("Switched to regular interval: every %d min", SUBSEQUENT_INTERVAL // 60)

    async def _run_agent_pipeline(self):
        """爬取完成后，触发 Agent 处理管线"""
        items = news_store.get_all()
        if not items:
            logger.info("Agent pipeline skipped: no items in store")
            return

        try:
            from agent.pipeline import run_pipeline
            logger.info("Triggering agent pipeline with %d store items...", len(items))
            result = await asyncio.to_thread(run_pipeline, items)
            logger.info(
                "Agent pipeline done: analyzed=%d, db_inserted=%d",
                result.get("analyzed", 0),
                result.get("news_inserted", 0),
            )
        except ImportError as e:
            logger.warning("Agent pipeline not available: %s", e)
        except Exception as e:
            logger.error("Agent pipeline failed: %s", e)

    async def _do_db_dump(self):
        """定时将 MySQL 数据 dump 到 data/ 文件夹"""
        try:
            from agent.dump import dump_database
            result = await asyncio.to_thread(dump_database)
            if result:
                logger.info("DB dump saved: %s", os.path.basename(result))
        except ImportError as e:
            logger.warning("Dump module not available: %s", e)
        except Exception as e:
            logger.error("DB dump failed: %s", e)

    def shutdown(self):
        self._scheduler.shutdown(wait=False)
