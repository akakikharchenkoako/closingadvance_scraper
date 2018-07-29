# -*- coding: utf-8 -*-

from urllib.parse import urljoin

import scrapy
import zipcodes
import re
from closingadvance_scraper.locations import states
from closingadvance_scraper.items import RealtorAgentItem, RealtorBrokerItem
from closingadvance_scraper.loaders import AgentLoader, RealtorBrokerLoader


class BrownBookSpider(scrapy.Spider):
    name = 'brownbook'
    allowed_domains = ['www.brownbook.net']
    start_url = 'http://www.brownbook.net/united-states/categories'

    def start_requests(self):
        for zipcode in zipcodes.filter_by(zipcodes.list_all(), active=True):
            url = self.search_url.format(zipcode['zip_code'])
            yield scrapy.Request(url, callback=self.parse_categories_list_page)

    def parse_categories_list_page(self, response):
        for agent_node in response.xpath('//div[@id="promo_full"]//table//td/a/'):
            yield response.follow(agent_node.xpath('./@data-url').extract_first(), self.parse_agent_profile, meta={'search_keyword': response.meta.get('search_keyword')})

        if response.xpath('//nav[@class="pagination"]/span[@class="next"]/a[@class="next"]/@href').extract_first():
            yield scrapy.Request(response.xpath('//nav[@class="pagination"]/span[@class="next"]'
                                                '/a[@class="next"]/@href').extract_first(),
                                 self.parse, meta={'dont_cache': True, 'search_keyword': response.meta.get('search_keyword')})

