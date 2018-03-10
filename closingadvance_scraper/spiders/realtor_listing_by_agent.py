# -*- coding: utf-8 -*-

import logging
import scrapy
import csv
import os
import re
from urllib.parse import urljoin
from closingadvance_scraper.locations import states
from closingadvance_scraper.items import RealtorListingItem
from closingadvance_scraper.loaders import ListingLoader
from closingadvance_scraper.processors import serialize_number


logger = logging.getLogger('peewee')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())
from closingadvance_scraper.models import *


class RealtorListingSpider(scrapy.Spider):
    name = 'realtor_listing_by_agent'
    allowed_domains = ['www.realtor.com']

    def start_requests(self):
        input_file = csv.DictReader(open(os.path.dirname(os.path.realpath(__file__)) + "/../external_data/agent id list.csv"), delimiter=";")

        for row in input_file:
            yield scrapy.Request(row["originUrl"], callback=self.parse, meta={'id': row["id"]})

    def parse(self, response):
        self.logger.info('Crawled (%d) %s' % (response.status, response.url))

        for property in response.xpath('//div[@id="section_for_sale_all_wrap"]//div[@class="aspect-content"]//div[@class="listing-photo"]//a'):
            link = property.xpath('./@href').extract_first()
            if link:
                yield response.follow(link, self.parse_item, meta={'id': response.meta['id']})

    def parse_item(self, response):
        self.logger.info('Crawled (%d) %s' % (response.status, response.url))

        property_type = response.xpath('//li[@class="ldp-key-fact-item"]/div[text()="Type"]/following-sibling::div/text()').extract_first()

        if 'single family home' not in property_type.lower():
            self.logger.info('Not Single Family %s' % response.url)
            return

        listing_status = response.xpath(
            '//li[@class="ldp-key-fact-item"]/div[text()="Status"]/following-sibling::div/text()').extract_first()

        if listing_status:
            if 'active' in listing_status.lower():
                listing_status = 'Active'
            elif 'new' in listing_status.lower():
                listing_status = 'New'
            elif 'sold' in listing_status.lower():
                listing_status = 'Sold'
            elif 'for sale' in listing_status.lower():
                listing_status = 'For Sale'
            elif 'pending' in listing_status.lower():
                listing_status = 'Pending'
            elif "under contract" in listing_status.lower():
                listing_status = 'Under Contract'
            else:
                listing_status = None

        if not listing_status:
            self.logger.info('Not For Sale or Pending %s' % response.url)
            return

        l = ListingLoader(item=RealtorListingItem(), response=response)
        l.add_value('originUrl', response.url)
        l.add_value('propertyType', property_type)
        l.add_value('listingStatus', listing_status)
        l.add_xpath('daysOnMarket', '//li[@data-label="property-listing-agent"]/div[text()="On realtor.com"]/following-sibling::div/text()', re=r'(\d+)')
        l.add_xpath('propertyAddress', '//div[@id="ldp-address"]/@content')
        l.add_xpath('zipCode', '//span[@itemprop="postalCode"]/text()')
        purchasePrice = response.xpath('//div[@class="ldp-header-price"]/div/span')
        if purchasePrice:
            purchasePrice = purchasePrice.xpath('./text()').extract_first().strip()
            l.add_value('purchasePrice', purchasePrice.strip())
        l.add_xpath('mlsId', '//td[@itemprop="productID"]/text()')
        l.add_xpath('yearBuilt', '//div[text()="Built"]/following-sibling::div/text()')
        l.add_xpath('beds', '//div[@id="ldp-property-meta"]//li[@data-label="property-meta-beds"]/span/text()')
        l.add_xpath('baths', '//div[@id="ldp-property-meta"]//li[@data-label="property-meta-bath"]/span/text()')
        l.add_xpath('sqft', '//li[@data-label="property-meta-sqft"]/span/text()', re=r'([0-9\,]+)')
        l.add_xpath('lotSize', '//li[@data-label="property-meta-lotsize"]/span/text()', re=r'([0-9\,]+)')
        l.add_xpath('photoCount', '//a[@id="hero-view-photo"]/span[3]/text()', re=r'([0-9\,]+)')
        open_house = response.xpath('//div[contains(@class, "open-house-calendar")]//time/text()').extract_first()
        if open_house and open_house.strip():
            l.add_value('open_house', open_house.strip())
        l.add_xpath('listingUpdated', '//div[@id="ldp-history-price"]//table/tbody/tr[1]/td[1]/text()')
        l.add_value('agent_id', response.meta['id'])
        l.add_xpath('officeName', '//li[@data-label="additional-office-link"]/a/text()')
        l.add_xpath('officePhone', '//span[contains(@data-label, "office-phone")]/text()')
        price_history_block_list = response.xpath('//div[@id="ldp-history-price"]//table/tbody/tr')
        price_history_dict_list = []
        for price_record in price_history_block_list:
            listingDate = price_record.xpath('./td[1]/text()').extract_first()
            listingEvent = price_record.xpath('./td[2]/text()').extract_first()
            purchasePrice = price_record.xpath('./td[3]/text()').extract_first()
            if purchasePrice:
                purchasePrice = re.sub("[^\d\.]", "", purchasePrice)
            listingSource = price_record.xpath('./td[5]/text()').extract_first()
            price_history_dict_list.append({'listingDate': listingDate,
                                            'listingEvent': listingEvent,
                                            'purchasePrice': purchasePrice,
                                            'listingSource': listingSource})
        if price_history_dict_list:
            l.add_value('priceHistories', price_history_dict_list)
        '''
        PriceHistory.create(
            id=id,
            listing=listing,
            listingDate=entry.get('listingDate'),
            purchasePrice=entry.get('purchasePrice'),
            listingEvent=entry.get('listingEvent'),
                listingSource=entry.get('listingSource'),
            listingAgent=entry.get('listingAgent')
        '''
        yield l.load_item()
