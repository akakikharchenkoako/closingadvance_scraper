# -*- coding: utf-8 -*-

import re
import scrapy
import zipcodes

from closingadvance_scraper.items import Century21AgentItem
from closingadvance_scraper.loaders import Century21AgentLoader


class Century21AgentSpider(scrapy.Spider):
    name = 'century21_agent'
    allowed_domains = ['www.century21.com']
    search_url = 'https://www.century21.com/agentsearch-async?lid=C{}{}&t=2&s=0&r=20'

    def start_requests(self):
        for zipcode in zipcodes.list_all():
            url = self.search_url.format(zipcode['state'], zipcode['city'])
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        self.logger.info('Crawled (%d) %s' % (response.status, response.url))

        for a in response.xpath('//div[@class="agent-card-primary-info"]/a'):
            yield response.follow(a, self.parse_item)

        if b'No Results Found' not in response.body:
            index = re.search(r's=(\d+)', response.url).group(1)
            url = re.sub(r's=\d+', 's=' + str(int(index) + 20), response.url)
            yield scrapy.Request(url, self.parse)

    def parse_item(self, response):
        self.logger.info('Crawled (%d) %s' % (response.status, response.url))

        l = Century21AgentLoader(item=Century21AgentItem(), response=response)
        l.add_value('agentUrl', response.url)
        l.add_xpath('agentName', '//div[@id="agentRightLane"]//span[@itemprop="name"]/text()')
        l.add_xpath('agentPhone', '//a[contains(@data-ctc-track, "agent-phone")]/text()')
        l.add_xpath('agentMobile', '//a[contains(@data-ctc-track, "agent-mobile")]/text()')
        l.add_xpath('officeName', '//div[@class="LaneTitle"]/b/text()')
        l.add_xpath('officePhone', '//a[contains(@data-ctc-track, "office-phone")]/text()')
        l.add_xpath('officeAddress', '//div[@class="addressBlock"]/text()')
        yield l.load_item()
