import scrapy
from crawler.items import NewsItem
from crawler.seen import seen_tracker
from crawler.spider_config import spider_url


class CsSpider(scrapy.Spider):
    """
    中国证券报 (cs.com.cn) — 近5天新闻标题与链接
    只爬取新内容，跳过已存在条目
    """
    name = "cs"
    allowed_domains = ["cs.com.cn"]

    custom_settings = {
        "DOWNLOAD_DELAY": 2.0,
    }

    def start_requests(self):
        base = spider_url("cs") or "https://www.cs.com.cn/"
        yield scrapy.Request(url=base, callback=self.parse_list)

    def parse_list(self, response):
        articles = response.css("ul.list li, div.newslist li, div.article-list a, a[href*='html']")
        if not articles:
            articles = response.css("a[href]")

        new_count = 0
        for article in articles:
            link = article.css("a::attr(href)").get() or article.attrib.get("href", "")
            title = (
                article.css("a::text").get()
                or article.css("a::attr(title)").get()
                or article.attrib.get("title", "")
                or ""
            ).strip()

            if not title or len(title) < 4:
                continue

            if link and not link.startswith("http"):
                link = response.urljoin(link)

            date_str = (article.css("span.time::text, .date::text, time::text").get() or "").strip()
            if date_str and not seen_tracker.is_within_5_days(date_str):
                continue
            if not seen_tracker.is_new(title, link):
                continue

            new_count += 1
            yield NewsItem(
                source="中国证券报", title=title, link=link, date=date_str,
            )

        self.logger.info("cs: %d new on %s", new_count, response.url)
