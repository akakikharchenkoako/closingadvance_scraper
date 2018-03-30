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
from closingadvance_scraper.items import RealtorListingExtraJulienItem
from closingadvance_scraper.loaders import RealtorListingExtraJulienLoader
from closingadvance_scraper.processors import serialize_number, to_datetime
from closingadvance_scraper.processors import serialize_number


logger = logging.getLogger('peewee')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())
from closingadvance_scraper.models import *


class RealtorListingExtraSpiderForJulien(scrapy.Spider):
    name = 'realtor_listing_extra_for_julien'
    allowed_domains = ['www.realtor.com']
    listingStatus = ['Active', 'Contingent', 'For Sale', 'New', 'Pending', 'Sold', 'Under Contract']

    def start_requests(self):
        self.listingStatus = [user._data['status'] for user in ListingStatus.select()]
        input_file = csv.DictReader(open(os.path.dirname(os.path.realpath(__file__)) + "/../external_data/input/realtor_listing.csv"), delimiter=";")

        for row in input_file:
            yield scrapy.Request(row["originUrl"], callback=self.parse_item, meta={'listing_id': row["id"]})

    def parse_item(self, response):
        self.logger.info('Crawled (%d) %s' % (response.status, response.url))

        l = RealtorListingExtraJulienLoader(item=RealtorListingExtraJulienItem(), response=response)
        l.add_value('listing_id', response.meta['listing_id'])

        try:
            price_history_block_list = response.xpath('//div[@id="ldp-history-price"]//table/tbody/tr')
            price_history_dict_list = []
            for price_record in price_history_block_list:
                listingDate = price_record.xpath('./td[1]/text()').extract_first()
                if listingDate and listingDate.lower() == "today":
                    listingDate = datetime.date.today().strftime("%Y-%m-%d")
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
        except Exception as e:
            print(e)
            pass

        try:
            tax_history_block_list = response.xpath('//div[@id="ldp-history-taxes"]//table/tbody/tr')
            tax_history_dict_list = []
            for tax_record in tax_history_block_list:
                listingDate = tax_record.xpath('./td[1]/text()').extract_first()
                taxPrice = tax_record.xpath('./td[2]/text()').extract_first()
                if taxPrice:
                    taxPrice = re.sub("[^\d\.]", "", taxPrice)
                tax_history_dict = {'listingDate': listingDate, 'taxPrice': taxPrice}
                if not taxPrice.isdigit():
                    del tax_history_dict['taxPrice']
                tax_history_dict_list.append(tax_history_dict)
            if tax_history_dict_list:
                #l.add_value('priceHistories', json.dumps(price_history_dict_list))
                l.add_value('taxHistories', str(list(reversed(tax_history_dict_list))))
        except Exception as e:
            print(e)
            pass

        try:
            nearby_history_block_list = response.xpath('//div[@id="ldp-nearby-home-values"]//ul[contains(@class, "nearby-homevalues-properties")]/li')
            nearby_history_dict_list = []
            for nearby_record in nearby_history_block_list:
                estimatePrice = nearby_record.xpath('./div[1]/text()').extract_first()
                if estimatePrice:
                    estimatePrice = re.sub("[^\d\.]", "", estimatePrice)
                nearby_history_dict = {'estimatePrice': estimatePrice}
                if not estimatePrice.isdigit():
                    del nearby_history_dict['estimatePrice']
                else:
                    nearby_history_dict_list.append(nearby_history_dict)
            if nearby_history_dict_list:
                #l.add_value('priceHistories', json.dumps(price_history_dict_list))
                l.add_value('nearbyPriceHistories', str(nearby_history_dict_list))
        except Exception as e:
            print(e)
            pass

        yield l.load_item()
