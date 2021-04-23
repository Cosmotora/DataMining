import json
from urllib.parse import urlencode
import scrapy


# from ..items import InstaTag, InstaPost


class InstagramSpider(scrapy.Spider):
    name = "instagram"
    allowed_domains = ["www.instagram.com"]
    start_urls = ["https://www.instagram.com/"]
    _login_url = "https://www.instagram.com/accounts/login/ajax/"
    api_url = "https://www.instagram.com/graphql/query/"

    def __init__(self, login, password, users, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.login = login
        self.password = password
        self.user1 = users['user1']
        self.user2 = users['user2']

    def parse(self, response):
        try:
            js_data = self.js_data_extract(response)
            yield scrapy.FormRequest(
                self._login_url,
                method="POST",
                callback=self.parse,
                formdata={"username": self.login, "enc_password": self.password, },
                headers={"X-CSRFToken": js_data["config"]["csrf_token"]},
            )
        except AttributeError as e:
            # if response.json()["authenticated"]:
            yield response.follow(f"{self.start_urls[0]}{self.user1}/", callback=self.user_parse)

    def user_parse(self, response):
        js_data = self.js_data_extract(response)
        insta_user = IUser(js_data["entry_data"]["ProfilePage"][0]["graphql"]["user"])
        if insta_user.user['username'] == self.user2:
            pass

        else:
            next_request = self.get_followers(insta_user)
            yield from next_request

    def _api_user_parse(self, response):
        data = response.json()
        insta_user = IUser(data["data"]["user"])
        flag = response.meta['flag']
        item = response.meta['item']
        item['follow'] = item['follow'].extend(response.json()['data']['user'][f"edge_{flag}"]['edges'])
        if insta_user.user[f'edge_{flag}']['page_info']['has_next_page']:
            insta_user.variables['after'] = insta_user.user[f'edge_{flag}']['page_info']['end_cursor']
            yield response.follow(
                f"{self.api_url}?{urlencode(insta_user.paginate_params(flag))}",
                callback=self._api_user_parse,
            )

    def get_followers(self, insta_user):
        item = insta_user.get_user_item()
        for flag in ['follow', 'followed_by']:
            request = scrapy.Request(
                f"{self.api_url}?{urlencode(insta_user.paginate_params(flag))}",
                callback=self._api_user_parse, priority=1
            )
            request.meta['item'] = item
            request.meta['flag'] = flag
            request.meta['user'] = insta_user
            request.meta['depth'] = item['depth']
            yield request
            yield self.get_mutual_followers(item)

    def get_mutual_followers(self, item):
        followers = item["followed_by"]["edges"]
        following = item['follow']["edges"]
        mutual = []
        for item1 in following:
            if item1 in followers:
                mutual.append(item1)
        item['mutual'] = mutual
        return item

    def js_data_extract(self, response):
        script = response.xpath(
            "//script[contains(text(), 'window._sharedData = ')]/text()"
        ).extract_first()
        return json.loads(script.replace("window._sharedData = ", "")[:-1])


class IUser:
    query_hash = {'follow': "3dec7e2c57367ef3da3d987d89f9dbc8",
                  'followed_by': '5aefa9893005572d237da5068082d8d5'}

    def __init__(self, user: dict):
        self.variables = {
            "id": user["id"],
            "include_reel": 'true',
            "fetch_mutual": 'false',
            "first": 24,
        }

        self.user = user
        # self.level = level
        # self.parent = parent

    def paginate_params(self, flag: str):
        url_query = {"query_hash": self.query_hash[flag], "variables": json.dumps(self.variables)}
        return url_query

    def get_user_item(self):
        item = {
            'user': self.user,
            'follow': [],
            'followed_by': [],
            'depth': 0
        }
        return item
