# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class BaikePipeline(object):
    def __init__(self):
        self.f = open('output.html', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        if spider.count == 0:
            self.f.write("<html>")
            self.f.write("<body>")
            self.f.write("<table>")
        self.f.write("<tr>")
        self.f.write("<td>%s</td>" % item['entryUrl'])
        self.f.write("<td>%s</td>" % item['entry'])
        self.f.write("<td>%s</td>" % item['abstract'])
        self.f.write("</tr>")
        if spider.count == 1000:
            self.f.write("</html>")
            self.f.write("</body>")
            self.f.write("</table>")
        return item

    def close_spider(self, spider):
        self.f.close()
