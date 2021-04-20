# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request
import pymongo
from .items import InstaTag, InstaPost


class ScrapyJuniorParsePipeline:
    def process_item(self, item, spider):
        return item


class ScrapyJuniorMongoPipeline:
    def __init__(self):
        client = pymongo.MongoClient()
        self.db = client["scrapy_parse"]

    def process_item(self, item, spider):
        name = 'posts' if isinstance(item, InstaPost) else 'tags'
        self.db[name].insert_one(item)
        return item


class ScrapyJuniorDownloadPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if isinstance(item, InstaPost):
            yield Request(item['data'].get("display_url"))

    def item_completed(self, results, item, info):
        if isinstance(item, InstaPost):
            item["photo"] = results[0][1]
        return item
