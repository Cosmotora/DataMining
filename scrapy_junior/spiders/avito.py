import scrapy
from scrapy import Request
from time import sleep
from random import randint
import json
from ..loaders import AvitoLoader
from itemadapter import ItemAdapter


class AvitoSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['avito.ru']
    start_urls = ['https://www.avito.ru/krasnodar/kvartiry/prodam-ASgBAgICAUSSA8YQ']

    def __init__(self, **kwargs):
        super(AvitoSpider, self).__init__(**kwargs)
        self.page = 1
        self.url = self.start_urls[0] + f'?p={self.page}'
        self.idx = self.url.index('=') + 1

    def _get_pagination(self, response, *args, **kwargs):
        self.pagination_total = int(response.xpath("//span[contains(@data-marker,'page(')]/"
                                                   "@data-marker").extract()[-1][5:-1])
        while self.page <= self.pagination_total:
            yield response.follow(self.url, callback=self.catalog_parse)
            self.page += 1
            self.url = self.url[:self.idx] + f'{self.page}'

    def _get_follow(self, response, url, callback, **kwargs):
        yield response.follow(url=url, callback=callback, cb_kwargs=kwargs)

    def _get_data(self, response):
        data = json.loads(response.xpath('//div[@class="js-initial"]/@data-state').extract_first())
        return data

    def parse(self, response, **kwargs):
        yield from self._get_pagination(response)

    def catalog_parse(self, response, *args, **kwargs):
        data = self._get_data(response)
        for flat in data['catalog']['items']:
            if flat['type'] == 'item':
                author_url = flat.get('urlPath') + '?showPhoneNumber'
                yield from self._get_follow(response, author_url, callback=self.author_parse, flat=flat)

    def author_parse(self, response, flat, **kwargs):
        author_data = {
            'author': response.xpath('//a[@title="Нажмите, чтобы перейти в профиль"]/@href'),
            # 'phone': response.xpath('//style[contains(text(), .ymaps-2-1-78-panorama-screen"]/text()'),
        }
        yield from self.flat_parse(flat, author_data)

    def flat_parse(self, data, author_data):
        flat = {
            'url': data.get('urlPath'),
            'title': data.get('title'),
            'price': data.get('priceDetailed'),
            'address': data.get('addressDetailed'),
            'info': {
                'description': data.get('description'),
                'photos': data.get('gallery').get('image_large_urls')
            },
            'author': author_data['author'],
            'phone': author_data.get('phone'),
        }
        loader = AvitoLoader()
        for key, value in flat.items():
            loader.add_value(key, value)
        yield loader.load_item()
