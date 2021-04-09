import re
from scrapy.loader import ItemLoader
from scrapy import Selector
from itemloaders.processors import TakeFirst, MapCompose


def clear_price(salary: str) -> float:
    try:
        result = float(salary.replace("\u2009", ""))
    except ValueError:
        result = None
    return result


def get_characteristics(item: str) -> dict:
    selector = Selector(text=item)
    data = [selector.xpath("//span[@data-qa='bloko-tag__text']/text()").extract_first()]
    return data


class HHJobLoader(ItemLoader):
    default_item_class = dict
    type_out = TakeFirst()
    url_out = TakeFirst()
    title_out = TakeFirst()
    salary_out = TakeFirst()
    skills_in = MapCompose(get_characteristics)
    description_out = TakeFirst()
    employer_out = TakeFirst()


class HHEmployerLoader(ItemLoader):
    pass
