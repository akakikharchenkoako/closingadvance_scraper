# -*- coding: utf-8 -*-

import re
import json
from urllib.parse import urljoin
import scrapy
from scrapy.spiders import CSVFeedSpider

from closingadvance_scraper.items import RedfinListingItem
from closingadvance_scraper.loaders import ListingLoader


class RedfinListingSpider(CSVFeedSpider):
    name = 'redfin_listing'
    allowed_domains = ['www.redfin.com']
    search_url = 'https://www.redfin.com{}/filter/property-type=house,min-price=150k,max-price=600k,min-beds=3,min-sqft=1.25k-sqft,min-year-built=1980,max-year-built=2016,max-lot-size=5-acre,status=contingent+pending'
    delimiter = ','
    headers = ['SALE TYPE','SOLD DATE','PROPERTY TYPE','ADDRESS','CITY','STATE','ZIP','PRICE','BEDS','BATHS','LOCATION','SQUARE FEET','LOT SIZE','YEAR BUILT','DAYS ON MARKET','$/SQUARE FEET','HOA/MONTH','STATUS','NEXT OPEN HOUSE START TIME','NEXT OPEN HOUSE END TIME','URL (SEE http://www.redfin.com/buy-a-home/comparative-market-analysis FOR INFO ON PRICING)','SOURCE','MLS#','FAVORITE','INTERESTED','LATITUDE','LONGITUDE']

    def start_requests(self):
        with open('redfin_city.txt', 'r') as f:
            for line in f.readlines():
                json_obj = json.loads(line)
                url = self.search_url.format(json_obj['url'])
                yield scrapy.Request(url, callback=self.parse_search)

    def parse_search(self, response):
        self.logger.info('Crawled (%d) %s' % (response.status, response.url))

        download_link = response.xpath('//a[@id="download-and-save"]/@href').extract_first()
        if download_link:
            yield scrapy.Request(urljoin(response.url, download_link), self.parse)

    def parse_row(self, response, row):
        if row['ZIP'] == 'ZIP':
            return
        item = RedfinListingItem()
        item['originUrl'] = row['URL (SEE http://www.redfin.com/buy-a-home/comparative-market-analysis FOR INFO ON PRICING)']
        item['propertyType'] = row['PROPERTY TYPE']
        item['listingStatus'] = row['STATUS']
        item['mlsId'] = row['MLS#']
        item['zipCode'] = row['ZIP']
        item['purchasePrice'] = row['PRICE']
        item['daysOnMarket'] = row['DAYS ON MARKET']
        item['yearBuilt'] = row['YEAR BUILT']
        item['beds'] = row['BEDS']
        item['baths'] = row['BATHS']
        item['sqft'] = row['SQUARE FEET'] if row['SQUARE FEET'] else None
        item['lotSize'] = row['LOT SIZE']
        item['propertyAddress'] = ', '.join([row['ADDRESS'], row['CITY'], row['STATE']]) + ' ' + row['ZIP']
        yield item


