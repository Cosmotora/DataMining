import os
import dotenv
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from scrapy_junior.spiders.instagram import InstagramSpider

if __name__ == "__main__":
    crawler_settings = Settings()
    crawler_settings.setmodule("scrapy_junior.settings")
    crawler_proc = CrawlerProcess(settings=crawler_settings)
    dotenv.load_dotenv(".env")
    insta_tags = ["miniatureschnauzer", "sansevieria"]
    insta_params = {
        "login": os.getenv("USERNAME"),
        "password": os.getenv("ENC_PASSWORD"),
        "tags": insta_tags,
    }
    crawler_proc.crawl(InstagramSpider, **insta_params)
    crawler_proc.start()
