# -*- coding: utf-8 -*-

import re
import json
from datetime import datetime, timedelta
from urllib.parse import urljoin

import scrapy
from scrapy.selector import Selector

from closingadvance_scraper.models import Agent
from closingadvance_scraper.loaders import ListingLoader
from closingadvance_scraper.items import ZillowListingItem
from closingadvance_scraper.processors import serialize_number, to_datetime


class ZillowListingSpider(scrapy.Spider):
    name = 'zillow_listing'
    allowed_domains = ['www.zillow.com']

    def start_requests(self):
        for row in Agent.select():
            yield scrapy.Request(row.originUrl, callback=self.parse, meta={'agent': row, 'dont_cache': True})

    def parse(self, response):
        self.logger.info('Crawled (%d) %s' % (response.status, response.url))

        for a in response.xpath('//div[contains(@class, "property-listings-table-row")]//div[@class="sh-addr-address"]/a'):
            yield response.follow(a, self.parse_item, meta={'agent': response.meta['agent']})

        for node in response.xpath('//div[contains(@class, "sales-history-table")]//div[contains(@class, "property-listings-table-row")]'):
            date = node.xpath('./div[contains(@class, "sh-sold-date")]/div/text()').extract_first()
            if date:
                date_obj = to_datetime(date)
                if date_obj > datetime.now() - timedelta(days=365):
                    href = node.xpath('.//div[@class="sh-addr-address"]/a/@href').extract_first()
                    if href:
                        url = 'https://www.zillow.com' + href.strip()
                        yield scrapy.Request(url, self.parse_item, meta={'agent': response.meta['agent']})

        body = response.body.decode()
        zuid = re.search(r'zuid:"(.*?)",', body).group(1)
        url = 'https://www.zillow.com/ajax/profile-active-listings/?p={}&pagesize=5&zuid={}&m=0&regId='.format(2, zuid)
        yield scrapy.Request(url, self.parse_listing, meta={'agent': response.meta['agent'], 'dont_cache': True})

    def parse_listing(self, response):
        self.logger.info('Crawled (%d) %s' % (response.status, response.url))

        try:
            data = json.loads(response.body)
        except TypeError:
            data = json.loads(response.body.decode())

        for each in data['props']:
            if each:
                url = urljoin(response.url, each['url']['url'])
                yield scrapy.Request(url, self.parse_item, meta={'agent': response.meta['agent']})

        page = re.search(r'p=(\d+)', response.url).group(1)
        if int(page) * 5 < data['ct']:
            url = re.sub(r'p=\d+', 'p=' + str(int(page) + 1), response.url)
            yield scrapy.Request(url, self.parse_listing, meta={'agent': response.meta['agent'], 'dont_cache': True})

    def parse_item(self, response):
        if b'data-type="Single Family"' not in response.body:
            self.logger.info('Not Single Family %s' % response.url)
            return

        self.logger.info('Crawled (%d) %s' % (response.status, response.url))
        l = ListingLoader(item=ZillowListingItem(), response=response)
        listingStatus = '.'.join(response.xpath('//div[contains(@class, "status-icon-row")]/descendant-or-self::text()').extract())
        if 'Sold' in listingStatus:
            l.add_value('listingStatus', 'Sold')
        elif 'For Sale' in listingStatus:
            l.add_value('listingStatus', 'For Sale')
        elif 'Pending' in listingStatus:
            l.add_value('listingStatus', 'Pending')
        else:
            self.logger.info('Not For Sale or Pending %s' % response.url)
            return
        l.add_value('originUrl', response.url)
        street = response.xpath('//header[@class="zsg-content-header addr"]/h1/text()').extract_first()
        city = response.xpath('//span[contains(@class, "addr_city")]/text()').extract_first()
        l.add_value('propertyAddress', ' '.join([street.strip(), city.strip()]))
        l.add_value('zipCode', city.strip().split()[-1])
        l.add_xpath('mlsId', '//div[@class="zsgxw-subfooter"]/descendant-or-self::text()', re=r'\(MLS #(.*?)\)')
        l.add_xpath('purchasePrice', '//div[contains(@class, "home-summary-row")]/span/text()')
        l.add_xpath('beds', '//span[contains(@class, "addr_bbs")]/text()', re=r'(\d+) bed')
        l.add_xpath('baths', '//span[contains(@class, "addr_bbs")]/text()', re=r'(\d+) bath')
        l.add_xpath('sqft', '//span[contains(@class, "addr_bbs")]/text()', re=r'([0-9\,]+) sqft')
        l.add_xpath('yearBuilt', '//p[contains(text(), "Year Built")]/following-sibling::div/text()', re=r'([0-9]+)')
        l.add_xpath('lotSize', '//p[contains(text(), "Lot")]/following-sibling::div/text()')
        l.add_xpath('daysOnMarket', '//p[contains(text(), "Days on Zillow")]/following-sibling::div/text()', re=r'([0-9\,]+) Day|([0-9\,]+) day')
        l.add_value('photoCount', str(len(response.xpath('//ul[@class="photo-wall-content"]/li').extract())))
        l.add_xpath('listingUpdated', '//h3[contains(text(), "Price History")]/following-sibling::table//tr[1]/td/text()')
        l.add_xpath('openHouse', '//p[contains(text(), "Open House")]/following-sibling::ul/li/span/text()')
        l.add_value('agent', response.meta['agent'])
        body = response.body.decode()
        if l.get_output_value('listingStatus') == 'Sold':
            end = body.find('jsModule:"z-hdp-price-history"')
            price_history_url = re.search(r'ajaxURL:"(.*?)",', body[end - 1000:end]).group(1)
            price_history_url = urljoin(response.url, price_history_url)
            return scrapy.Request(
                price_history_url,
                self.parse_price_history,
                meta={'item': l.load_item()})
        else:
            start = body.find('#contact-wide-response')
            ajax_url = re.search(r'ajaxURL:"(.*?)",', body[start:start + 1000]).group(1)
            ajax_url = urljoin(response.url, ajax_url)
            end = body.find('jsModule:"z-hdp-price-history"')
            price_history_url = re.search(r'ajaxURL:"(.*?)",', body[end - 1000:end]).group(1)
            price_history_url = urljoin(response.url, price_history_url)
            return scrapy.Request(
                ajax_url,
                self.parse_listing_info,
                meta={'item': l.load_item(), 'price_history_url': price_history_url})

    def parse_listing_info(self, response):
        self.logger.info('Crawled (%d) %s' % (response.status, response.url))
        item = response.meta['item']
        try:
            data = json.loads(response.body)
        except TypeError:
            data = json.loads(response.body.decode())
        selector = Selector(text=data['html'])
        text = selector.xpath('//p[@class="enhancedField"]/descendant-or-self::text()').extract()
        text = list(filter(lambda x: len(x.strip()) > 0, text))
        if text:
            for idx, t in enumerate(text):
                if re.search(r'\(\d+\)', t):
                    if idx > 2:
                        item['officeName'] = text[idx - 2].strip() + ' ' + text[idx - 1].strip()
                        item['officePhone'] = serialize_number(text[idx].strip())
                    else:
                        item['officeName'] = text[idx - 1].strip()
                        item['officePhone'] = serialize_number(text[idx].strip())
        else:
            text = selector.xpath('//div[@class="zsg-media-bd"]/p/descendant-or-self::text()').extract()
            if len(text) == 1:
                text = text[0].split(',')
            for idx, t in enumerate(text):
                if re.search(r'\(\d+\)', t):
                    if idx > 2:
                        item['officeName'] = text[idx - 2].strip() + ' ' + text[idx - 1].strip()
                        item['officePhone'] = serialize_number(text[idx].strip())
                    else:
                        item['officeName'] = text[idx - 1].strip()
                        item['officePhone'] = serialize_number(text[idx].strip())
        yield scrapy.Request(
            response.meta['price_history_url'],
            self.parse_price_history,
            meta={'item': item, 'price_history_url': response.meta['price_history_url']})

    def parse_price_history(self, response):
        self.logger.info('Crawled (%d) %s' % (response.status, response.url))
        item = response.meta['item']
        try:
            data = json.loads(response.body)
        except TypeError:
            data = json.loads(response.body.decode())
        if data['html']:
            selector = Selector(text=data['html'])
            entries = []
            for node in selector.xpath('//table/tbody/tr'):
                entry = dict()
                entry['listingDate'] = to_datetime(node.xpath('./td[1]/text()').extract_first())
                if 'listingUpdated' not in item:
                    item['listingUpdated'] = entry['listingDate']
                entry['listingEvent'] = node.xpath('./td[2]/text()').extract_first().strip()
                if 'Sold' in entry['listingEvent']:
                    href = node.xpath('./td[4]/a/@href').extract_first()
                    if href:
                        entry['listingAgent'] = 'https://www.zillow.com' + href.strip()
                else:
                    listingSource = node.xpath('./td[5]/text()').extract_first()
                    if listingSource:
                        entry['listingSource'] = listingSource.strip()
                purchase_price = serialize_number(node.xpath('./td[3]/span/text()').extract_first())
                if purchase_price:
                    entry['purchasePrice'] = purchase_price
                entries.append(entry)
            entries.reverse()
            item['priceHistories'] = entries
        yield item

