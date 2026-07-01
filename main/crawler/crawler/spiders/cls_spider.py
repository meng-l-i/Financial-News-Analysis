"""
财联社 (cls.cn) — JS 渲染页面，scrapy-playwright 集成
打开 → 选子频道 → 加载更多 → 抓取
"""
import scrapy
from scrapy_playwright.page import PageMethod
from crawler.items import NewsItem
from crawler.seen import seen_tracker
from crawler.spider_config import spider_url


class ClsSpider(scrapy.Spider):
    name = "cls"
    allowed_domains = ["cls.cn"]
    custom_settings = {"DOWNLOAD_DELAY": 1.5}


    def start_requests(self):
        url = spider_url("cls") or "https://www.cls.cn/telegraph"
        yield scrapy.Request(
            url,
            meta={
                "playwright": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_selector",
                               "#__next div.level-2-nav-box h3:nth-child(3) a"),
                    PageMethod("click",
                               "#__next div.level-2-nav-box h3:nth-child(3) a"),
                    PageMethod("wait_for_load_state", "networkidle"),
                    PageMethod("wait_for_selector",
                               '//*[@id="__next"]/div/div[2]/div[2]/div[1]/div[3]'),
                    PageMethod("click",
                               '//*[@id="__next"]/div/div[2]/div[2]/div[1]/div[3]'),
                   # PageMethod("wait_for_timeout", 3000),
                ],
            },
            callback=self.parse,
        )

    def parse(self, response):
        card_xpath  = '//*[@id="__next"]/div/div[2]/div[2]/div[1]/div[2]/div'
        time_xpath  = './div/div[1]/div/div/span[1]/text()'
        title_xpath = './div/div[1]/div/div/span[2]/text()'
        data_xpath  = './div/div[1]/div/div/span[3]/text()'
        link_xpath  = './div/div[3]/a[1]/@href'
        date_xpath  = '//*[@id="__next"]/div/div[2]/div[2]/div[1]/div[1]/div[1]/div[1]/text()'

        # 页面级日期，如 "2026.06.16 星期二 18:09:35" → 取前10位 "2026.06.16"
        page_date = (response.xpath(date_xpath).get() or "").strip()[:10]
        self.logger.info("page_date=%s", page_date)

        new_count = 0
        seen = set()
        cards = response.xpath(card_xpath)
        self.logger.info("found %d cards", len(cards))
        for card in cards:
            title = (card.xpath(title_xpath).get() or "").strip()
            if not title:
                continue

            time = (card.xpath(time_xpath).get() or "").strip()
            data = (card.xpath(data_xpath).get() or "").strip()
            full_time = f"{page_date.replace('.', '-')} {time}" if page_date and time else time

            link = (card.xpath(link_xpath).get() or "").strip()
            if link and not link.startswith("http"):
                link = response.urljoin(link)

            if not seen_tracker.is_new(title, link):
                continue

            seen.add(f"{title}|{link}")
            new_count += 1
            yield NewsItem(source="财联社", title=title, link=link, data=data, date=full_time)

        self.logger.info("cls: %d new items", new_count)
