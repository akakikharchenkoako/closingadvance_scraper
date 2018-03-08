# -*- coding: utf-8 -*-

import re
import scrapy
import zipcodes

from closingadvance_scraper.models import RealtorAgent
from closingadvance_scraper.items import AgentItem, BrokerItem
from closingadvance_scraper.loaders import AgentLoader, BrokerLoader


class RealtorAgentSpider(scrapy.Spider):
    name = 'realtor_agent'
    allowed_domains = ['www.realtor.com']
    search_url = 'https://www.realtor.com/realestateagents/{}'

    def start_requests(self):
        for zipcode in zipcodes.list_all()[:1]:
            url = self.search_url.format(zipcode['zip_code'])
            yield scrapy.Request(url, callback=self.parse)

    # def parse(self, response):
    #     self.logger.info('Crawled (%d) %s' % (response.status, response.url))
    #
    #     for a in response.xpath('//div[@class="agent-name text-bold"]/a'):
    #         yield response.follow(a, self.parse_item)
    #
    #     for a in response.xpath('//nav[@class="pagination"]//a'):
    #         yield response.follow(a, self.parse)

    # def start_requests(self):
    #     for row in RealtorAgent.select(RealtorAgent.agentUrl):
    #         yield scrapy.Request(row.agentUrl, callback=self.parse)

    def parse(self, response):
        self.logger.info('Crawled (%d) %s' % (response.status, response.url))
        designation = response.xpath('//div[@class="agent-name text-bold" and @itemprop="name"]/a/text()').extract_first()
        if ' - ' in designation:
            designation = re.search(r' \- (.+)', designation).group(1)
        elif ', ' in designation:
            designation = re.search(r'\, (.+)', designation).group(1)
        elif ' | ' in designation:
            designation = re.search(r' \| (.+)', designation).group(1)
#        else:
#            designation = None
        designation = designation.strip() if designation else None
        broker_indicators = ['Broker', 'CEO', 'Owner', 'President', 'Chairman']
        is_broker = False
        if designation:
            for indicator in broker_indicators:
                if indicator.lower() in designation.lower():
                    is_broker = True
                    break
        if is_broker:
            l = BrokerLoader(item=BrokerItem(), response=response)
            l.add_value('originUrl', response.url)
            l.add_value('brokerType', designation)
            broker_name = response.xpath('//span[@class="agent-name"]/text()').extract_first()
            if ' - ' in broker_name:
                l.add_xpath('brokerName', '//span[@class="agent-name"]/text()', re=r'^(.*?)-')
            elif ', ' in broker_name:
                l.add_xpath('brokerName', '//span[@class="agent-name"]/text()', re=r'^(.*?),')
            if ' | ' in broker_name:
                l.add_xpath('brokerName', '//span[@class="agent-name"]/text()', re=r'^(.*?)\|')
            if not l.get_output_value('brokerName'):
                l.add_xpath('brokerName', '//span[@class="agent-name"]/text()')
            l.add_xpath('brokerMobile', '//div[@class="sticky-agent-info"]/text()')
            l.add_xpath('officeName', '//div[@id="popoverBrokerage"]//h4/text()')
            l.add_xpath('officePhone', '//div[@id="popoverBrokerage"]//li[contains(span/@class, "fa-phone")]/text()')
            if not l.get_output_value('officePhone'):
                for node in response.xpath('//li/i[contains(@class, "fa-phone")]/..'):
                    if 'Office:' in node.extract() or 'Fax:' in node.extract():
                        l.add_value('officePhone', node.xpath('./a/span/text()').extract_first())
                        break
            l.add_xpath('officeAddress', '//div[@id="popoverBrokerage"]//li[contains(span/@class, "fa-map-marker")]/text()')
            if not l.get_output_value('officeAddress'):
                l.add_xpath('officeAddress', '//span[@itemprop="streetAddress"]/text()')
            yield l.load_item()
        else:
            l = AgentLoader(item=AgentItem(), response=response)
            l.add_value('originUrl', response.url)
            l.add_value('designation', designation)
            agent_name = response.xpath('//span[@class="agent-name"]/text()').extract_first()
            if ' - ' in agent_name:
                l.add_xpath('agentName', '//span[@class="agent-name"]/text()', re=r'^(.*?)-')
            elif ', ' in agent_name:
                l.add_xpath('agentName', '//span[@class="agent-name"]/text()', re=r'^(.*?),')
            if ' | ' in agent_name:
                l.add_xpath('agentName', '//span[@class="agent-name"]/text()', re=r'^(.*?)\|')
            if not l.get_output_value('agentName'):
                l.add_xpath('agentName', '//span[@class="agent-name"]/text()')
            for node in response.xpath('//li/i[contains(@class, "fa-phone")]/..'):
                if 'Mobile:' in node.extract():
                    l.add_value('agentMobile', node.xpath('./a/span/text()').extract_first())
                    break
            l.add_xpath('forSale', '//a[@data-nav-type="for_sale"]/@data-nav-count')
            l.add_xpath('openHouse', '//a[@data-nav-type="open_house_all"]/@data-nav-count')
            l.add_xpath('recentlySold', '//a[@data-nav-type="recently_sold"]/@data-nav-count')
            l.add_xpath('officeName', '//div[@id="popoverBrokerage"]//h4/text()')
            l.add_xpath('officePhone', '//div[@id="popoverBrokerage"]//li[contains(span/@class, "fa-phone")]/text()')
            if not l.get_output_value('officePhone'):
                for node in response.xpath('//li/i[contains(@class, "fa-phone")]/..'):
                    if 'Office:' in node.extract() or 'Fax:' in node.extract():
                        l.add_value('officePhone', node.xpath('./a/span/text()').extract_first())
                        break
            l.add_xpath('officeAddress', '//div[@id="popoverBrokerage"]//li[contains(span/@class, "fa-map-marker")]/text()')
            if not l.get_output_value('officeAddress'):
                l.add_xpath('officeAddress', '//span[@itemprop="streetAddress"]/text()')
            yield l.load_item()
