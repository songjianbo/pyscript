# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BaikeItem(scrapy.Item):
    # define the fields for your item here like:
    # 百科词条
    entry = scrapy.Field()
    # 词条地址
    entryUrl = scrapy.Field()
    # 词条摘要
    abstract = scrapy.Field()
