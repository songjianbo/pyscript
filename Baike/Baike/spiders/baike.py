# -*- coding: utf-8 -*-
import scrapy
from Baike.items import BaikeItem


class BaikeSpider(scrapy.Spider):
    name = "baike"
    allowed_domains = ["baike.baidu.com"]
    start_urls = ['https://baike.baidu.com/item/Python']
    count = 0

    def parse(self, response):
        if self.count == 1000:
            return
        item = BaikeItem()
        item['entry'] = response.xpath("//h1").extract()[0]
        item['entryUrl'] = response.url
        item['abstract'] = response.xpath("//div[@class='lemma-summary']").extract()[0]
        yield item

        url_list = response.xpath("//div[@class='lemma-summary']//a/@href").extract()
        for url in url_list:
            yield scrapy.Request("https://baike.baidu.com" + url, callback=self.parse)
        self.count += 1
