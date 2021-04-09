from urllib.parse import urljoin
from scrapy.loader import ItemLoader
from scrapy import Selector
from itemloaders.processors import TakeFirst, MapCompose, Compose


def salary_to_text(items):
    return ' '.join(items)


def description_to_text(items):
    return '\n'.join(items).replace('\n:', ':').replace('\n,', ',')


def get_employer(url):
    return urljoin('https://hh.ru/', url)


class HHLoader(ItemLoader):
    default_item_class = dict
    url_out = TakeFirst()
    title_in = salary_to_text
    title_out = TakeFirst()
    salary_in = salary_to_text
    salary_out = TakeFirst()
    description_in = description_to_text
    description_out = TakeFirst()
    employer_in = Compose(TakeFirst(), get_employer)
    employer_out = TakeFirst()
    company_title_out = TakeFirst()
    website_out = TakeFirst()
    business_out = TakeFirst()
