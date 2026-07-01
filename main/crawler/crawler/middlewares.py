from scrapy import signals


class CrawlerDownloaderMiddleware:

    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider=None):
        return None

    def process_response(self, request, response, spider=None):
        return response

    def process_exception(self, request, exception, spider=None):
        return None

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s", spider.name)
