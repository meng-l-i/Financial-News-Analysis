import sys
if sys.platform == "win32":
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

BOT_NAME = "crawler"

SPIDER_MODULES = ["crawler.spiders"]
NEWSPIDER_MODULE = "crawler.spiders"

# Playwright — 全局设置（必须在 custom_settings 之前生效）
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}
PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 15000
PLAYWRIGHT_LAUNCH_OPTIONS = {"args": ["--no-sandbox"]}

# 用户代理
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)

# robots.txt
ROBOTSTXT_OBEY = False

# 并发控制
CONCURRENT_REQUESTS = 8
CONCURRENT_REQUESTS_PER_DOMAIN = 2
DOWNLOAD_DELAY = 1.5
RANDOMIZE_DOWNLOAD_DELAY = True

# Cookie
COOKIES_ENABLED = False

# 默认请求头
DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Referer": "https://www.google.com/",
}

# 中间件
DOWNLOADER_MIDDLEWARES = {
    "crawler.middlewares.CrawlerDownloaderMiddleware": 543,
}

# 输出到 stdout（runner 通过 subprocess stdout 截获）
FEED_URI = "stdout:"
FEED_FORMAT = "jsonlines"
ITEM_PIPELINES = {}

# 自动限速
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 2
AUTOTHROTTLE_MAX_DELAY = 10

# 日志
LOG_LEVEL = "INFO"
LOG_FILE = None  # stdout

# 重试
RETRY_ENABLED = True
RETRY_TIMES = 3

# 超时
DOWNLOAD_TIMEOUT = 15
