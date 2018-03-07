# -*- coding: utf-8 -*-

import scrapy

from closingadvance_scraper.items import BankInfoItem


class BankInfoSpider(scrapy.Spider):
    name = 'bank_info'
    allowed_domains = ['gregthatcher.com']
    start_urls = ['http://www.gregthatcher.com/Bank/Routing/Numbers/']

    def parse(self, response):
        self.logger.info('Crawled (%d) %s' % (response.status, response.url))

        for a in response.xpath('//div[@id="ContentPlaceHolder1_PanelAlphabet"]//a[contains(@id, "ContentPlaceHolder1_Browse")]'):
            yield response.follow(a, self.parse_item)

    def parse_item(self, response):
        self.logger.info('Crawled (%d) %s' % (response.status, response.url))

        for node in response.xpath('//tr[@class="centerIt"][position() > 1]'):
            values = node.xpath('td/text()').extract()
            item = BankInfoItem()
            item['routing_number'] = values[0]
            if values[1].strip() != '':
                item['routing_number'] = values[1]
            item['bank_name'] = values[2]
            item['address'] = values[3]
            item['city'] = values[4]
            item['state'] = values[5]
            item['zip_code'] = values[6]
            item['telephone'] = values[7]
            item['revision_date'] = values[8]
            yield item

