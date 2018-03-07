# -*- coding: utf-8 -*-

import re
import json
import scrapy
from urllib.parse import urljoin

from closingadvance_scraper.items import LenderItem


class ZillowLenderSpider(scrapy.Spider):
    name = 'zillow_lender'

    def start_requests(self):
        states = ['California', 'New York']
        for location in states:
            payload = {
                'fields': ['screenName'],
                'location': location,
                'page': 1,
                'pageSize': 20,
                'sort': 'Relevance'
            }
            request = self.make_search_request(payload)
            yield request

    def make_search_request(self, payload):
        url = 'https://mortgageapi.zillow.com/getLenderDirectoryListings?partnerId=RD-JGLGMSG'
        return scrapy.Request(
            url, method='POST',
            callback=self.parse_search,
            body=json.dumps(payload),
            headers={'Content-Type': 'application/json'},
            meta={'payload': payload},
            dont_filter=True)

    def parse_search(self, response):
        self.logger.info('Crawled (%d) %s' % (response.status, response.url))

        try:
            data = json.loads(response.body)
        except TypeError:
            data = json.loads(response.body.decode())

        for lender in data['lenders']:
            payload = {
                "fields": ["aboutMe","address","cellPhone","contactLenderFormDisclaimer","companyName","employerScreenName","equalHousingLogo","faxPhone","imageId","individualName","languagesSpoken","memberFDIC","nationallyRegistered","nmlsId","nmlsType","officePhone","rating","screenName","stateLicenses","stateSponsorships","title","totalReviews","website"],
                "lenderRef": {"screenName": lender['screenName']}
            }
            url = 'https://mortgageapi.zillow.com/getRegisteredLender?partnerId=RD-JGLGMSG'
            yield scrapy.Request(
                url, method='POST',
                callback=self.parse_item,
                body=json.dumps(payload),
                headers={'Content-Type': 'application/json'})

        payload = response.meta['payload']

        if payload['page'] * payload['pageSize'] < data['totalLenders']:
            payload['page'] += 1
            request = self.make_search_request(payload)
            yield request

    def parse_item(self, response):
        self.logger.info('Crawled (%d) %s' % (response.status, response.url))

        try:
            data = json.loads(response.body)
        except TypeError:
            data = json.loads(response.body.decode())

        item = LenderItem()
        item['link'] = 'https://www.trulia.com/mortgage-lender-profile/' + data['lender']['screenName']
        item['name'] = data['lender']['companyName']
        item['address'] = '{}, {}, {} {}'.format(
            data['lender']['address']['address'], data['lender']['address']['city'],
            data['lender']['address']['stateAbbreviation'], data['lender']['address']['zipCode'])
        if 'cellPhone' in data['lender']:
            item['cellPhone'] = '({}) {}-{}'.format(
                data['lender']['cellPhone']['areaCode'],
                data['lender']['cellPhone']['prefix'],
                data['lender']['cellPhone']['number'])
        item['officePhone'] = '({}) {}-{}'.format(
            data['lender']['officePhone']['areaCode'],
            data['lender']['officePhone']['prefix'],
            data['lender']['officePhone']['number'])
        if 'website' in data['lender']:
            item['website'] = data['lender']['website']
            yield scrapy.Request(item['website'], self.parse_email, meta={'item': item})
        else:
            yield item

    def parse_email(self, response):
        self.logger.info('Crawled (%d) %s' % (response.status, response.url))

        item = response.meta['item']

        try:
            emails = re.findall(r'[a-zA-Z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+', response.body.decode())
            if emails:
                item['email'] = ', '.join(set(emails))
                yield item
        except UnicodeDecodeError:
            item['email'] = response.xpath('//body').re_first(r'([a-zA-Z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+)')
            yield item

        for href in response.xpath('//a/@href').extract():
            if 'contact' in href and '.pdf' not in href:
                yield scrapy.Request(urljoin(item['website'], href), self.parse_email, meta={'item': item})

