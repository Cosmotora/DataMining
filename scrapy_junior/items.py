# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapyJuniorItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class Insta(scrapy.Item):
    _id = scrapy.Field()
    following = scrapy.Field()
    followed_by = scrapy.Field()


class InstaUser(Insta):
    pass


class InstaFriend2(Insta):
    pass
