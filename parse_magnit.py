import time
from datetime import datetime
import requests
from urllib.parse import urljoin
import bs4
import pymongo


class MagnitParse:
    def __init__(self, start_url, mongo_url):
        self.start_url = start_url
        client = pymongo.MongoClient(mongo_url)
        self.db = client["promo_parse"]

    def get_response(self, url, *args, **kwargs):
        for _ in range(15):
            response = requests.get(url, *args, **kwargs)
            if response.status_code == 200:
                return response
            time.sleep(1)
        raise ValueError("URL DEAD")

    def get_soup(self, url, *args, **kwargs) -> bs4.BeautifulSoup:
        soup = bs4.BeautifulSoup(self.get_response(url, *args, **kwargs).text, "lxml")
        return soup

    @property
    def template(self):
        def _make_price(txt: str) -> float:
            txt = txt.strip()
            assert not txt.endswith('%'), 'Не цена'
            price = '.'.join(txt.split())
            price = float(price)
            return price

        def _make_date(txt: str, date_from: bool) -> datetime:
            txt = txt.strip().split()
            date_map = {'янв': '01', 'фев': '02', 'мар': '03', 'апр': '04', 'мая': '05', 'июн': '06',
                        'июл': '07', 'авг': '08', 'сен': '09', 'окт': '10', 'ноя': '11', 'дек': '12'}
            if len(txt) < 5:
                date_from = True
            i = 1 if date_from else 4
            date_str = txt[i] + ' ' + date_map.get(txt[i + 1][:3], '{0:0>2}'.format(datetime.now().month))
            date = datetime.strptime(date_str, '%d %m').replace(year=datetime.now().year)
            return date

        data_template = {
            "url": lambda a: urljoin(self.start_url, a.attrs.get("href", "/")),
            "promo_name": lambda a: a.find("div", attrs={"class": "card-sale__header"}).text,
            "product_name": lambda a: a.find("div", attrs={"class": "card-sale__title"}).text,
            "old_price": lambda a: _make_price(a.find("div", attrs={"class": "label__price_old"}).text),
            "new_price": lambda a: _make_price(a.find("div", attrs={"class": "label__price_new"}).text),
            "image_url": lambda a: urljoin(self.start_url,
                                           a.find("picture").find("img").attrs.get("data-src", "/")),
            "date_from": lambda a: _make_date(a.find("div", attrs={"class": "card-sale__date"}).text,
                                              date_from=True),
            "date_to": lambda a: _make_date(a.find("div", attrs={"class": "card-sale__date"}).text,
                                            date_from=False),
        }
        return data_template

    def run(self):
        for product in self._parse(self.get_soup(self.start_url)):
            self.save(product)

    def _parse(self, soup):
        products_a = soup.find_all("a", attrs={"class": "card-sale"})
        for prod_tag in products_a:
            is_banner = "card-sale_banner" in prod_tag.get("class")
            if is_banner:
                continue
            is_product = True
            product_data = {}
            for key, func in self.template.items():
                try:
                    product_data[key] = func(prod_tag)
                except (AssertionError, AttributeError):
                    pass
                if product_data.get('promo_name', '') in ['Скидка пенсионерам', 'Скидка на категорию']:
                    is_product = False
                    break
            if is_product:
                yield product_data

    def save(self, data):
        collection = self.db["magnit"]
        collection.insert_one(data)


if __name__ == "__main__":
    url = "https://magnit.ru/promo/"
    mongo_url = "mongodb://localhost:27017"
    parser = MagnitParse(url, mongo_url)
    parser.run()
