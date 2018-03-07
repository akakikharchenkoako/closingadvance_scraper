# # -*- coding: utf-8 -*-

# from urllib.parse import urlencode

# import scrapy

# from closingadvance_scraper.items import Item
# from closingadvance_scraper.loaders import Loader
# from closingadvance_scraper.processors import serialize_number
# from closingadvance_scraper.locations import states


# class Century21Spider(scrapy.Spider):
#     name = 'century21'
#     allowed_domains = ['www.century21.com', 'www.realtor.com']
#     search_url = 'https://www.century21.com/propsearch-async?'
#     search_params = {
#         'lid': '',
#         'pr': '150000|550000',
#         'o': 'listingdate-desc',
#         'co': '1',
#         'sn': '5',
#         't': '0',
#         's': '0',
#         'r': '20',
#         'pt': '1',
#         'sk': 'Y',
#     }

#     def start_requests(self):
#         for location in states:
#             params = self.search_params.copy()
#             params['lid'] = 'S' + location['abbr']
#             yield scrapy.Request(self.search_url + urlencode(params), callback=self.parse, meta={'params': params})

#     def parse(self, response):
#         self.logger.info('Crawled (%d) %s' % (response.status, response.url))
#         for node in response.xpath('//div[contains(@class, "infinite-item property-card")]'):
#             if 'Sale Pending' in node.extract():
#                 for a in node.xpath('.//div[contains(@class, "property-card-primary-info")]/a'):
#                     yield response.follow(a, self.parse_item)

#         if 'No Results Found' not in response.body.decode():
#             params = response.meta['params']
#             params['s'] = str(int(params['s']) + 20)
#             yield scrapy.Request(self.search_url + urlencode(params), callback=self.parse, meta={'params': params})

#     def parse_item(self, response):
#         self.logger.info('Crawled (%d) %s' % (response.status, response.url))
#         l = Loader(item=Item(), response=response)
#         l.add_value('propertyUrl', response.url)
#         l.add_xpath('mlsId', '//div[contains(@class, "pdp-info-mls")]/text()')
#         l.add_xpath('price', '//meta[contains(@itemprop, "price")]/@content')
#         street = response.xpath('//div[contains(@itemprop, "streetAddress")]/text()').extract_first()
#         if not street:
#             street = response.xpath('//div[contains(@class, "info-address")]/text()').extract_first()
#         locality = response.xpath('//span[contains(@itemprop, "addressLocality")]/text()').extract_first()
#         region = response.xpath('//span[contains(@itemprop, "addressRegion")]/text()').extract_first()
#         postal = response.xpath('//span[contains(@itemprop, "postalCode")]/text()').extract_first()
#         l.add_value('propertyAddress', ', '.join([street.strip(), locality, region, postal]))
#         if postal:
#             l.add_value('zipCode', postal.strip())
#         else:
#             l.add_value('zipCode', street.strip().split()[-1])
#         l.add_xpath('brokerName', '//a[contains(@class, "officeName")]')
#         broker_address_street = response.xpath('//div[contains(@class, "contactAddress")]/text()').extract_first()
#         broker_address_city = response.xpath('//div[contains(@class, "contactLocation")]/text()').extract_first()
#         l.add_value('brokerAddress', ', '.join([broker_address_street.replace(',', ''), broker_address_city]))
#         l.add_xpath('agentName', '//a[contains(@class, "contactName")]/strong/text()')
#         agent_name = l.get_output_value('agentName')
#         if agent_name:
#             l.add_xpath('agentPhone', '//a[contains(@class, "phoneNumber")]/@href')
#             # Search agent on realtor.com
#             url = 'https://www.realtor.com/realestateagents/%s/agentname-%s' % (broker_address_city.split()[-1], '-'.join(agent_name.split()))
#             yield scrapy.Request(url, callback=self.parse_realtor_agent, meta={'item': l.load_item()}, dont_filter=True)
#         else:
#             l.add_xpath('brokerPhone', '//a[contains(@class, "phoneNumber")]/@href')
#         yield l.load_item()

#     def parse_realtor_agent(self, response):
#         self.logger.info('Crawled (%d) %s' % (response.status, response.url))
#         item = response.meta['item']
#         phone_number = response.xpath('//div[contains(@itemprop, "telephone")]/text()').extract_first()
#         if phone_number:
#             phone_number = serialize_number(phone_number)
#             if phone_number != item['agentPhone']:
#                 item['agentPhone2'] = phone_number
#         item['agentSelling'] = response.xpath('//div[contains(text(), "For Sale")]/a/strong/text()').extract_first()
#         item['agentSold'] = response.xpath('//div[contains(text(), "Sold")]/a/strong/text()').extract_first()
#         return item
