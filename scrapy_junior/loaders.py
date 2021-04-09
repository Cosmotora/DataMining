from urllib.parse import urljoin
from scrapy.loader import ItemLoader
from scrapy import Selector
from itemloaders.processors import TakeFirst, MapCompose


def clear_salary(salary: str) -> float:
    try:
        salary = salary.split()[1]
        result = float(salary.replace("\xa0", ""))
    except ValueError:
        result = None
    return result


def get_description(item: str):
    selector = Selector(text=item)
    data = {
        'experience': selector.xpath('//span[@data-qa="vacancy-experience"]/text()').extract_first(),
        'requirements': selector.xpath('//div[@data-qa="vacancy-description"]//span/text()')
    }
    return data


def get_skills(item: str) -> list:
    selector = Selector(text=item)
    data = selector.xpath("//span[@data-qa='bloko-tag__text']/text()").extract()
    return data


def get_employer(text):
    result = f'https://hh.ru{text}'
    return result


class HHJobLoader(ItemLoader):
    default_item_class = dict
    type_out = TakeFirst()
    url_out = TakeFirst()
    title_out = TakeFirst()
    salary_in = MapCompose(clear_salary)
    salary_out = TakeFirst()
    skills_in = MapCompose(get_skills)
    description_in = MapCompose(get_description)
    employer_in = MapCompose(get_employer)
    employer_out = TakeFirst()


class HHEmployerLoader(ItemLoader):
    pass
