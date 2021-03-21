import requests
from pathlib import Path
import json
import time


class Parse5ka:
    params = {
        "records_per_page": 20,
    }

    def __init__(self, start_url: str, cat_url: str, result_path: Path):
        self.start_url = start_url
        self.result_path = result_path
        self.cat_url = cat_url

    def _get_response(self, url, *args, **kwargs) -> requests.Response:
        while True:
            response = requests.get(url, *args, **kwargs)
            if response.status_code == 200:
                return response
            time.sleep(1)

    def run(self):
        for category in self._parse(self.cat_url, self.start_url):
            self._save(category)

    def _get_categories(self, url):
        categories = []
        for parent_cat in self._get_response(url).json():
            cat_url = url + parent_cat['parent_group_code']
            categories.extend(self._get_response(cat_url).json())
        return categories

    def _parse(self, cat_url, start_url):
        for cat_info in self._get_categories(cat_url):
            self.params['categories'] = cat_info['group_code']
            category = cat_info
            category['products'] = []
            url = start_url
            while url:
                response = self._get_response(url, params=self.params)
                data = response.json()
                url = data.get("next")
                category['products'].extend(data.get("results", []))
            yield category

    def _save(self, data):
        file_path = self.result_path.joinpath(f'{data["group_code"]}.json')
        file_path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')


if __name__ == "__main__":
    file_path = Path(__file__).parent.joinpath("products")
    if not file_path.exists():
        file_path.mkdir()
    parser = Parse5ka(start_url="https://5ka.ru/api/v2/special_offers/", cat_url="https://5ka.ru/api/v2/categories/",
                      result_path=file_path)
    parser.run()
