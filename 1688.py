import scrapy
import json
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner, CrawlerProcess
import os
from multiprocessing import Process, Queue
import re


class SourceSpider(scrapy.Spider):
    PATH = 'Results/'
    name = 'source'
    headers = {
        "authority": "search.1688.com",
        "sec-ch-ua": "\"Google Chrome\";v=\"89\", \"Chromium\";v=\"89\", \";Not A Brand\";v=\"99\"",
        "sec-ch-ua-mobile": "?0",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
        "accept": "*/*",
        "origin": "https://s.1688.com",
        "sec-fetch-site": "same-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://s.1688.com/",
        "accept-language": "en-US,en;q=0.9"
    }

    custom_settings = {'FEEDS': {PATH + 'results.json': {'format': 'json'}}}
    try:
        os.remove(PATH + 'results.json')
    except OSError:
        pass

    def parse(self, response):
        data = json.loads(response.body)
        max_page = min(int(data['data']['data']['pageCount']), 2)  # Is it relevant to scrape all pages?
        companies = []
        url = [re.sub(r'(?<=beginPage=)\d+', str(page), response.url) for page in range(1, max_page + 1)]
        companies = yield from response.follow_all(url,
                                                   callback=self.parse_supplier)

    def parse_supplier(self, response):
        data = json.loads(response.body)
        return data['data']['data']["companyWithOfferLists"]


def run_spider(spider, url):
    q = Queue()
    p = Process(target=f, args=(q, spider, url))
    p.start()
    result = q.get()
    p.join()

    if result is not None:
        raise result


def f(q, spider, url):
    try:
        runner = CrawlerProcess()
        deferred = runner.crawl(spider, start_urls=url)
        deferred.addBoth(lambda _: reactor.stop())
        reactor.run()
        q.put(None)
    except Exception as e:
        q.put(e)


if __name__ == '__main__':
    start_urls = [
        'https://search.1688.com/service/companySearchBusinessService?keywords=BMI%B2%E2%C1%BF&spm=a26352%2C15231885&async=true&asyncCount=20&beginPage=1&pageSize=20&requestId=DAfQG4WFYbwRppamixXyG6p2KSYDN5pjr6dKAhrejYscJkYd&sessionId=13d635a16b844cbb8b8acd6fc2262f4a&startIndex=0&pageName=supplier&_bx-v=1.1.20']
    run_spider(SourceSpider, start_urls)