# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import scrapy
from scrapy.pipelines.images import ImagesPipeline
import os
from settings import IMAGES_STORE


class DouyuPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        imagelink = item['imagelink']
        yield scrapy.Request(imagelink)

    def item_completed(self, results, item, info):
        image_path = [x['path'] for ok, x in results if ok]
        old_path = os.path.join(IMAGES_STORE, image_path[0])
        new_path = os.path.join(IMAGES_STORE, item['nickname'] + ".jpg")
        if os.path.exists(old_path):
            os.rename(old_path, new_path)
        return item
