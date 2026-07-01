"""
Agent 1 — 领域与公司提取器（含领域表匹配）
从新闻标题中提取领域 + 公司，匹配 conf/fields.json 已有领域或建议新增
"""

import json
import logging
import os
from typing import List

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

logger = logging.getLogger("agent.extractor")

FIELDS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "conf", "fields.json",
)

EXTRACT_PROMPT = ChatPromptTemplate.from_template("""
你是一个金融新闻分析专家。请分析以下新闻标题。

已有领域表（优先匹配，若无匹配则给出一个新领域名）：
{known_fields}

对于每条标题，先判断是否与金融、工业、商业相关：
- 纯政治新闻（领导人会晤、外交访问、选举等）、社会新闻（天灾、节日、文体等）→ relevant: false
- 概述性新闻无具体行业指向且无公司关联 → relevant: false
- 涉及行业动态、公司动态、股市、投资、产业链、政策利好方向 → relevant: true

仅当 relevant 为 true 时提取：
- field: 优先从已有领域表中选择最匹配的领域，若无匹配则给出一个简洁的新领域名（2-6字）
- field_action: "match"（匹配已有领域）或 "new"（建议新增领域）
- company: 新闻关联的公司名称（如果标题中没有明确提及具体公司，则为 null）

输入是一组新闻标题（JSON 数组），请返回相同长度的 JSON 数组。

标题列表：
{titles}

请只返回 JSON 数组，不要包含其他文字。
输出格式：[{{"relevant": true, "field": "领域名", "field_action": "match|new", "company": "公司名或null"}}, {{"relevant": false, "field": null, "field_action": null, "company": null}}, ...]
""")


class FieldCompanyExtractor:
    """从新闻标题中提取领域和公司，匹配或新增领域表"""

    def __init__(self, config: dict):
        llm_config = config.get("deepseek", {})
        self.llm = ChatOpenAI(
            model=llm_config.get("model", "deepseek-chat"),
            openai_api_key=llm_config.get("api_key", ""),
            openai_api_base=llm_config.get("base_url", "https://api.deepseek.com/v1"),
            temperature=llm_config.get("temperature", 0.3),
            max_tokens=llm_config.get("max_tokens", 2048),
        )
        self.parser = JsonOutputParser()
        self.batch_size = config.get("processing", {}).get("batch_size", 10)
        self._known_fields: List[str] = []
        self._load_fields()

    def _load_fields(self):
        if os.path.exists(FIELDS_FILE):
            try:
                with open(FIELDS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._known_fields = data.get("fields", [])
                logger.info("Loaded %d known fields from fields.json", len(self._known_fields))
            except Exception as e:
                logger.warning("Failed to load fields.json: %s", e)
                self._known_fields = []

    def _save_new_fields(self, new_fields: List[str]):
        """将新领域追加到 fields.json"""
        if not new_fields:
            return
        try:
            with open(FIELDS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            existing = set(data.get("fields", []))
            added = [f for f in new_fields if f and f not in existing]
            if added:
                data["fields"].extend(added)
                with open(FIELDS_FILE, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                logger.info("Added %d new fields to fields.json: %s", len(added), added)
                self._known_fields.extend(added)
        except Exception as e:
            logger.warning("Failed to save new fields: %s", e)

    @property
    def known_fields(self) -> List[str]:
        return list(self._known_fields)

    def extract(self, titles: List[str]) -> List[dict]:
        """批量提取，返回 [{relevant, field, field_action, company}, ...]"""
        results = []
        new_fields = []
        for i in range(0, len(titles), self.batch_size):
            batch = titles[i:i + self.batch_size]
            try:
                batch_results = self._extract_batch(batch)
                results.extend(batch_results)
                for r in batch_results:
                    if r.get("field_action") == "new" and r.get("field"):
                        new_fields.append(r["field"])
                relevant_count = sum(1 for r in batch_results if r.get("relevant"))
                logger.info("Extracted %d/%d titles (%d relevant, %d new fields)",
                           min(i + self.batch_size, len(titles)), len(titles),
                           relevant_count, sum(1 for r in batch_results if r.get("field_action") == "new"))
            except Exception as e:
                logger.error("Extraction failed for batch %d: %s", i // self.batch_size, e)
                results.extend([{"relevant": False, "field": None, "field_action": None, "company": None}] * len(batch))

        # 持久化新发现的领域
        self._save_new_fields(new_fields)
        return results

    def _extract_batch(self, titles: List[str]) -> List[dict]:
        titles_json = json.dumps(titles, ensure_ascii=False)
        fields_json = json.dumps(self._known_fields, ensure_ascii=False)
        chain = EXTRACT_PROMPT | self.llm | self.parser
        result = chain.invoke({"titles": titles_json, "known_fields": fields_json})
        if not isinstance(result, list):
            raise ValueError(f"Expected list, got {type(result)}")
        while len(result) < len(titles):
            result.append({"relevant": False, "field": None, "field_action": None, "company": None})
        return result[:len(titles)]
