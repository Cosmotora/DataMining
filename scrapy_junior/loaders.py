from urllib.parse import urljoin
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, Compose


def clean_text_items(items):
    items = [i.strip().replace('\xa0', '') for i in items if i.strip()]
    return items


def to_plain_text(items):
    items = clean_text_items(items)
    return ' '.join(items).strip()


def description_to_text(items):
    return '\n'.join(clean_text_items(items))


def get_employer(url):
    return urljoin('https://hh.ru/', url)


class HHDefaultLoader(ItemLoader):
    default_item_class = dict
    url_out = TakeFirst()
    title_in = to_plain_text
    title_out = TakeFirst()
    description_in = description_to_text
    description_out = TakeFirst()


class HHJobLoader(HHDefaultLoader):
    salary_in = to_plain_text
    salary_out = TakeFirst()
    employer_in = Compose(TakeFirst(), get_employer)
    employer_out = TakeFirst()


class HHEmployerLoader(HHDefaultLoader):
    website_out = TakeFirst()
    business_out = TakeFirst()
