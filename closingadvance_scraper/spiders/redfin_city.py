# -*- coding: utf-8 -*-

import re
import json
import scrapy
import zipcodes


class RedfinCitySpider(scrapy.Spider):
    name = 'redfin_city'
    allowed_domains = ['www.redfin.com']
    search_url = 'https://www.redfin.com/stingray/do/location-autocomplete?location={}%2C%20{}&start=0&count=10&v=2&market=dallas&al=1&iss=false&ooa=true'
    start_urls = ['https://www.redfin.com/stingray/do/location-autocomplete?location=Westwood%2C%20NJ&start=0&count=10&v=2&market=dallas&al=1&iss=false&ooa=true']

    # def start_requests(self):
    #     for zipcode in zipcodes.filter_by(zipcodes.list_all(), active=True):
    #         url = self.search_url.format(zipcode['city'].title(), zipcode['state'])
    #         yield scrapy.Request(url, callback=self.parse, meta={'citystate': zipcode['city'].title() + ', ' + zipcode['state']})

    def parse(self, response):
        self.logger.info('Crawled (%d) %s' % (response.status, response.url))
        body = re.sub(r'.+&&', '', response.body.decode())
        data = json.loads(body)
        if 'exactMatch' in data['payload']:
            match = data['payload']['exactMatch']
            if match['type'] == '2' and match['active'] is True:# and match['subName'] == response.meta['citystate']:
                yield match
                #return {'citystate': response.meta['citystate'], 'url': match['url']}

