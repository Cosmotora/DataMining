import scrapy

from ..loaders import HHLoader


class HHSpider(scrapy.Spider):
    name = 'hh'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113']

    _data_query = {
        'title': '//div[@class="vacancy-title"]//child::text()',
        'salary': '//p[contains(@class, "vacancy-salary")]//child::text()',
        'description': '//div[@class="vacancy-description"]//child::text()',
        'skills': '//div[@class="bloko-tag-list"]/div//span/text()',
        'employer': '//div[@class="vacancy-company__details"]/a[@data-qa="vacancy-company-name"]/@href',
        'company_title': '//div[@class="employer-sidebar-header"]/'
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
        yield from self._get_follow(
            response, self._data_query['employer'], self.employer_parse,
        )
        yield from self.load_data(response)

    def employer_parse(self, response, *args, **kwargs):
        yield from self.load_data(response)
        yield from self._get_follow(
            response, self._selectors['employer_job'], self.list_parse,
        )

    def load_data(self, response):
        loader = HHLoader(response=response)
        loader.add_value("url", response.url)
        for key, xpath in self._data_query.items():
            loader.add_xpath(key, xpath)
        yield loader.load_item()

    def data_loader(self, response):
        pass
