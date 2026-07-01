"""
Agent 2 — 热度分析器
基于 DeepSeek 内置金融知识分析 hotscore (0-10)
"""

import json
import logging
from typing import List

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

logger = logging.getLogger("agent.analyzer")

ANALYZE_PROMPT = ChatPromptTemplate.from_template("""
你是一个金融投资热度分析师。请根据以下信息评估热度。

对于每个分析对象（领域或公司），结合其近期新闻标题，给出一个 hotscore (0-10)：
- 0-2: 冷门，几乎无市场关注
- 3-4: 一般，有一定讨论但无显著热度
- 5-6: 温热，市场较为关注，有一定投资潜力
- 7-8: 热门，市场高度关注，投资情绪积极
- 9-10: 极热，市场焦点，大量资本涌入

分析因素：新闻频率、政策利好、资金流向、行业趋势、市场情绪。

待分析对象（JSON 数组，每项包含 name/type/topic）：
{items}

请返回 JSON 数组，每项添加 hotscore：
[{{"name": "...", "type": "field或company", "topic": "...", "hotscore": 5, "reason": "简短理由"}}, ...]
""")


class HotscoreAnalyzer:
    """分析领域/公司的金融热度"""

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

    def analyze(self, items: List[dict]) -> List[dict]:
        """分析一批领域/公司对象的 hotscore"""
        results = []
        for i in range(0, len(items), self.batch_size):
            batch = items[i:i + self.batch_size]
            try:
                batch_results = self._analyze_batch(batch)
                results.extend(batch_results)
                logger.info("Analyzed %d/%d items", min(i + self.batch_size, len(items)), len(items))
            except Exception as e:
                logger.error("Analysis failed for batch %d: %s", i // self.batch_size, e)
                for item in batch:
                    item["hotscore"] = 0
                    item["reason"] = f"analysis failed: {str(e)[:50]}"
                results.extend(batch)
        return results

    def _analyze_batch(self, items: List[dict]) -> List[dict]:
        chain = ANALYZE_PROMPT | self.llm | self.parser
        result = chain.invoke({"items": json.dumps(items, ensure_ascii=False)})
        if not isinstance(result, list):
            raise ValueError(f"Expected list, got {type(result)}")
        return result[:len(items)]
