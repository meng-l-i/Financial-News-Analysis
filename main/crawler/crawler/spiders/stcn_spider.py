import scrapy
from crawler.items import NewsItem
from crawler.seen import seen_tracker
from crawler.spider_config import spider_url


class StcnSpider(scrapy.Spider):
    """
    证券时报 (stcn.com) — 近5天新闻标题与链接
    只爬取新内容，跳过已存在条目和超过5天的旧闻
    """
    name = "stcn"
    allowed_domains = ["stcn.com"]

    custom_settings = {
        "DOWNLOAD_DELAY": 2.0,
    }

    def start_requests(self):
        base = spider_url("stcn") or "https://www.stcn.com/article/list.html"
        for page in range(1, 11):
            yield scrapy.Request(
                url=f"{base}?page={page}",
                callback=self.parse,
                meta={"page": page},
            )

    def parse(self, response):
        articles = response.css("div.news_list li, ul.news_list li, div.article_list a")
        if not articles:
            articles = response.css("a[href*='/article/'], a[href*='/news/']")

        new_count = 0
        for article in articles:
            link = article.css("a::attr(href)").get() or article.attrib.get("href", "")
            title = (
                article.css("a::attr(title)").get()
                or article.css("a::text").get()
                or article.css("h3::text").get()
                or ""
            ).strip()

            if not title or len(title) < 4:
                continue

            if link and not link.startswith("http"):
                link = "https://www.stcn.com" + link

            date_str = (article.css("span.time::text, .date::text, time::text").get() or "").strip()
            if date_str and not seen_tracker.is_within_5_days(date_str):
                continue
            if not seen_tracker.is_new(title, link):
                continue

            new_count += 1
            yield NewsItem(
                source="证券时报", title=title, link=link, date=date_str,
            )

        if new_count == 0 and response.meta["page"] > 3:
            self.logger.info("stcn: no new items on page %d, stopping",
                             response.meta["page"])
            return

        self.logger.info("stcn: %d new on page %d", new_count, response.meta["page"])
