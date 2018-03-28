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
from closingadvance_scraper.items import RealtorListingForJulienItem
from closingadvance_scraper.loaders import RealtorListingJulienLoader
from closingadvance_scraper.processors import serialize_number, to_datetime
from closingadvance_scraper.processors import serialize_number


logger = logging.getLogger('peewee')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())
from closingadvance_scraper.models import *


class RealtorListingAllSpider(scrapy.Spider):
    name = 'realtor_listing_by_agent_for_julien'
    allowed_domains = ['www.realtor.com']
    listingStatus = ['Active', 'Contingent', 'For Sale', 'New', 'Pending', 'Sold', 'Under Contract']

    def start_requests(self):
        self.listingStatus = [user._data['status'] for user in ListingStatus.select()]
        input_file = csv.DictReader(open(os.path.dirname(os.path.realpath(__file__)) + "/../external_data/input/realtor_agents.csv"), delimiter=";")

        for row in input_file:
            yield scrapy.Request(row["originUrl"], callback=self.parse, meta={'agent_id': row["id"]})

    def parse(self, response):
        self.logger.info('Crawled (%d) %s' % (response.status, response.url))

        for listing_thumbnail in response.xpath('//div[@id="section_recently_sold_all_wrap"]/div'):
            if listing_thumbnail.xpath('.//div[@class="listing-photo-label"]'
                                       '/span[@data-label="property-label-new"]'
                                       '/text()').extract_first().lower() == 'sold' and \
                    'worked with seller' in listing_thumbnail.xpath('.//div[@class="listing-photo-label"]/span/text()').extract()[2].lower():
                link = "https:" + listing_thumbnail.xpath('./@data-prop-url-path').extract_first()
                status = 'sold'
                soldDate = listing_thumbnail.xpath('.//div[@class="listing-photo-label"]/span/text()').extract()[1]
                soldDate = datetime.datetime.strptime(soldDate, '%A, %B %d, %Y').strftime("%Y-%m-%d")
                worked = listing_thumbnail.xpath('.//div[@class="listing-photo-label"]/span/text()').extract()[2]
                purchasePrice = listing_thumbnail.xpath('.//div[@class="listing-info"]//li[@class="listing-info-price"]/text()').extract_first()
                if purchasePrice:
                    purchasePrice = re.sub("[^\d\.]", "", purchasePrice)
                    if purchasePrice.isdigit():
                        purchasePrice = purchasePrice
                meta_payload = {'agent_id': response.meta['agent_id'],
                                'status': status,
                                'soldDate': soldDate,
                                'worked': worked,
                                'purchasePrice': purchasePrice}
                yield response.follow(link, self.parse_listing, meta=meta_payload)

    def parse_listing(self, response):
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
                if status.lower().strip() in listing_status.lower():
                    isListingStatusFound = True
                    listing_status = status
                    break
        if not isListingStatusFound and False and False and False:
            self.logger.info('Not For Sale or Pending %s' % response.url)
            return
        l = RealtorListingJulienLoader(item=RealtorListingForJulienItem(), response=response)
        l.add_value('originUrl', response.url)
        l.add_value('agent_id', response.meta['agent_id'])
        l.add_xpath('agentName', '//span[contains(@data-label, "agent-name")]/text()')
        l.add_xpath('agentMobile', '//span[contains(@data-label, "agent-phone")]/text()')
        l.add_value('status', response.meta['status'])
        l.add_value('soldDate', response.meta['soldDate'])
        l.add_value('worked', response.meta['worked'])
        beds = response.xpath('//div[@id="ldp-property-meta"]//li[@data-label="property-meta-beds"]/span/text()').extract_first()
        isBedsIsInRange = False
        if beds and beds.strip() and beds.strip().isdigit():
            beds = int(beds.strip())
            l.add_value('beds', str(beds))
            if beds >= 3:
                isBedsIsInRange = True
        if not isBedsIsInRange and False and False and False:
            return
        l.add_xpath('baths', '//div[@id="ldp-property-meta"]//li[@data-label="property-meta-bath"]/span/text()')
        isSqftIsInRange = False
        sqft = response.xpath('//li[@data-label="property-meta-sqft"]/span/text()').extract_first()
        if sqft:
            sqft = re.sub("[^\d\.]", "", sqft)
            if sqft and sqft.strip() and sqft.strip().isdigit():
                sqft = int(sqft.strip())
                l.add_value('sqft', str(sqft))
                if sqft >= 1250:
                    isSqftIsInRange = True
        if not isSqftIsInRange and False and False and False:
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
                        l.add_value('lotSize', lotSize)
                        if int(lotSize) < 80000 and int(lotSize) >= 0:
                            isLotSizeIsInRange = True
                elif isAcresLot:
                    l.add_value('lotSize', str(int(43560 * float(lotSize))))
                    if float(lotSize) <= 2.0 and float(lotSize) >= 0:
                        isLotSizeIsInRange = True
        if not isLotSizeIsInRange and False and False and False:
            return
        l.add_xpath('photoCount', '//a[@id="hero-view-photo"]/span[3]/text()', re=r'([0-9\,]+)')
        purchasePrice = response.meta['purchasePrice']
        isPurchasePriceIsInRange = False
        l.add_value('purchasePrice', purchasePrice)
        if int(purchasePrice) > 150000 and int(purchasePrice) < 550000:
            isPurchasePriceIsInRange = True
        if not isPurchasePriceIsInRange and False and False and False:
            return
        currentPrice = response.xpath('//div[@class="ldp-header-price"]//span[@itemprop="price"]/text()').extract_first()
        if currentPrice:
            currentPrice = re.sub("[^\d\.]", "", currentPrice)
            if currentPrice.isdigit():
                l.add_value('currentPrice', currentPrice)
        l.add_xpath('propertyAddress', '//div[@id="ldp-address"]/@content')
        l.add_xpath('zipCode', '//span[@itemprop="postalCode"]/text()')
        moreExpensiveThanNearbyProperties = response.xpath('//span[contains(text(), "More expensive than")]'
                                                           '/preceding-sibling::div/text()').extract_first()
        if moreExpensiveThanNearbyProperties:
            moreExpensiveThanNearbyProperties = re.sub("[^\d\.]", "", moreExpensiveThanNearbyProperties)
            l.add_value('moreExpensiveThanNearbyProperties', str(moreExpensiveThanNearbyProperties))
        lessExpensiveThanNearbyProperties = response.xpath('//span[contains(text(), "Less expensive than")]'
                                                           '/preceding-sibling::div/text()').extract_first()
        if lessExpensiveThanNearbyProperties:
            lessExpensiveThanNearbyProperties = re.sub("[^\d\.]", "", lessExpensiveThanNearbyProperties)
            l.add_value('lessExpensiveThanNearbyProperties', str(lessExpensiveThanNearbyProperties))
        daysOnMarket = response.xpath('//span[contains(text(), "Days on market")]/preceding-sibling::div[@class="summary-datapoint"]/text()').extract_first()
        if daysOnMarket:
            daysOnMarket = re.sub("[^\d\.]", "", daysOnMarket)
            if daysOnMarket.isdigit():
                l.add_value('daysOnMarket', daysOnMarket)
        soldHigherThanTheListedPrice = response.xpath('//span[contains(text(), "Sold higher than")]'
                                                           '/preceding-sibling::div/text()').extract_first()
        if soldHigherThanTheListedPrice:
            soldHigherThanTheListedPrice = re.sub("[^\d\.]", "", soldHigherThanTheListedPrice)
            l.add_value('soldHigherThanTheListedPrice', str(soldHigherThanTheListedPrice))
        soldLowerThanTheListedPrice = response.xpath('//span[contains(text(), "Sold lower than")]'
                                                           '/preceding-sibling::div/text()').extract_first()
        if soldLowerThanTheListedPrice:
            soldLowerThanTheListedPrice = re.sub("[^\d\.]", "", soldLowerThanTheListedPrice)
            l.add_value('soldLowerThanTheListedPrice', str(soldLowerThanTheListedPrice))
        pricePerSqFt = response.xpath('//div[contains(text(), "Price/Sq Ft")]/following-sibling::div/text()').extract_first()
        if pricePerSqFt:
            pricePerSqFt = re.sub("[^\d\.]", "", pricePerSqFt)
            if pricePerSqFt:
                l.add_value('pricePerSqFt', str(pricePerSqFt))
        l.add_value('propertyType', property_type)
        yearBuilt = response.xpath('//div[text()="Built"]/following-sibling::div/text()').extract_first()
        isYearBuiltIsInRange = False
        if yearBuilt and yearBuilt.strip() and yearBuilt.strip().isdigit():
            yearBuilt = int(yearBuilt.strip())
            l.add_value('yearBuilt', str(yearBuilt))
            if yearBuilt >= 1980 and yearBuilt <= 2016:
                isYearBuiltIsInRange = True
        if not isYearBuiltIsInRange and False and False and False:
            return
        medianListingPrice = response.xpath('//div[text()="Median Listing Price"]/preceding-sibling::p/text()').extract_first()
        if medianListingPrice:
            medianListingPrice = re.sub("[^\d\.]", "", medianListingPrice)
            l.add_value('medianListingPrice', str(medianListingPrice))
        medianSalePrice = response.xpath('//div[text()="Median Sales Price"]/preceding-sibling::p/text()').extract_first()
        if medianSalePrice:
            medianSalePrice = re.sub("[^\d\.]", "", medianSalePrice)
            l.add_value('medianSalePrice', str(medianSalePrice))
        medianDaysOnMarket = response.xpath('//div[text()="Median Days on Market"]/preceding-sibling::p/text()').extract_first()
        if medianDaysOnMarket:
            medianDaysOnMarket = re.sub("[^\d\.]", "", medianDaysOnMarket)
            l.add_value('medianDaysOnMarket', str(medianDaysOnMarket))
        averagePricePerSqFt = response.xpath('//div[text()="Price Per Sq Ft"]/preceding-sibling::p/text()').extract_first()
        if averagePricePerSqFt:
            averagePricePerSqFt = re.sub("[^\d\.]", "", averagePricePerSqFt)
            l.add_value('averagePricePerSqFt', str(averagePricePerSqFt))

        yield l.load_item()
