# -*- coding: utf-8 -*-

import logging
import scrapy
import csv
import os
import json
import re
from closingadvance_scraper.items import RealtorListingFix1ForJulienItem
from closingadvance_scraper.loaders import RealtorListingFix1JulienLoader
from closingadvance_scraper.processors import to_datetime


logger = logging.getLogger('peewee')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())
from closingadvance_scraper.models import *


class RealtorListingFix1ForJulienSpider(scrapy.Spider):
    name = 'realtor_listing_fix1_for_julien_spider'
    allowed_domains = ['www.realtor.com']
    listingStatus = ['Active', 'Contingent', 'For Sale', 'New', 'Pending', 'Sold', 'Under Contract']

    def start_requests(self):
        self.listingStatus = [user._data['status'] for user in ListingStatus.select()]
        input_file = csv.DictReader(open(os.path.dirname(os.path.realpath(__file__)) + "/../external_data/input/ID_list_bd_or_ba_is_null.csv"), delimiter=";")

        for row in input_file:
            yield scrapy.Request(row["agentUrl"], callback=self.parse, meta={'listingUrl': row["listingUrl"]})

    def parse(self, response):
        self.logger.info('Crawled (%d) %s' % (response.status, response.url))
        listingUrl = response.meta['listingUrl']
        listingMetaInfo = response.xpath('//a[@href="{0}"]/../..//div[@class="listing-info"]'
                                         '//li[@data-label="property-meta-beds-baths"]'
                                         '//span[@class="data-value"]/text()'.format(listingUrl[6:])).extract_first()

        if listingMetaInfo:
            bedsAndBaths = re.findall('(\d)bd (\d)ba', listingMetaInfo)
            if bedsAndBaths:
                bedsAndBaths = bedsAndBaths[0]
                beds = bedsAndBaths[0]
                baths = bedsAndBaths[1]

                l = RealtorListingFix1JulienLoader(item=RealtorListingFix1ForJulienItem(), response=response)
                l.add_value('beds', beds)
                l.add_value('baths', baths)
                l.add_value('originUrl', response.meta['listingUrl'])

                yield l.load_item()
