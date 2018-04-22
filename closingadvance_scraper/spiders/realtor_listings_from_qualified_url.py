# -*- coding: utf-8 -*-

import logging
import scrapy
import csv
import os
import json
import re
from closingadvance_scraper.locations import states
from closingadvance_scraper.items import RealtorListingForJulienItem
from closingadvance_scraper.loaders import RealtorListingJulienLoader
from closingadvance_scraper.processors import to_datetime


logger = logging.getLogger('peewee')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())
from closingadvance_scraper.models import *


class RealtorListingFromQualifiedUrlsSpider(scrapy.Spider):
    handle_httpstatus_list = [400, 404, 503, 500]
    name = 'realtor_listing_from_qualified_urls_spider'
    base_url = "https://www.realtor.com"
    allowed_domains = ['www.realtor.com']
    listingStatus = ['Active', 'Contingent', 'For Sale', 'New', 'Pending', 'Sold', 'Under Contract']
    statesAbbrList = [state['abbr'] for state in states]

    def start_requests(self):
        self.listingStatus = [user._data['status'] for user in ListingStatus.select()]

        with open(os.path.dirname(os.path.realpath(__file__)) + "/../external_data/output/failure_list.csv", "w") as output_file:
                output_file.write("")

        output_file.close()

        with open(os.path.dirname(os.path.realpath(__file__)) + "/../external_data/output/realtor_listing_urls.csv") as f:
            for line in f:
                yield scrapy.Request(line.strip(),
                                     callback=self.parse_listing,
                                     headers={'X-Crawlera-Profile': 'desktop'})

    def parse_listing(self, response):
        self.logger.info('Crawled (%d) %s' % (response.status, response.url))

        if response.status == 200:
            try:
                listingPropertyJson = json.loads(re.findall(re.compile(r'MOVE_DATA.propertyDetails,(.*?)\);\n', flags=re.DOTALL), response.text)[0].strip())
                listingProvider = listingPropertyJson.get("listing_provider", {})

                l = RealtorListingJulienLoader(item=RealtorListingForJulienItem(), response=response)

                propertyType = listingPropertyJson['prop_type']
                originUrl = response.url
                agentUrl = self.base_url + listingProvider.get("agent_profile_link") if listingProvider.get("agent_profile_link") else None
                agentName = listingProvider.get("agent_name")
                status = listingPropertyJson.get("property_status")
                soldDate = response.xpath("//span[@data-label='property-meta-sold-date']/text()").extract_first()
                if soldDate:
                    soldDate = soldDate[soldDate.find(" on ") + 4:].strip()
                    soldDate = datetime.datetime.strptime(soldDate, '%B %d, %Y').strftime("%Y-%m-%d")
                beds = str(listingPropertyJson.get("beds", ""))
                baths = str(listingPropertyJson.get("baths" ""))
                sqft = str(listingPropertyJson.get("sqft", ""))
                lotSize = str(listingPropertyJson.get("lot_size", ""))
                photoCount = response.xpath('//a[@id="hero-view-photo"]/span[3]/text()').extract_first()
                if photoCount:
                    photoCount = str(re.sub("[^\d\.]", "", photoCount))
                lastSoldPrice = str(listingPropertyJson.get("price", ""))
                propertyAddress = listingPropertyJson.get("full_address_display")
                zipCode = response.xpath("//meta[@property='og:postal-code']/@content").extract_first()
                moreExpensiveThanNearbyProperties = response.xpath('//span[contains(text(), "More expensive than")]'
                                                                   '/preceding-sibling::div/text()').extract_first()
                if moreExpensiveThanNearbyProperties:
                    moreExpensiveThanNearbyProperties = re.sub("[^\d\.]", "", moreExpensiveThanNearbyProperties).strip()
                lessExpensiveThanNearbyProperties = response.xpath('//span[contains(text(), "Less expensive than")]'
                                                                   '/preceding-sibling::div/text()').extract_first()
                if lessExpensiveThanNearbyProperties:
                    lessExpensiveThanNearbyProperties = re.sub("[^\d\.]", "", lessExpensiveThanNearbyProperties).strip()
                daysOnMarket = response.xpath(
                    '//span[contains(text(), "Days on market")]/preceding-sibling::div[@class="summary-datapoint"]/text()').extract_first()
                if daysOnMarket:
                    daysOnMarket = re.sub("[^\d\.]", "", daysOnMarket).strip()
                soldHigherThanTheListedPrice = response.xpath('//span[contains(text(), "Sold higher than")]'
                                                              '/preceding-sibling::div/text()').extract_first()
                if soldHigherThanTheListedPrice:
                    soldHigherThanTheListedPrice = re.sub("[^\d\.]", "", soldHigherThanTheListedPrice).strip()
                soldLowerThanTheListedPrice = response.xpath('//span[contains(text(), "Sold lower than")]'
                                                             '/preceding-sibling::div/text()').extract_first()
                if soldLowerThanTheListedPrice:
                    soldLowerThanTheListedPrice = re.sub("[^\d\.]", "", soldLowerThanTheListedPrice).strip()
                pricePerSqFt = response.xpath(
                    '//div[contains(text(), "Price/Sq Ft")]/following-sibling::div/text()').extract_first()
                if pricePerSqFt:
                    pricePerSqFt = re.sub("[^\d\.]", "", pricePerSqFt).strip()
                yearBuilt = str(listingPropertyJson.get("year_built", ""))
                medianListingPrice = response.xpath(
                    '//div[text()="Median Listing Price"]/preceding-sibling::p/text()').extract_first()
                if medianListingPrice:
                    medianListingPrice = re.sub("[^\d\.]", "", medianListingPrice).strip()
                '''
                medianSalePrice = response.xpath(
                    '//div[text()="Median Sales Price"]/preceding-sibling::p/text()').extract_first()
                if medianSalePrice:
                    medianSalePrice = re.sub("[^\d\.]", "", medianSalePrice).strip()
                '''
                medianDaysOnMarket = response.xpath(
                    '//div[text()="Median Days on Market"]/preceding-sibling::p/text()').extract_first()
                if medianDaysOnMarket:
                    medianDaysOnMarket = re.sub("[^\d\.]", "", medianDaysOnMarket).strip()
                averagePricePerSqFt = response.xpath(
                    '//div[text()="Price Per Sq Ft"]/preceding-sibling::p/text()').extract_first()
                if averagePricePerSqFt:
                    averagePricePerSqFt = re.sub("[^\d\.]", "", averagePricePerSqFt).strip()

                l.add_value('originUrl', originUrl)
                l.add_value('agentUrl', agentUrl)
                l.add_value('agentName', agentName)
                l.add_value('status', status)
                l.add_value('soldDate', soldDate)
                l.add_value('beds', beds)
                l.add_value('baths', baths)
                l.add_value('sqft', sqft)
                l.add_value('lotSize', lotSize)
                l.add_value('photoCount', photoCount)
                l.add_value('lastSoldPrice', lastSoldPrice)
                l.add_value('propertyAddress', propertyAddress)
                l.add_value('zipCode', zipCode)
                l.add_value('moreExpensiveThanNearbyProperties', moreExpensiveThanNearbyProperties)
                l.add_value('lessExpensiveThanNearbyProperties', lessExpensiveThanNearbyProperties)
                l.add_value('daysOnMarket', daysOnMarket)
                l.add_value('soldHigherThanTheListedPrice', soldHigherThanTheListedPrice)
                l.add_value('soldLowerThanTheListedPrice', soldLowerThanTheListedPrice)
                l.add_value('pricePerSqFt', pricePerSqFt)
                l.add_value('propertyType', propertyType)
                l.add_value('yearBuilt', yearBuilt)
                l.add_value('medianListingPrice', medianListingPrice)
                l.add_value('medianDaysOnMarket', medianDaysOnMarket)
                l.add_value('averagePricePerSqFt', averagePricePerSqFt)


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
                        # l.add_value('priceHistories', json.dumps(price_history_dict_list))
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
                        # l.add_value('priceHistories', json.dumps(price_history_dict_list))
                        l.add_value('taxHistories', str(list(reversed(tax_history_dict_list))))
                except Exception as e:
                    print(e)
                    pass

                try:
                    nearby_history_block_list = response.xpath(
                        '//div[@id="ldp-nearby-home-values"]//ul[contains(@class, "nearby-homevalues-properties")]/li')
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
                        # l.add_value('priceHistories', json.dumps(price_history_dict_list))
                        l.add_value('nearbyPriceHistories', str(nearby_history_dict_list))
                except Exception as e:
                    print(e)
                    pass

                yield l.load_item()
            except Exception as e:
                print(e)
        else:
            with open(os.path.dirname(os.path.realpath(__file__)) + "/../external_data/output/404_list.csv",
                      "a") as output_file:
                output_file.write(response.url + "\n")

