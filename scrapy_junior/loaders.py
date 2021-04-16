from urllib.parse import urljoin
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, Compose


def get_url(url):
    return urljoin('https://hh.ru/', url)


def get_price(item):
    return item.get('string')

def get_photos(item):
    item['photos'] = item.get('info').get('photos', {}).values()


class AvitoLoader(ItemLoader):
    default_item_class = dict
    url_out = Compose(TakeFirst(), get_url)
    title_out = TakeFirst()
    price_in = get_price
    price_out = TakeFirst()
    address_out = TakeFirst()
    info_in = get_photos
    # info_out = TakeFirst()
    author_out = TakeFirst()
    phone_out = TakeFirst()
