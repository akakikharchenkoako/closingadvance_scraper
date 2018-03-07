# -*- coding: utf-8 -*-

import logging
import scrapy
import zipcodes
from urllib.parse import urljoin

from closingadvance_scraper.locations import states
from closingadvance_scraper.items import RealtorListingItem
from closingadvance_scraper.loaders import ListingLoader
from closingadvance_scraper.processors import serialize_number


logger = logging.getLogger('peewee')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


class RealtorListingSpider(scrapy.Spider):
    name = 'realtor_listing'
    allowed_domains = ['www.realtor.com']
    search_url = 'https://www.realtor.com/realestateandhomes-search/{}/beds-3/type-single-family-home/price-150000-600000/sqft-1250/lot-sqft-0-87120/age-1+30/nc-hide?pgsz=50'
    # start_urls = ['https://www.realtor.com/realestateandhomes-search/Austin_TX/beds-3/type-single-family-home/price-150000-600000/sqft-1250/lot-sqft-0-87120/age-1+30/nc-hide?pgsz=50']

    def start_requests(self):
        target_states = [state['abbr'] for state in states]
        for zipcode in zipcodes.filter_by(zipcodes.list_all(), active=True):
            if zipcode['state'] in target_states:
                url = self.search_url.format(zipcode['zip_code'])
                yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        self.logger.info('Crawled (%d) %s' % (response.status, response.url))

        for li in response.xpath('//li[@data-omtag="srp-listMap:result:link"]'):
            label = li.xpath('.//span[contains(@data-label, "property-label")]/text()').extract_first()
            if label and ('Pending' in label or 'Contingent' in label):
                yield response.follow(li.xpath('.//div[@class="srp-item-photo"]/a')[0], self.parse_item)

        for a in response.xpath('//span[@class="page"]/a'):
            yield response.follow(a, self.parse)

    def parse_item(self, response):
        self.logger.info('Crawled (%d) %s' % (response.status, response.url))

        listing_status = response.xpath('//li[@class="ldp-key-fact-item"]/div[text()="Status"]/following-sibling::div/text()').extract_first()
        property_type = response.xpath('//li[@class="ldp-key-fact-item"]/div[text()="Type"]/following-sibling::div/text()').extract_first()
        if 'Pending' in listing_status:
            listing_status = 'Pending'
        elif 'Contingent' in listing_status:
            listing_status = 'Contingent'
        else:
            return
        if ('Pending' in listing_status or 'Contingent' in listing_status) and 'Single family home' in property_type:
            l = ListingLoader(item=RealtorListingItem(), response=response)
            l.add_value('originUrl', response.url)
            l.add_value('propertyType', property_type)
            l.add_value('listingStatus', listing_status)
            l.add_xpath('daysOnMarket', '//li[@data-label="property-listing-agent"]/div[text()="On realtor.com"]/following-sibling::div/text()', re=r'(\d+)')
            l.add_xpath('propertyAddress', '//div[@id="ldp-address"]/@content')
            l.add_xpath('zipCode', '//span[@itemprop="postalCode"]/text()')
            l.add_xpath('purchasePrice', '//div[@class="ldp-header-price"]/div/span/text()')
            l.add_xpath('mlsId', '//td[@itemprop="productID"]/text()')
            l.add_xpath('yearBuilt', '//div[text()="Built"]/following-sibling::div/text()')
            l.add_xpath('beds', '//li[@data-label="property-meta-beds"]/span/text()')
            l.add_xpath('baths', '//li[@data-label="property-meta-bath"]/span/text()')
            l.add_xpath('sqft', '//li[@data-label="property-meta-sqft"]/span/text()')
            l.add_xpath('lotSize', '//li[@data-label="property-meta-lotsize"]/span/text()')
            l.add_xpath('photoCount', '//a[@id="hero-view-photo"]/span[3]/text()')
            open_house = response.xpath('//div[contains(@class, "open-house-calendar")]/text()').extract_first()
            if open_house and 'None at this time' not in open_house:
                l.add_value('open_house', open_house.strip())
            l.add_xpath('listingUpdated', '//div[@id="ldp-history-price"]//table/tbody/tr[1]/td[1]/text()')
            l.add_xpath('agentName', '//a[@data-omtag="ldp:listingProvider:agentProfile"]/text()')
            l.add_xpath('officeName', '//li[@data-label="additional-office-link"]/a/text()')
            l.add_xpath('officePhone', '//span[contains(@data-label, "office-phone")]/text()')
            href = response.xpath('//a[@data-omtag="ldp:listingProvider:agentProfile"]/@href').extract_first()
            if href:
                yield scrapy.Request(urljoin(response.url, href), self.parse_agent_profile, meta={'item': l.load_item()})
            else:
                yield l.load_item()

    def parse_agent_profile(self, response):
        self.logger.info('Crawled (%d) %s' % (response.status, response.url))
        item = response.meta['item']
        for node in response.xpath('//li/i[contains(@class, "fa-phone")]/..'):
            if 'Mobile:' in node.extract():
                item['agentMobile'] = serialize_number(node.xpath('./a/span/text()').extract_first())
                break
        item['agentProfile'] = response.url
        yield item

