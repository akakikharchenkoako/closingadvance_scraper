# -*- coding: utf-8 -*-

import logging
import scrapy
import csv
import os
import json
import re
from urllib.parse import urljoin
from closingadvance_scraper.locations import states
from closingadvance_scraper.models import ListingStatus
from closingadvance_scraper.items import RealtorListingItem
from closingadvance_scraper.loaders import RealtorListingLoader
from closingadvance_scraper.processors import serialize_number, to_datetime
from closingadvance_scraper.processors import serialize_number


logger = logging.getLogger('peewee')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())
from closingadvance_scraper.models import *


class RealtorListingSpider(scrapy.Spider):
    name = 'realtor_listing_by_agent'
    allowed_domains = ['www.realtor.com']
    listingStatus = ['Active', 'Contingent', 'For Sale', 'New', 'Pending', 'Sold', 'Under Contract']

    def start_requests(self):
        self.listingStatus = [user._data['status'] for user in ListingStatus.select()]
        input_file = csv.DictReader(open(os.path.dirname(os.path.realpath(__file__)) + "/../external_data/output/filtered agent list.csv"), delimiter=";")

        for row in input_file:
            yield scrapy.Request(row["originUrl"], callback=self.parse, meta={'agent_id': row["id"], 'brokers_list': row["brokers_list"]})
        '''
        yield scrapy.Request('https://www.realtor.com/realestateandhomes-detail/2830-Sombrero-Ln_Fort-Collins_CO_80525_M13066-96328',
                             callback=self.parse_item,
                             meta={'agent_id': '1', 'brokers_list': '2'})
        '''

    def parse(self, response):
        self.logger.info('Crawled (%d) %s' % (response.status, response.url))

        for property in response.xpath('//div[@id="section_for_sale_all_wrap"]//div[@class="aspect-content"]//div[@class="listing-photo"]//a'):
            link = property.xpath('./@href').extract_first()
            if link:
                yield response.follow(link, self.parse_item, meta={'agent_id': response.meta['agent_id'], 'brokers_list': response.meta['brokers_list']})

    def parse_item(self, response):
        self.logger.info('Crawled (%d) %s' % (response.status, response.url))

        property_type = response.xpath('//li[@class="ldp-key-fact-item"]/div[text()="Type"]/following-sibling::div/text()').extract_first()

        if 'single family' not in property_type.lower():
            self.logger.info('Not Single Family %s' % response.url)
            return

        listing_status = response.xpath(
            '//li[@class="ldp-key-fact-item"]/div[text()="Status"]/following-sibling::div/text()').extract_first()
        isListingStatusFound = False

        if listing_status:
            for status in self.listingStatus:
                if status.lower() in listing_status.lower():
                    isListingStatusFound = True
                    listing_status = status
                    break

        if not isListingStatusFound:
            self.logger.info('Not For Sale or Pending %s' % response.url)
            return

        l = RealtorListingLoader(item=RealtorListingItem(), response=response)
        l.add_value('originUrl', response.url)
        l.add_value('propertyType', property_type)
        l.add_value('listingStatus', listing_status)
        l.add_xpath('propertyAddress', '//div[@id="ldp-address"]/@content')
        l.add_xpath('zipCode', '//span[@itemprop="postalCode"]/text()')
        daysOnRealtor = response.xpath('//i[@class="ra ra-days-on-realtor"]/following-sibling::div[@class="key-fact-data ellipsis"]/text()').extract_first()
        if daysOnRealtor:
            daysOnRealtor = re.sub("[^\d\.]", "", daysOnRealtor)
            if daysOnRealtor.isdigit():
                l.add_value('daysOnRealtor', daysOnRealtor)
        medianDaysOnMarket = response.xpath('//div[text()="Median Days on Market"]/preceding-sibling::p/text()').extract_first()
        if medianDaysOnMarket:
            medianDaysOnMarket = re.sub("[^\d\.]", "", medianDaysOnMarket)
            if medianDaysOnMarket.isdigit():
                l.add_value('medianDaysOnMarket', medianDaysOnMarket)
        daysOnMarket = response.xpath('//span[contains(text(), "Days on market")]/preceding-sibling::div[@class="summary-datapoint"]/text()').extract_first()
        if daysOnMarket:
            daysOnMarket = re.sub("[^\d\.]", "", daysOnMarket)
            if daysOnMarket.isdigit():
                l.add_value('daysOnMarket', daysOnMarket)
        propertyTax = response.xpath('//input[@id="property_tax"]/@value').extract_first()
        if propertyTax:
            propertyTax = re.sub("[^\d\.]", "", propertyTax)
            if propertyTax.isdigit():
                l.add_value('propertyTax', propertyTax)
        purchasePrice = response.xpath('//div[@class="ldp-header-price"]/div/span/text()').extract_first()
        isPurchasePriceIsInRange = False
        if purchasePrice:
            purchasePrice = re.sub("[^\d\.]", "", purchasePrice)
            if purchasePrice.isdigit() and int(purchasePrice) > 150000 and int(purchasePrice) < 550000:
                l.add_value('purchasePrice', purchasePrice)
                isPurchasePriceIsInRange = True
        if not isPurchasePriceIsInRange:
            return
        lastSoldPrice = response.xpath('//span[text()="Last Sold for"]/following-sibling::span[@itemprop="price"]/@content').extract_first()
        if lastSoldPrice:
            if lastSoldPrice.isdigit():
                l.add_value('lastSoldPrice', lastSoldPrice)
        l.add_xpath('mlsId', '//td[@itemprop="productID"]/text()')
        yearBuilt = response.xpath('//div[text()="Built"]/following-sibling::div/text()').extract_first()
        isYearBuiltIsInRange = False
        if yearBuilt and yearBuilt.strip() and yearBuilt.strip().isdigit():
            yearBuilt = int(yearBuilt.strip())
            if yearBuilt >= 1980 and yearBuilt <= 2016:
                l.add_value('yearBuilt', str(yearBuilt))
                isYearBuiltIsInRange = True
        if not isYearBuiltIsInRange:
            return
        beds = response.xpath('//div[@id="ldp-property-meta"]//li[@data-label="property-meta-beds"]/span/text()').extract_first()
        isBedsIsInRange = False
        if beds and beds.strip() and beds.strip().isdigit():
            beds = int(beds.strip())
            if beds >= 3:
                l.add_value('beds', str(beds))
                isBedsIsInRange = True
        if not isBedsIsInRange:
            return
        l.add_xpath('baths', '//div[@id="ldp-property-meta"]//li[@data-label="property-meta-bath"]/span/text()')
        isSqftIsInRange = False
        sqft = response.xpath('//li[@data-label="property-meta-sqft"]/span/text()').extract_first()
        if sqft:
            sqft = re.sub("[^\d\.]", "", sqft)
            if sqft and sqft.strip() and sqft.strip().isdigit():
                sqft = int(sqft.strip())
                if sqft >= 1250:
                    l.add_value('sqft', str(sqft))
                    isSqftIsInRange = True
        if not isSqftIsInRange:
            return
        lotSize = response.xpath('//li[@data-label="property-meta-lotsize"]')
        isSqftLot = 'sqft lot' in ' ' . join(lotSize.xpath('./text()').extract())
        isAcresLot = 'acres lot' in ' ' . join(lotSize.xpath('./text()').extract())
        isLotSizeIsInRange = False
        if lotSize and (isSqftLot or isAcresLot):
            lotSize = lotSize.xpath('./span/text()').extract_first()
            if lotSize:
                if isSqftLot:
                    lotSize = re.sub("[^\d\.]", "", lotSize)
                    if lotSize.isdigit():
                        if int(lotSize) < 80000 and int(lotSize) >= 0:
                            l.add_value('lotSize', lotSize)
                            isLotSizeIsInRange = True
                elif isAcresLot:
                    if float(lotSize) <= 2.0 and float(lotSize) >= 0:
                        l.add_value('lotSize', str(int(43560 * float(lotSize))))
                        isLotSizeIsInRange = True
        if not isLotSizeIsInRange:
            return
        l.add_xpath('photoCount', '//a[@id="hero-view-photo"]/span[3]/text()', re=r'([0-9\,]+)')
        open_house = response.xpath('//div[contains(@class, "open-house-calendar")]//time/text()').extract_first()
        if open_house and open_house.strip():
            l.add_value('open_house', open_house.strip())
        listingUpdated = response.xpath('//div[@id="ldp-history-price"]//table/tbody/tr[1]/td[1]/text()').extract_first()
        if listingUpdated and listingUpdated.strip():
            l.add_value('listingUpdated', to_datetime(listingUpdated).strftime("%Y-%m-%d"))
        l.add_value('agent_id', response.meta['agent_id'])
        l.add_value('brokers_list', response.meta['brokers_list'])
        l.add_xpath('agentName', '//span[contains(@data-label, "agent-name")]/text()')
        l.add_xpath('agentMobile', '//span[contains(@data-label, "agent-phone")]/text()')
        l.add_xpath('officeName', '//li[@data-label="additional-office-link"]/a/text()')
        l.add_xpath('officePhone', '//span[contains(@data-label, "office-phone")]/text()')
        price_history_block_list = response.xpath('//div[@id="ldp-history-price"]//table/tbody/tr')
        price_history_dict_list = []
        for price_record in price_history_block_list:
            listingDate = price_record.xpath('./td[1]/text()').extract_first()
            listingEvent = price_record.xpath('./td[2]/text()').extract_first()
            purchasePrice = price_record.xpath('./td[3]/text()').extract_first()
            listingSource = price_record.xpath('./td[5]/text()').extract_first()
            if purchasePrice:
                purchasePrice = re.sub("[^\d\.]", "", purchasePrice)
            price_history_dict = {'listingDate': to_datetime(listingDate).strftime("%Y-%m-%d"),
                                  'listingEvent': listingEvent,
                                  'purchasePrice': purchasePrice,
                                  'listingSource': listingSource}
            if not purchasePrice.isdigit():
                del price_history_dict['purchasePrice']
            price_history_dict_list.append(price_history_dict)
        if price_history_dict_list:
            #l.add_value('priceHistories', json.dumps(price_history_dict_list))
            l.add_value('priceHistories', str(list(reversed(price_history_dict_list))))
        yield l.load_item()
