import scrapy
import re
from scrapy.selector import Selector
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from appstore.items import AppstoreItem


class HuaweiSpider(scrapy.Spider):
    name = "huawei"
    allowed_domains = ["huawei.com"]

    start_urls = [
        "http://appstore.huawei.com/more/all/1",
        # "http://appstore.huawei.com/more/recommend/1",
        # "http://appstore.huawei.com/more/soft/1",
        # "http://appstore.huawei.com/more/game/1",
        # "http://appstore.huawei.com/more/newPo/1",
        # "http://appstore.huawei.com/more/newUp/1",
        # "http://appstore.huawei.com/search/0/1",
        # "http://appstore.huawei.com/search/1/1",
        # "http://appstore.huawei.com/search/2/1",
        # "http://appstore.huawei.com/search/3/1",
        # "http://appstore.huawei.com/search/4/1",
        # "http://appstore.huawei.com/search/5/1",
        # "http://appstore.huawei.com/search/6/1",
        # "http://appstore.huawei.com/search/7/1",
        # "http://appstore.huawei.com/search/8/1",
        # "http://appstore.huawei.com/search/9/1",
        # "http://appstore.huawei.com/search/%25E5%25BA%2594%25E7%2594%25A8/1",
        # "http://appstore.huawei.com/search/%25E6%25B8%25B8%25E6%2588%258F/1",
        # "http://appstore.huawei.com/search/%25E6%2589%2580%25E6%259C%2589/1",
        # "http://appstore.huawei.com/search/%25E8%25BD%25AF%25E4%25BB%25B6/1",
    ]
    rules = (
        Rule(
            LinkExtractor(allow=r'all\/[1-2]'), callback='parse', follow=True)
    )

    def find_next_page(self, url):
        try:
            page_num_str = url.split('/')[-1]
            page_num = int(page_num_str) + 1
            url = url[:-len(page_num_str)] + str(page_num)
            return url
        except ValueError:
            print "### page cannot be handled: ",
            print url
            return "http://google.com"

    def parse(self, response):
        page = Selector(response)

        hrefs = page.xpath('//h4[@class="title"]/a/@href')

        for href in hrefs:
            url = href.extract()
            yield scrapy.Request(url, self.parse_item, meta={
                'splash': {
                    'endpoint': 'render.html',
                    'args': {'wait': 0.5}
                }
            })

    def parse_item(self, response):
        page = Selector(response)
        item = AppstoreItem()

        item['title'] = page.xpath(
            '//ul[@class="app-info-ul nofloat"]/li/p/span[@class="title"]/text()').extract_first().encode('utf-8')
        item['url'] = response.url
        item['appid'] = re.match(r'http://.*/(.*)', item['url']).group(1)
        item['intro'] = page.xpath(
            '//meta[@name="description"]/@content').extract_first().encode('utf-8')

        divs = page.xpath('//div[@class="open-info"]')
        recomm = ""
        for div in divs:
            url = div.xpath('./p[@class="name"]/a/@href').extract_first()
            recommended_appid = re.match(r'http://.*/(.*)', url).group(1)
            name = div.xpath(
                './p[@class="name"]/a/text()').extract_first().encode('utf-8')
            recomm += "{0}: {1},".format(recommended_appid, name)
        item['recommended'] = recomm
        yield item
