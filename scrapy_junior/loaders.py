from urllib.parse import urljoin
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, Compose, MapCompose


def get_url(url):
    return urljoin('https://avito.ru/', url)


def get_price(item):
    return float(item.get('string', 'NaN').replace(' ', ''))


def get_photos(item):
    item['photos'] = item.get('photos', {}).values()
    return item


class AvitoLoader(ItemLoader):
    default_item_class = dict
    url_out = Compose(TakeFirst(), get_url)
    title_out = TakeFirst()
    price_in = Compose(TakeFirst(), get_price)
    address_out = TakeFirst()
    info_in = MapCompose(get_photos)
    info_out = TakeFirst()
    author_out = TakeFirst()
    phone_out = TakeFirst()
