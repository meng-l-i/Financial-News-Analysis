import scrapy


class NewsItem(scrapy.Item):
    """新闻条目"""
    source = scrapy.Field()   # 来源
    title = scrapy.Field()    # 标题
    link = scrapy.Field()     # 链接
    data = scrapy.Field()     # 正文
    date = scrapy.Field()     # 时间
