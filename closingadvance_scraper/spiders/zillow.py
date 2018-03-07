# -*- coding: utf-8 -*-

import re
import json
from urllib.parse import urljoin
import scrapy
import zipcodes
from scrapy.selector import Selector

from closingadvance_scraper.items import ZillowListingItem, ZillowBrokerItem
from closingadvance_scraper.loaders import ListingLoader, BrokerLoader
from closingadvance_scraper.processors import serialize_number, to_datetime


class ZillowSpider(scrapy.Spider):
    name = 'zillow'
    allowed_domains = ['www.zillow.com']
    search_url = 'https://www.zillow.com/homes/for_sale/{}-{}-{}/fsba_lt/house_type/2-_beds/150000-550000_price/561-2057_mp/14_days/1_pnd/11_zm/0_mmm/'
    # start_urls = ['https://www.zillow.com/homes/for_sale/Austin-TX-78741/fsba_lt/house_type/2-_beds/150000-550000_price/561-2057_mp/7_days/1_pnd/11_zm/0_mmm/']

    def start_requests(self):
        for zipcode in zipcodes.list_all():
            url = self.search_url.format(zipcode['city'], zipcode['state'], zipcode['zip_code'])
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        self.logger.info('Crawled (%d) %s' % (response.status, response.url))

        for node in response.xpath('//div[contains(@class, "zsg-photo-card-content")]'):
            status = node.xpath('.//span[@class="zsg-photo-card-status"]/text()').extract_first()
            if 'Pending' in status or 'House For Sale' in status:
                yield response.follow(node.xpath('.//a[contains(@class, "hdp-link")]')[0], self.parse_item)

    def parse_item(self, response):
        if b'data-type="Single Family"' not in response.body:
            return

        self.logger.info('Crawled (%d) %s' % (response.status, response.url))
        l = ListingLoader(item=ZillowListingItem(), response=response)
        l.add_xpath('listingStatus', '//div[contains(@class, "status-icon-row")]/text()')
        listingStatus = l.get_output_value('listingStatus')
        listingStatus = listingStatus.strip() if listingStatus else ''
        if not listingStatus or (listingStatus != 'Pending' and listingStatus != 'For Sale'):
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
        l.add_xpath('agentMobile', '//span[@class="snl phone"]/text()')
        l.add_xpath('agentName', '//span[@class="snl name notranslate"]/text()')
        l.add_xpath('listingUpdated', '//h3[contains(text(), "Price History")]/following-sibling::table//tr[1]/td/text()')
        body = response.body.decode()
        start = body.find('#contact-wide-response')
        ajax_url = re.search(r'ajaxURL:"(.*?)",', body[start:start + 1000]).group(1)
        ajax_url = urljoin(response.url, ajax_url)
        end = body.find('jsModule:"z-hdp-price-history"')
        price_history_url = re.search(r'ajaxURL:"(.*?)",', body[end - 1000:end]).group(1)
        price_history_url = urljoin(response.url, price_history_url)
        form_title = response.xpath('//h2[@class="form-title"]/text()').extract_first()
        if form_title and 'Contact Listing Agent' in form_title:
            href = response.xpath('//span[@class="snl name notranslate"]/a/@href').extract_first()
            if href:
                return scrapy.Request(
                    urljoin(response.url, href),
                    self.parse_agent_profile,
                    dont_filter=True,
                    meta={'item': l.load_item(), 'ajax_url': ajax_url, 'price_history_url': price_history_url})
            else:
                return scrapy.Request(
                    ajax_url,
                    self.parse_listing_info,
                    meta={'item': l.load_item(), 'price_history_url': price_history_url})

        node = response.xpath('//span[@class="contact-badge Listing Agent"]')
        if node:
            href = node.xpath('./following-sibling::div//a[@class="profile-name-link"]/@href').extract_first()
            if href:
                return scrapy.Request(
                    urljoin(response.url, href),
                    self.parse_agent_profile,
                    dont_filter=True,
                    meta={'item': l.load_item(), 'ajax_url': ajax_url, 'price_history_url': price_history_url})
            else:
                return scrapy.Request(
                    ajax_url,
                    self.parse_listing_info,
                    meta={'item': l.load_item(), 'price_history_url': price_history_url})

        node = response.xpath('//span[@class="contact-badge Agent"]')
        if node:
            href = node.xpath('../div[2]//a[@class="profile-name-link"]/@href').extract_first()
            if href:
                return scrapy.Request(
                    urljoin(response.url, href),
                    self.parse_agent_profile,
                    dont_filter=True,
                    meta={'item': l.load_item(), 'ajax_url': ajax_url, 'price_history_url': price_history_url})
            else:
                return scrapy.Request(
                    ajax_url,
                    self.parse_listing_info,
                    meta={'item': l.load_item(), 'price_history_url': price_history_url})

        node = response.xpath('//span[contains(text(), "Premier Agent")]')
        if node:
            href = response.xpath('//a[@class="profile-img-link"]/@href').extract_first()
            if href:
                return scrapy.Request(
                    urljoin(response.url, href),
                    self.parse_agent_profile,
                    dont_filter=True,
                    meta={'item': l.load_item(), 'ajax_url': ajax_url, 'price_history_url': price_history_url})
            else:
                return scrapy.Request(
                    ajax_url,
                    self.parse_listing_info,
                    meta={'item': l.load_item(), 'price_history_url': price_history_url})

    def parse_agent_profile(self, response):
        self.logger.info('Crawled (%d) %s' % (response.status, response.url))
        title = response.xpath('//p[@id="profile-title"]/strong/text()').extract_first()
        if title and 'Broker' in title:
            l = BrokerLoader(item=ZillowBrokerItem(), response=response)
            l.add_value('originUrl', response.url)
            l.add_value('brokerTitle', title.strip())
            l.add_xpath('brokerName', '//span[@class="ctcd-user-name"]/text()')
            l.add_value('brokerMobile', response.meta['item']['agentMobile'])
            l.add_xpath('officeName', '//dd[contains(@class, "profile-information-address")]/text()')
            l.add_xpath('officePhone', '//dt[contains(text(), "Phone:")]/following-sibling::dd/text()')
            l.add_xpath('officeAddress', '//dd[contains(@class, "profile-information-address")]/span/text()')
            l.add_xpath('licenses', '//div[contains(@id, "license")]/ul/li/text()')
            return l.load_item()
        item = response.meta['item']
        item['agentName'] = response.xpath('//span[@class="ctcd-user-name"]/text()').extract_first()
        item['activeListings'] = response.xpath('//h2[@id="profile-active-listings"]/following-sibling::span/text()').re_first(r'(\d+)')
        item['salesLast12Months'] = response.xpath('//li[contains(@class, "ctcd-item_sales")]/text()').re_first(r'(\d+) Sale')
        return scrapy.Request(
            response.meta['ajax_url'],
            self.parse_listing_info,
            meta={'item': item, 'price_history_url': response.meta['price_history_url']})

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
        selector = Selector(text=data['html'])
        item['listingUpdated'] = to_datetime(selector.xpath('//table/tbody/tr[1]/td[1]/text()').extract_first())
        yield item

