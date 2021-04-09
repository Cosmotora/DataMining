from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from scrapy_junior.spiders.hh import HHSpider

if __name__ == "__main__":
    crawler_settings = Settings()
    crawler_settings.setmodule("scrapy_junior.settings")
    crawler_proc = CrawlerProcess(settings=crawler_settings)
    crawler_proc.crawl(HHSpider)
    crawler_proc.start()
