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
    handle_httpstatus_list = [403]

    def __init__(self):
        super(AvitoSpider, self).__init__(*args, **kwargs)
        self.page = 1
        self.url = self.start_urls[0] + f'?p={page}'
        self.idx = self.url.index('=') + 1
        self._template = {

        }

    def _availibility_check(self, response):
        c = 0
        while response.status in self.handle_httpstatus_list:
            c += 1
            if c > 5:
                scrapy.Spider.close(AvitoSpider, '403')
            sleep(randint(60, 65))
            response = Request(response.url, callback=self.parse)
        return True

    def _get_follow(self, response, *args, **kwargs):
        self.pagination_total = int(response.xpath("//span[contains(@data-marker,'page(')]/"
                                                   "@data-marker").extract()[-1][5:-1])
        while self.page <= self.pagination_total:
            yield response.follow(self.url, callback=self.catalog_parse)
            self.page += 1
            self.url = self.url[:self.idx] + f'{self.page}'

    def _get_data(self, response):
        data = json.loads(response.xpath('//div[@class="js-initial"]/@data-state').extract_first())
        return data

    def parse(self, response):
        if self._availibility_check(response):
            yield from self._get_follow(response)

    def catalog_parse(self, response, *args, **kwargs):
        data = self._get_data(response)
        for flat in data['catalog']['items']:
            if flat['type'] == 'item':
                yield self.flat_parse(flat)

    def flat_parse(self, data):
        flat = {}
        for key, func in self._template.items():
            flat[key] = func(data)
        loader = AvitoLoader(item=ItemAdapter(flat))
        yield loader.load_item()
