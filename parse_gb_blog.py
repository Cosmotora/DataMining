import typing
import requests
import time
from datetime import datetime
import bs4
from urllib.parse import urljoin
from database import db


class GbBlogParse:
    def __init__(self, start_url, database: db.Database):
        self.db = database
        self.start_url = start_url
        self.done_urls = set()
        self.tasks = []
        self.comments_url = "https://geekbrains.ru/api/v2/comments"

    def get_task(self, url: str, callback: typing.Callable) -> typing.Callable:
        def task():
            soup = self._get_soup(url)
            return callback(url, soup)

        self.done_urls.add(url)
        return task

    def _get_response(self, url, *args, **kwargs) -> requests.Response:
        for _ in range(15):
            response = requests.get(url, *args, **kwargs)
            if response.status_code in [200, 206]:
                return response
            time.sleep(1)
        raise ValueError("URL DEAD, CODE", response.status_code)

    def _get_soup(self, url, *args, **kwargs) -> bs4.BeautifulSoup:
        soup = bs4.BeautifulSoup(self._get_response(url, *args, **kwargs).text, "lxml")
        return soup

    def _get_comments(self, soup):
        params = {
            "commentable_id": soup.find("comments").attrs.get('commentable-id'),
            "commentable_type": soup.find("comments").attrs.get('commentable-type'),
        }
        comments = self._get_response(self.comments_url, params).json()
        return comments

    def parse_post(self, url, soup):
        author_tag = soup.find("div", attrs={"itemprop": "author"})
        data = {
            "post_data": {
                "id": soup.find("comments").attrs.get('commentable-id'),
                "title": soup.find("h1", attrs={"class": "blogpost-title"}).text,
                "url": url,
                "img": soup.find('img').attrs.get('src', ""),
                "date": datetime.fromisoformat(soup.find("time").attrs.get("datetime")),
            },
            "author_data": {
                "url": urljoin(url, author_tag.parent.attrs.get("href")),
                "name": author_tag.text,
            },
            "tags_data": [
                {"url": urljoin(url, tag_a.attrs.get("href")), "name": tag_a.text}
                for tag_a in soup.find_all("a", attrs={"class": "small"})
            ],
            "comments_data": self._get_comments(soup),
        }

        return data

    def parse_feed(self, url, soup):
        ul = soup.find("ul", attrs={"class": "gb__pagination"})
        pag_urls = set(
            urljoin(url, url_a.attrs.get("href"))
            for url_a in ul.find_all("a")
            if url_a.attrs.get("href")
        )
        for pag_url in pag_urls:
            if pag_url not in self.done_urls:
                task = self.get_task(pag_url, self.parse_feed)
                self.tasks.append(task)

        post_urls = set(
            urljoin(url, url_a.attrs.get("href"))
            for url_a in soup.find_all("a", attrs={"class": "post-item__title"})
            if url_a.attrs.get("href")
        )
        for post_url in post_urls:
            if post_url not in self.done_urls:
                task = self.get_task(post_url, self.parse_post)
                self.tasks.append(task)

    def run(self):
        task = self.get_task(self.start_url, self.parse_feed)
        self.tasks.append(task)
        self.done_urls.add(self.start_url)

        for task in self.tasks:
            task_result = task()
            if task_result:
                self.save(task_result)

    def save(self, data):
        # pass
        self.db.create_post(data)


if __name__ == "__main__":
    database = db.Database("sqlite:///gb_blog.db")
    parser = GbBlogParse("https://gb.ru/posts", database)
    parser.run()
