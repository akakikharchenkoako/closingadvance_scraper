# -*- coding: utf-8 -*-

import scrapy
import zipcodes

from closingadvance_scraper.items import HomeClosingItem
from closingadvance_scraper.loaders import CompanyLoader


class Homeclosing101Spider(scrapy.Spider):
    name = 'homeclosing101'
    allowed_domains = ['www.homeclosing101.org']
    search_url = 'http://www.homeclosing101.org/list/?stateCode={}&cities=List+Cities'

    def start_requests(self):
        for zipcode in zipcodes.list_all():
            url = self.search_url.format(zipcode['state'])
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        self.logger.info('Crawled (%d) %s' % (response.status, response.url))

        for a in response.xpath('//div[@id="contact-page"]//div[@class="columns"]/a'):
            yield response.follow(a, self.parse_search_result)

    def parse_search_result(self, response):
        self.logger.info('Crawled (%d) %s' % (response.status, response.url))

        for a in response.xpath('//table[@class="search_results"]//a'):
            yield response.follow(a, self.parse_item)

    def parse_item(self, response):
        self.logger.info('Crawled (%d) %s' % (response.status, response.url))

        l = CompanyLoader(item=HomeClosingItem(), response=response)
        l.add_value('url', response.url)
        l.add_xpath('name', '//h1[@class="title"]/text()')
        l.add_xpath('phone', '//div[@class="member_profile"]/text()', re=r'Phone: ([0-9-]+)')
        l.add_xpath('fax', '//div[@class="member_profile"]/text()', re=r'Fax: ([0-9-]+)')
        chunks = response.xpath('//div[@class="member_profile"]/text()').extract()
        parts = []
        for part in chunks:
            if 'Phone' in part:
                break
            parts.append(part.strip())
        l.add_value('address', ', '.join(parts))
        l.add_xpath('email', '//div[@class="member_profile"]/a[contains(@href, "mailto")]/text()')
        l.add_xpath('website', '//div[@class="member_profile"]/a[contains(@href, "http")]/text()')
        yield l.load_item()

