"""
Agent 处理管线
1. 从 news_store 获取爬虫数据
2. Agent 1 → 提取领域 + 公司
3. Agent 2 → 分析 hotscore（用 data 正文）
4. 保存 JSON → output/  + MySQL
"""
import json
import logging
import os
from datetime import datetime
from typing import List

from agent.extractor import FieldCompanyExtractor
from agent.analyzer import HotscoreAnalyzer
from agent.db import news_db

logger = logging.getLogger("agent.pipeline")

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONF_DIR = os.path.join(PROJECT_DIR, "conf")
OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")
PROCESSED_FILE = os.path.join(OUTPUT_DIR, "agent_processed.json")


def _load_processed() -> set:
    """加载已处理过的 (source, title, link) 键集合"""
    if os.path.exists(PROCESSED_FILE):
        with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def _save_processed(keys: set):
    """保存已处理键集合"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(PROCESSED_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(keys), f)


def _load_config() -> dict:
    config_path = os.path.join(CONF_DIR, "agent.json")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _build_items_from_titles(titles_data: List[dict], results: List[dict]) -> tuple[List[dict], int]:
    items = []
    skipped = 0
    for news, extracted in zip(titles_data, results):
        if not extracted.get("relevant"):
            skipped += 1
            continue

        field_name = extracted.get("field", "")
        company_name = extracted.get("company")
        content = news.get("data", "") or news.get("title", "")

        base = {
            "title": news.get("title", ""),
            "content": content,
            "newslink": news.get("link", ""),
            "source": news.get("source", ""),
            "date": news.get("date", ""),
            "data": news.get("data", ""),
        }

        if company_name and company_name != "null":
            items.append({**base, "name": company_name, "type": "company", "field_name": field_name})
        elif field_name:
            items.append({**base, "name": field_name, "type": "field"})

    return items, skipped


def run_pipeline(news_items: List[dict]) -> dict:
    if not news_items:
        logger.info("No items to process")
        return {"status": "skipped", "reason": "no items"}

    # 过滤已处理过的条目
    processed = _load_processed()
    unprocessed = []
    new_keys = set()
    for it in news_items:
        key = f"{it.get('source','')}||{it.get('title','')}||{it.get('link','')}"
        if key not in processed:
            unprocessed.append(it)
            new_keys.add(key)

    skipped_count = len(news_items) - len(unprocessed)
    if skipped_count > 0:
        logger.info("Skipping %d already-processed items", skipped_count)

    if not unprocessed:
        logger.info("No new items to process")
        return {"status": "skipped", "reason": "all items already processed"}

    config = _load_config()
    logger.info("Pipeline starting: %d new / %d total items", len(unprocessed), len(news_items))

    # Agent 1 — 提取领域 + 公司
    logger.info("[1/5] Extracting fields and companies...")
    extractor = FieldCompanyExtractor(config)
    titles = [it.get("title", "") for it in unprocessed]
    extracted = extractor.extract(titles)

    # 构建分析对象（含正文 data）
    analyze_items, irrelevant = _build_items_from_titles(unprocessed, extracted)
    logger.info("[2/5] Built %d analysis items, skipped %d irrelevant", len(analyze_items), irrelevant)

    # Agent 2 — 热度分析，用正文 content 代替 topic 传入
    logger.info("[3/5] Analyzing hotscores...")
    if analyze_items:
        # 保留原始字段映射 key=(name,type)，等 analyzer 返回后合并
        item_index: dict[tuple, dict] = {}
        for it in analyze_items:
            key = (it["name"], it["type"])
            item_index[key] = it
            it["topic"] = it.pop("content", it.get("topic", ""))

        analyzer = HotscoreAnalyzer(config)
        analyzed = analyzer.analyze(analyze_items)

        # 把原始字段合回 analyzer 结果
        for a in analyzed:
            key = (a.get("name", ""), a.get("type", ""))
            if key in item_index:
                a.update(item_index[key])
    else:
        analyzed = []

    # 保存
    logger.info("[4/5] Saving JSON + MySQL...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = os.path.join(OUTPUT_DIR, f"analyzed_{timestamp}.json")

    output_objects = []
    news_records = []
    field_upserted = 0
    company_upserted = 0

    field_id_map: dict[str, int] = {}
    for item in analyzed:
        fname = item.get("field_name") or item.get("name")
        if item.get("type") == "field" or item.get("type") == "company":
            fid = news_db.upsert_field(fname, 0)
            if fid:
                field_id_map[fname] = fid

    for item in analyzed:
        item_type = item.get("type", "field")
        item_name = item.get("name", "")
        hotscore = item.get("hotscore", 0)
        field_name = item.get("field_name", "")

        tarid = None
        if item_type == "field":
            fid = field_id_map.get(item_name)
            if fid:
                news_db.upsert_field(item_name, hotscore)
                field_upserted += 1
                tarid = fid
        elif item_type == "company":
            fid = field_id_map.get(field_name)
            if fid:
                cid = news_db.upsert_company(item_name, fid, hotscore)
                if cid:
                    tarid = cid
                    company_upserted += 1

        news_records.append({
            "source": item.get("source", ""),
            "title": item.get("topic", ""),
            "link": item.get("newslink", ""),
            "date": item.get("date", ""),
            "data": item.get("data", ""),
            "name": item_name,
            "type": item_type,
            "hotscore": hotscore,
            "tarid": tarid,
        })

        # 保留原始爬虫字段 + agent 新增字段
        output_objects.append({
            "source": item.get("source", ""),
            "title": item.get("topic", ""),
            "link": item.get("newslink", ""),
            "date": item.get("date", ""),
            "data": item.get("data", ""),
            "name": item_name,
            "type": item_type,
            "hotscore": hotscore,
        })

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output_objects, f, ensure_ascii=False, indent=2)

    db_count = news_db.insert_news(news_records)

    # 标记已处理
    _save_processed(processed | new_keys)
    logger.info("[5/5] Done: fields=%d companies=%d news=%d json=%s",
                field_upserted, company_upserted, db_count, json_path)

    return {
        "status": "ok", "news_input": len(unprocessed),
        "extracted": len(extracted), "analyzed": len(analyzed),
        "fields_upserted": field_upserted, "companies_upserted": company_upserted,
        "news_inserted": db_count, "json_file": json_path,
    }
