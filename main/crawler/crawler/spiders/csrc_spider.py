import scrapy
from crawler.items import NewsItem
from crawler.seen import seen_tracker
from crawler.spider_config import spider_url


class CsrcSpider(scrapy.Spider):
    """
    证监会 (csrc.gov.cn) — 证券市场快报（近5天）
    抓取统计信息页面，分离出多个标题，链接均指向该快报页面。
    只爬取新内容，跳过已存在条目。
    """
    name = "csrc"
    allowed_domains = ["csrc.gov.cn"]

    custom_settings = {
        "DOWNLOAD_DELAY": 2.0,
    }

    def start_requests(self):
        url = spider_url("csrc") or "https://www.csrc.gov.cn/csrc/c100028/common_list.shtml"
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        """解析快报页面，分离所有标题，链接统一指向该页面"""
        page_link = response.url

        title_selectors = [
            "h3::text", "h4::text", "strong::text",
            ".title::text", ".article-title::text",
            "p::text", "td::text", "li::text",
        ]

        new_count = 0
        found_titles = set()
        for selector in title_selectors:
            for text in response.css(selector).getall():
                text = text.strip()
                if not (4 <= len(text) <= 200) or text.isdigit():
                    continue
                if text in found_titles:
                    continue
                found_titles.add(text)

                if seen_tracker.is_new(text, page_link):
                    new_count += 1
                    yield NewsItem(
                        source="证监会",
                        title=text,
                        link=page_link,
                        date="",
                    )

        self.logger.info("csrc: %d new titles from %s", new_count, page_link)
