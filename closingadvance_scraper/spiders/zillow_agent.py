# -*- coding: utf-8 -*-

import re
import scrapy
import zipcodes
from urllib.parse import urljoin

from closingadvance_scraper.locations import states
from closingadvance_scraper.items import ZillowAgentItem, ZillowBrokerItem
from closingadvance_scraper.loaders import AgentLoader, BrokerLoader


class ZillowAgentSpider(scrapy.Spider):
    name = 'zillow_agent'
    allowed_domains = ['www.zillow.com']
    most_active_search_url = 'https://www.zillow.com/{}-{}-{}/listing-agent--real-estate-agent-reviews/?service=Selling&propertyType=houses&showAdvancedItems=true&page=1'
    most_sales_search_url = 'https://www.zillow.com/{}-{}-{}/listing-agent--real-estate-agent-reviews/?service=Selling&propertyType=houses&sortBy=sales&showAdvancedItems=true&page=1'
    most_listings_search_url = 'https://www.zillow.com/{}-{}-{}/listing-agent--real-estate-agent-reviews/?service=Selling&propertyType=houses&sortBy=listings&showAdvancedItems=true&page=1'
    # start_urls = ['https://www.zillow.com/profile/JPAssociatesREALTORS/']

    def start_requests(self):
        target_states = [state['abbr'] for state in states]
        for zipcode in zipcodes.filter_by(zipcodes.list_all(), active=True):
            if zipcode['state'] in target_states:
                url = self.most_active_search_url.format('-'.join(zipcode['city'].split()).lower(), zipcode['state'].lower(), zipcode['zip_code'])
                yield scrapy.Request(url, callback=self.parse, meta={'dont_cache': True})
                url = self.most_sales_search_url.format('-'.join(zipcode['city'].split()).lower(), zipcode['state'].lower(), zipcode['zip_code'])
                yield scrapy.Request(url, callback=self.parse, meta={'dont_cache': True})
                url = self.most_listings_search_url.format('-'.join(zipcode['city'].split()).lower(), zipcode['state'].lower(), zipcode['zip_code'])
                yield scrapy.Request(url, callback=self.parse, meta={'dont_cache': True})

    def parse(self, response):
        self.logger.info('Crawled (%d) %s' % (response.status, response.url))

        for a in response.xpath('//p[contains(@class, "ldb-contact-name")]/a'):
            yield response.follow(a, self.parse_agent_profile)

        if response.xpath('//a[@class="js-pagination"][text()="Next"]').extract_first():
            index = re.search(r'page=(\d+)', response.url).group(1)
            next_url = re.sub(r'page=\d+', 'page=' + str(int(index) + 1), response.url)
            yield scrapy.Request(next_url, self.parse, meta={'dont_cache': True})

    def parse_agent_profile(self, response):
        self.logger.info('Crawled (%d) %s' % (response.status, response.url))

        for href in response.xpath('//div[@class="ptm-team-members"]//a/@href').extract():
            url = urljoin(response.url, href)
            yield scrapy.Request(url, self.parse_agent_profile, meta={'brokerUrl': response.url})

        title = response.xpath('//p[@id="profile-title"]/strong/text()').extract_first()
        if not title:
            title = response.xpath('//span[@class="license-desc"]/text()').re_first(r'\((.*?)\)')
        title = title.strip() if title else None
        if title and 'broker' in title.lower():
            l = BrokerLoader(item=ZillowBrokerItem(), response=response)
            l.add_value('originUrl', response.url)
            l.add_value('brokerTitle', title)
            state = response.xpath('//li[@id="region-state"]/a/text()').extract_first()
            city = response.xpath('//li[@id="region-city"]/a/text()').extract_first()
            try:
                l.add_value('location', city.strip() + ', ' + state.strip())
            except AttributeError:
                return
            l.add_xpath('brokerName', '//span[@class="ctcd-user-name"]/text()')
            l.add_xpath('brokerMobile', '//dt[contains(text(), "Phone:")]/following-sibling::dd/text()')
            l.add_xpath('officeName', '//dd[contains(@class, "profile-information-address")]/text()')
            l.add_xpath('officePhone', '//dt[contains(text(), "Brokerage:")]/following-sibling::dd/text()')
            if not l.get_output_value('officePhone'):
                l.add_xpath('officePhone', '//dt[contains(text(), "Phone:")]/following-sibling::dd/text()')
            street = response.xpath('//span[@class="street-address"]/text()').extract_first()
            street = street.strip() if street else ''
            locality = response.xpath('//span[@class="locality"]/text()').extract_first()
            locality = locality.strip() if locality else ''
            region = response.xpath('//span[@class="region"]/text()').extract_first()
            region = region.strip() if region else ''
            postal = response.xpath('//span[@class="postal-code"]/text()').re_first(r'\s(\d+)')
            postal = postal.strip() if postal else ''
            l.add_value('officeAddress', ', '.join([street, locality, region, postal]))
            yield l.load_item()
        else:
            l = AgentLoader(item=ZillowAgentItem(), response=response)
            l.add_value('originUrl', response.url)
            l.add_value('brokerUrl', response.meta.get('brokerUrl'))
            l.add_value('designation', title)
            state = response.xpath('//li[@id="region-state"]/a/text()').extract_first()
            city = response.xpath('//li[@id="region-city"]/a/text()').extract_first()
            try:
                l.add_value('location', city.strip() + ', ' + state.strip())
            except AttributeError:
                return
            l.add_xpath('agentName', '//span[@class="ctcd-user-name"]/text()')
            l.add_xpath('agentMobile', '//dt[contains(text(), "Phone:")]/following-sibling::dd/text()')
            l.add_xpath('officeName', '//dd[contains(@class, "profile-information-address")]/text()')
            l.add_xpath('officePhone', '//dt[contains(text(), "Brokerage:")]/following-sibling::dd/text()')
            if not l.get_output_value('officePhone'):
                l.add_xpath('officePhone', '//dt[contains(text(), "Phone:")]/following-sibling::dd/text()')
            street = response.xpath('//span[@class="street-address"]/text()').extract_first()
            street = street.strip() if street else ''
            locality = response.xpath('//span[@class="locality"]/text()').extract_first()
            locality = locality.strip() if locality else ''
            region = response.xpath('//span[@class="region"]/text()').extract_first()
            region = region.strip() if region else ''
            postal = response.xpath('//span[@class="postal-code"]/text()').re_first(r'\s(\d+)')
            postal = postal.strip() if postal else ''
            l.add_value('officeAddress', ', '.join([street, locality, region, postal]))
            l.add_xpath('activeListings', '//h2[@id="profile-active-listings"]/following-sibling::span/text()', re=r'(\d+)')
            l.add_xpath('salesLast12Months', '//li[contains(@class, "ctcd-item_sales")]/text()', re=r'(\d+) Sale')
            yield l.load_item()

