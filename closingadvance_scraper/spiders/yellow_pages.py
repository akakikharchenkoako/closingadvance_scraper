# -*- coding: utf-8 -*-

import scrapy
import zipcodes

from closingadvance_scraper.items import CompanyItem
from closingadvance_scraper.loaders import CompanyLoader


class YellowPagesSpider(scrapy.Spider):
    name = 'yellowpages'
    allowed_domains = ['www.yellowpages.com']
    categories = [
        'title-companies', 'escrow-service',
        'real-estate-title-service', 'real-estate-attorneys',
        'real-estate-agents', 'real-estate-buyer-brokers']
    search_url = 'https://www.yellowpages.com/{}-{}/{}'

    custom_settings = {
        'HTTPCACHE_ENABLED': False
    }

    def start_requests(self):
        for zipcode in zipcodes.filter_by(zipcodes.list_all(), active=True):
            for cat in self.categories:
                url = self.search_url.format(zipcode['city'].lower().replace(' ', '-'), zipcode['state'].lower(), cat)
                yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        self.logger.info('Crawled (%d) %s' % (response.status, response.url))

        for a in response.xpath('//h2[@class="n"]/a'):
            yield response.follow(a, self.parse_item)

        for a in response.xpath('//div[@class="pagination"]/ul/li/a'):
            yield response.follow(a, self.parse)

    def parse_item(self, response):
        self.logger.info('Crawled (%d) %s' % (response.status, response.url))

        l = CompanyLoader(item=CompanyItem(), response=response)
        l.add_value('url', response.url)
        l.add_xpath('name', '//div[@class="sales-info"]/h1/text()')
        l.add_xpath('phone', '//p[@class="phone"]/text()')
        l.add_xpath('fax', '//dd[@class="extra-phones"]/p/span[contains(text(), "Fax")]/following-sibling::span/text()')
        l.add_xpath('email', '//a[@class="email-business"]/@href', re=r'mailto:(.+)')
        l.add_xpath('website', '//a[@class="secondary-btn website-link"]/@href')
        l.add_xpath('address', '//p[@class="address"]/span/text()')
        l.add_xpath('categories', '//dd[@class="categories"]/span/a/text()')
        yield l.load_item()

