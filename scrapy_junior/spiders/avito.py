import scrapy


class AvitoSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['avito.ru']
    start_urls = ['https://www.avito.ru/krasnodar/kvartiry/prodam']

    _selectors = {
        "pagination": "//span[@data-marker='pagination-button/next']",

    }

    _data_query = {

    }

    def _get_follow(self, response, selector, callback, *args, **kwargs):
        for link in response.xpath(selector):
            yield response.follow(link, callback=callback, cb_kwargs=kwargs)

    def parse(self, response):
        callbacks = {
            "pagination": self.parse,
        }
        for key, xpath in self._selectors:
            yield self._get_follow(response, xpath, callbacks[key])

    def flat_parse(self, response, *args, **kwargs):
        pass
