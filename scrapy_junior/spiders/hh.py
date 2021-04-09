import scrapy

from ..loaders import HHJobLoader, HHEmployerLoader


class HHSpider(scrapy.Spider):
    name = 'hh'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113']

    _data_query = {
        'type': 'job',
        'title': '//h1[@data-qa=vacancy-serp__vacancy-title]/span/text()',
        'salary': '//p[@class="vacancy-salary]/span[@data-qa="bloko-header-2"]/text()',
        'description': '//div[@data-qa="vacancy-description"]/text()',
        'skills': '//div[contains(@data-qa, skills-element)]',
        'employer': '//div[@class="vacancy-company__details"]/a[@data-qa="vacancy-company-name"]/@href',
    }

    _employer_data = {
        'type': 'employer',
        'title': '//div[@class="employer-sidebar-header"]/'
                 'div/h1[@data-qa="bloko-header-1"]/'
                 'span[@data-qa="company-header-title-name"]/text()',
        'website': '//div[@class="employer-sidebar"]/'
                   'div[@class="employer-sidebar-content"]/'
                   'a[@data-qa="sidebar-company-site"]/@href',
        'business': '//div[@class="employer-sidebar"]/'
                    'div[@class="employer-sidebar-content"]/'
                    'div[@class="employer-sidebar-block"]/p/text()',
    }

    _selectors = {
        "pagination": "//div[@data-qa='pager-block']//a[@data-qa='pager-next']//@href",
        "job": "//div[@class='vacancy-serp-item']//a[@data-qa='vacancy-serp__vacancy-title']/@href",
        "employer_job": '//div[@class="employer-sidebar"]/'
                        'div[@class="employer-sidebar-content"]/'
                        'div[@class="employer-sidebar-block"]/'
                        'a[@data-qa="employer-page__employer-vacancies-link"]/@href',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _get_follow(self, response, selector, callback, **kwargs):
        for link in response.xpath(selector):
            yield response.follow(link, callback=callback, cb_kwargs=kwargs)

    def parse(self, response, *args, **kwargs):
        yield from self._get_follow(
            response, self._selectors["pagination"], self.list_parse,
        )

    def list_parse(self, response, *args, **kwargs):
        yield from self._get_follow(
            response, self._selectors["pagination"], self.list_parse,
        )
        yield from self._get_follow(
            response, self._selectors["job"], self.job_parse,
        )

    def job_parse(self, response, *args, **kwargs):
        HHSpider.load_data(response, HHJobLoader, self._data_query)
        yield from self._get_follow(
            response, self._data_query['employer'], self.employer_parse,
        )

    def employer_parse(self, response, *args, **kwargs):
        HHSpider.load_data(response, HHEmployerLoader, self._employer_data)
        yield from self._get_follow(
            response, self._selectors['employer_job'], self.list_parse,
        )

    @staticmethod
    def load_data(response, loader, query):
        loader = loader(response=response)
        loader.add_value("url", response.url)
        for key, xpath in query.items():
            loader.add_xpath(key, xpath)
        yield loader.load_item()
