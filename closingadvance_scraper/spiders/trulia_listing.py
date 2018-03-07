# -*- coding: utf-8 -*-

import re
import json
import scrapy
import zipcodes

from closingadvance_scraper.locations import states
from closingadvance_scraper.items import TruliaListingItem
from closingadvance_scraper.loaders import ListingLoader
from closingadvance_scraper.processors import serialize_number, serialize_name


class TruliaListingSpider(scrapy.Spider):
    name = 'trulia_listing'
    custom_settings = {
        'CONCURRENT_REQUESTS': 16,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 16
    }
    allowed_domains = ['www.trulia.com']
    search_url = 'https://www.trulia.com/for_sale/{}_zip/3p_beds/150000-550000_price/2000p_sqft/SINGLE-FAMILY_HOME_type/date;d_sort/1983p_built/resale,sale_pending_lt/'
    agent_url = 'https://www.trulia.com/_ajax/Conversion/LeadFormApi/form/?ab=&disableExclusiveAgent=false&isBuilderCommunity=false&propertyId={}&searchType=pending&stateCode={}'

    def start_requests(self):
        target_states = [state['abbr'] for state in states]
        for zipcode in zipcodes.filter_by(zipcodes.list_all(), active=True):
            if zipcode['state'] in target_states:
                url = self.search_url.format(zipcode['zip_code'])
                yield scrapy.Request(url, callback=self.parse, meta={'state': zipcode['state']})

    def parse(self, response):
        self.logger.info('Crawled (%d) %s' % (response.status, response.url))

        if b'does not match' in response.body:
            return None

        for node in response.xpath('//a[contains(@class, "tileLink")]'):
            if 'Foreclosure' in node.extract() or 'For Sale By Owner' in node.extract() or 'Open House' in node.extract():
                pass
            elif 'Pending' in node.extract():
                yield response.follow(node, callback=self.parse_item, meta={'state': response.meta['state'], 'status': 'Pending'})
            else:
                yield response.follow(node, callback=self.parse_item, meta={'state': response.meta['state'], 'status': 'For Sale'})

        for a in response.xpath('//div[@class="txtC"]//a[@class="pvl phm"]'):
            yield response.follow(a, callback=self.parse, meta={'state': response.meta['state']})

    def parse_item(self, response):
        self.logger.info('Crawled (%d) %s' % (response.status, response.url))
        l = ListingLoader(item=TruliaListingItem(), response=response)
        l.add_value('originUrl', response.url)
        l.add_value('listingStatus', response.meta['status'])
        l.add_xpath('purchasePrice', '//span[@data-role="price"]/text()')
        l.add_xpath('mlsId', '//div[contains(text(), "Communities near")]/text()', re=r'MLS# (\d+)')
        street = response.xpath('//div[@data-role="address"]/text()').extract_first()
        street = street.strip() if street else ''
        city_state = response.xpath('//span[@data-role="cityState"]/text()').extract_first()
        city_state = city_state.strip() if city_state else ''
        l.add_value('propertyAddress', ', '.join([street, city_state]))
        l.add_value('zipCode', city_state.split()[-1])
        l.add_xpath('beds', '//div[contains(@class, "xsColOffset4")]/ul/li/text()', re=r'([0-9\,\.]+) Bed')
        l.add_xpath('baths', '//div[contains(@class, "xsColOffset4")]/ul/li/text()', re=r'([0-9\,\.]+) Bath')
        l.add_xpath('sqft', '//div[contains(div/span/text(), "LISTING INFORMATION")]/ul/li/text()', re=r'(.+) Square Feet')
        l.add_xpath('lotSize', '//div[contains(div/span/text(), "PUBLIC RECORDS")]/ul/li/text()', re=r'Lot Size: (.+)')
        if not l.get_output_value('lotSize'):
            l.add_xpath('lotSize', '//div[contains(div/span/text(), "LISTING INFORMATION")]/ul/li/text()', re=r'Lot Size: (.+)')
        l.add_xpath('photoCount', '//div[@id="mediaCount"]/span/text()', re=r'(\d+) photo')
        l.add_xpath('yearBuilt', '//div[contains(@class, "xsColOffset4")]/ul/li/text()', re=r'Built in ([0-9\,]+)')
        l.add_xpath('daysOnMarket', '//div[contains(@class, "xsColOffset4")]/ul/li/text()', re=r'([0-9\,]+) day')
        l.add_xpath('listingUpdated', '//span[contains(@class, "typeLowlight")]/text()', re=r'Updated: (.+)')
        property_id = re.search(r'/property/(\d+)', response.url).group(1)
        url = self.agent_url.format(property_id, response.meta['state'])
        yield scrapy.Request(url, callback=self.parse_agent_info, meta={'item': l.load_item()})

    def parse_agent_info(self, response):
        self.logger.info('Crawled (%d) %s' % (response.status, response.url))
        data = json.loads(response.body.decode())
        item = response.meta['item']
        item['agentName'] = serialize_name(data['providedBy']['agentName'])
        item['agentMobile'] = serialize_number(data['providedBy']['agentPhone'])
        item['officeName'] = data['providedBy']['brokerName']
        item['officePhone'] = serialize_number(data['providedBy']['brokerPhone'])
        yield item

