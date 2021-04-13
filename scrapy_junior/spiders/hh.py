import scrapy

from ..loaders import HHJobLoader, HHEmployerLoader


def get_link(response):
    employer_id = response.url.split('/')[-1]
    try:
        employer_id = employer_id[:employer_id.index('?')]
    except ValueError:
        pass
    link = 'https://spb.hh.ru/search/' \
           f'vacancy?st=searchVacancy&from=employerPage&employer_id={employer_id}'
    return link


class HHSpider(scrapy.Spider):
    name = 'hh'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113']

    _job_data_query = {
        'title': '//div[@class="vacancy-title"]//h1/child::text()',
        'salary': '//p[contains(@class, "vacancy-salary")]//child::text()',
        'description': '//div[@data-qa="vacancy-description"]//child::text()',
        'skills': '//div[@class="bloko-tag-list"]/div//span/text()',
        'employer': '//div[@class="vacancy-company__details"]/a[@data-qa="vacancy-company-name"]/@href',
    }

    _employer_data_query = {
        'title': '//div[@class="employer-sidebar-header"]/'
                 'div/h1[@data-qa="bloko-header-1"]/'
                 'span[@data-qa="company-header-title-name"]/text()',
        'website': '//div[@class="employer-sidebar"]/'
                   'div[@class="employer-sidebar-content"]/'
                   'a[@data-qa="sidebar-company-site"]/@href',
        'business': '//div[@class="employer-sidebar"]/'
                    'div[@class="employer-sidebar-content"]/'
                    'div[@class="employer-sidebar-block"]/p/text()',
        'description': '//div[@data-qa="company-description-text"]//child::text()'
    }

    _custom_employer_data_query = {
        'title': '//h3[contains(@class, "b-employerpage-vacancies-title")]/text()',
    }

    _selectors = {
        "pagination": "//div[@data-qa='pager-block']//a[@data-qa='pager-next']//@href",
        "job": "//div[@class='vacancy-serp-item']//a[@data-qa='vacancy-serp__vacancy-title']/@href",
        "employer": '//a[contains(@data-qa, "vacancy-employer")]/@href',
        "employer_job": '//a[@data-qa="employer-page__employer-vacancies-link"]/@href',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _get_follow(self, response, selector, callback, custom=False, **kwargs):
        if not custom:
            for link in response.xpath(selector):
                yield response.follow(link, callback=callback, cb_kwargs=kwargs)
        else:
            yield response.follow(get_link(response), callback=callback, cb_kwargs=kwargs)

    def parse(self, response, *args, **kwargs):
        callbacks = {'pagination': self.parse,
                     'job': self.job_parse,
                     'employer': self.employer_parse}
        for key, xpath in self._selectors.items():
            if key == 'employer_job':
                continue
            yield from self._get_follow(
                response, self._selectors[key], callbacks[key]
            )

    def job_parse(self, response, *args, **kwargs):
        yield HHSpider.load_data(response, HHJobLoader, self._job_data_query)

    def employer_parse(self, response, *args, **kwargs):
        if response.xpath(self._selectors['employer_job']):
            yield HHSpider.load_data(response, HHEmployerLoader, self._employer_data_query)
            yield from self._get_follow(
                response, self._selectors['employer_job'], self.parse
            )
        else:
            yield HHSpider.load_data(response, HHEmployerLoader, self._custom_employer_data_query)
            yield from self._get_follow(
                response, None, self.parse, custom=True
            )

    @staticmethod
    def load_data(response, loader, query):
        loader = loader(response=response)
        loader.add_value("url", response.url)
        for key, xpath in query.items():
            loader.add_xpath(key, xpath)
        return loader.load_item()
