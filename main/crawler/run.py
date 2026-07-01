#!/usr/bin/env python3
"""
CC Platform Crawler — 走 runner 爬取 + 入 store + 可选触发 agent
用法:
  python run.py                  # 运行全部爬虫
  python run.py cls              # 单独运行财联社
  python run.py cls --agent      # 爬虫 + agent
  python run.py --agent-only     # 仅跑 agent（不爬虫）
"""
import sys
#windows上默认用proactoreventloop(主线程和子线程同级，future可以跨线程传递)，和scrapy不兼容。linux直接用。
if sys.platform == "win32":
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from crawler.runner import crawl_single
from crawler.store import news_store
from crawler.spider_config import enabled_spiders


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    run_agent = "--agent" in sys.argv
    agent_only = "--agent-only" in sys.argv

    if agent_only:
        items = news_store.get_all()
        if items:
            print(f"[agent-only] Running pipeline on {len(items)} items...")
            from agent.pipeline import run_pipeline
            result = run_pipeline(items)
            print(f"[agent-only] Done: analyzed={result.get('analyzed',0)} db={result.get('news_inserted',0)}")
        else:
            print("[agent-only] No items in store, skipping")
        return

    all_spiders = enabled_spiders()
    selected = args if args else all_spiders
    for name in selected:
        if name not in all_spiders:
            print(f"Unknown spider: {name}. Available: {all_spiders}")
            sys.exit(1)

    summary = {}
    for name in selected:
        result = crawl_single(name)
        summary[name] = result

    for name, result in summary.items():
        status = result.get("status", "?")
        if status == "ok":
            print(f"  [{name}] fetched={result.get('fetched',0)} new={result.get('new',0)} store={result.get('total_store',0)}")
        else:
            print(f"  [{name}] ERROR: {result.get('error','')[:80]}")

    if run_agent:
        items = news_store.get_all()
        if items:
            print(f"\n[agent] Running pipeline on {len(items)} items...")
            from agent.pipeline import run_pipeline
            result = run_pipeline(items)
            print(f"[agent] Done: analyzed={result.get('analyzed',0)} db={result.get('news_inserted',0)}")
        else:
            print("\n[agent] No items in store, skipping")

    print(f"\nDone. Store: {news_store.count()} items")


if __name__ == "__main__":
    main()
