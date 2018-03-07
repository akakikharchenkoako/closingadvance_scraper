# -*- coding: utf-8 -*-

import scrapy
import zipcodes

from closingadvance_scraper.items import AttorneyItem
from closingadvance_scraper.loaders import AttorneyLoader


class AvvoSpider(scrapy.Spider):
    name = 'avvo'
    allowed_domains = ['www.avvo.com']
    search_url = 'https://www.avvo.com/search/lawyer_search?loc={}&q=Real+estate&sort=relevancy'

    custom_settings = {
        'HTTPCACHE_ENABLED': False
    }

    def start_requests(self):
        for zipcode in zipcodes.filter_by(zipcodes.list_all(), active=True):
            url = self.search_url.format(zipcode['zip_code'])
            yield scrapy.Request(url, callback=self.parse, meta={'zip': zipcode['zip_code']})

    def parse(self, response):
        self.logger.info('Crawled (%d) %s' % (response.status, response.url))

        for a in response.xpath('//a[@class="v-serp-block-link"]'):
            yield response.follow(a, self.parse_item, meta={'zip': response.meta['zip']})

        for a in response.xpath('//li[@class="pagination-page"]/span/a'):
            yield response.follow(a, self.parse, meta={'zip': response.meta['zip']})

    def parse_item(self, response):
        self.logger.info('Crawled (%d) %s' % (response.status, response.url))

        l = AttorneyLoader(item=AttorneyItem(), response=response)
        l.add_value('originUrl', response.url)
        l.add_xpath('name', '//span[@itemprop="name"]/text()')
        l.add_xpath('phone', '//span[contains(@class, "lawyer-phone")]/text()')
        address = response.xpath('//div[contains(@class, "header-address")]/text()').extract_first()
        l.add_value('address', ' '.join([address.strip(), str(response.meta['zip'])]))
        l.add_xpath('website', '//a[contains(@onclick, "website")]/@href')
        l.add_xpath('practice_areas', '//a[@href="#practice_areas"]/text()')
        l.add_xpath('licensed_since', '//time[@data-timestamp="years-active"]/text()', re=r'(\d+)')
        profile_picture = response.xpath('//figure/img[@itemprop="image"]/@src').extract_first()
        if profile_picture:
            l.add_value('pictureUrl', 'https:' + profile_picture.strip())
        yield l.load_item()

