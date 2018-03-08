# -*- coding: utf-8 -*-

from urllib.parse import urljoin

import scrapy
import zipcodes
import re
from closingadvance_scraper.locations import states
from closingadvance_scraper.items import RealtorAgentItem, RealtorBrokerItem
from closingadvance_scraper.loaders import AgentLoader, BrokerLoader


class RealtorAgentFinderSpider(scrapy.Spider):
    name = 'realtor_agent_finder'
    allowed_domains = ['www.realtor.com']
    search_url = 'https://www.realtor.com/realestateteam/{}'

    def start_requests(self):
        yield scrapy.Request('https://www.realtor.com/realestateteam/89109', callback=self.parse)
        '''
        for zipcode in zipcodes.list_all()[:100]:
            url = self.search_url.format(zipcode['zip_code'])
            yield scrapy.Request(url, callback=self.parse)
        '''

    def parse(self, response):
        self.logger.info('Crawled (%d) %s' % (response.status, response.url))

        for agent_node in response.xpath('//div[@id="agent_list_wrapper"]/div'):
            yield response.follow(agent_node.xpath('./@data-url').extract_first(), self.parse_team)

        if response.xpath('//nav[@class="pagination"]/span[@class="next"]/a[@class="next"]/@href').extract_first():
            yield scrapy.Request(response.xpath('//nav[@class="pagination"]/span[@class="next"]'
                                                '/a[@class="next"]/@href').extract_first(),
                                 self.parse, meta={'dont_cache': True})

    def parse_team(self, response):
        self.logger.info('Crawled (%d) %s' % (response.status, response.url))

        for agent_profile_link in response.xpath('//div[@id="teams-section"]//div[@class="agent-simple-card"]/a'):
            yield response.follow(agent_profile_link.xpath('./@href').extract_first(),
                                  self.parse_agent_profile, meta={'teamUrl': response.url})

    def parse_agent_profile(self, response):
        self.logger.info('Crawled (%d) %s' % (response.status, response.url))

        contact_info_block = response.xpath("//div[@id='modalcontactInfo']")
        designation = contact_info_block.xpath(".//p[@class='modal-agent-name']/text()").extract_first()

        if not designation:
            designation = response.xpath('//div[@id="button_group_coverwrap"]//h1[@class="profile-name"]'
                                         '/span[@class="agent-name"]/text()').extract_first()

        print(designation)

        designation = designation.strip() if designation else None

        if designation:
            if ' - ' in designation:
                designation = re.search(r' \- (.+)', designation).group(1)
            elif ', ' in designation:
                designation = re.search(r'\, (.+)', designation).group(1)
            elif ' | ' in designation:
                designation = re.search(r' \| (.+)', designation).group(1)

            broker_indicators = ['Broker', 'CEO', 'Owner', 'President', 'Chairman', 'Principal']
            is_broker = False

            for indicator in broker_indicators:
                if indicator.lower() in designation.lower():
                    is_broker = True
                    break
        try:
            if is_broker:
                l = BrokerLoader(item=RealtorBrokerItem(), response=response)
                l.add_value('teamUrl', response.meta.get('teamUrl'))
                l.add_value('originUrl', response.url)
                l.add_value('brokerTitle', designation)
                broker_name = contact_info_block.xpath(".//p[@class='modal-agent-name']/text()").extract_first()

                if ' - ' in broker_name:
                    l.add_xpath('brokerName',
                                "//div[@id='modalcontactInfo']//p[@class='modal-agent-name']/text()",
                                re=r'^(.*?)-')
                elif ', ' in broker_name:
                    l.add_xpath('brokerName',
                                "//div[@id='modalcontactInfo']//p[@class='modal-agent-name']/text()",
                                re=r'^(.*?),')
                elif ' | ' in broker_name:
                    l.add_xpath('brokerName',
                                "//div[@id='modalcontactInfo']//p[@class='modal-agent-name']/text()",
                                re=r'^(.*?)\|')

                if not l.get_output_value('brokerName'):
                    l.add_xpath('brokerName', "//div[@id='modalcontactInfo']//p[@class='modal-agent-name']/text()")

                l.add_xpath('officeName', '//div[@id="popoverBrokerage"]//h4/text()')

                for node in response.xpath('//div[@id="modalcontactInfo"]//li/i[contains(@class, "fa-phone")]/..'):
                    if 'Office:' in node.extract() or 'Fax:' in node.extract():
                        l.add_value('officePhone', node.xpath('./a/span/text()').extract_first())
                        continue

                    if 'Mobile:' in node.extract():
                        l.add_value('brokerMobile', node.xpath('./a/span/text()').extract_first())

                l.add_xpath('officeAddress', '//div[@id="popoverBrokerage"]//li[contains(span/@class, "fa-map-marker")]/text()')

                if not l.get_output_value('officeAddress'):
                    l.add_xpath('officeAddress', '//span[@itemprop="streetAddress"]/text()')

                yield l.load_item()
            else:
                l = AgentLoader(item=RealtorAgentItem(), response=response)
                l.add_value('teamUrl', response.meta.get('teamUrl'))
                l.add_value('brokerUrl', response.meta.get('teamUrl'))
                l.add_value('originUrl', response.url)
                l.add_value('designation', designation)

                agent_name = contact_info_block.xpath(".//p[@class='modal-agent-name']/text()").extract_first()

                if ' - ' in agent_name:
                    l.add_xpath('agentName',
                                "//div[@id='modalcontactInfo']//p[@class='modal-agent-name']/text()",
                                re=r'^(.*?)-')
                elif ', ' in agent_name:
                    l.add_xpath('agentName',
                                "//div[@id='modalcontactInfo']//p[@class='modal-agent-name']/text()",
                                re=r'^(.*?),')
                elif ' | ' in agent_name:
                    l.add_xpath('agentName',
                                "//div[@id='modalcontactInfo']//p[@class='modal-agent-name']/text()",
                                re=r'^(.*?)\|')

                if not l.get_output_value('agentName'):
                    l.add_xpath('agentName', "//div[@id='modalcontactInfo']//p[@class='modal-agent-name']/text()")

                for node in response.xpath('//div[@id="modalcontactInfo"]//li/i[contains(@class, "fa-phone")]/..'):
                    if 'Office:' in node.extract() or 'Fax:' in node.extract():
                        l.add_value('officePhone', node.xpath('./a/span/text()').extract_first())
                        continue

                    if 'Mobile:' in node.extract():
                        l.add_value('agentMobile', node.xpath('./a/span/text()').extract_first())

                l.add_xpath('officeName', '//div[@id="popoverBrokerage"]//h4/text()')
                l.add_xpath('officeAddress',
                            '//div[@id="modalcontactInfo"]//span[@itemprop="streetAddress"]/text()')

                '''
                l.add_xpath('forSale', '//a[@data-nav-type="for_sale"]/@data-nav-count')
                l.add_xpath('openHouse', '//a[@data-nav-type="open_house_all"]/@data-nav-count')
                l.add_xpath('recentlySold', '//a[@data-nav-type="recently_sold"]/@data-nav-count')
                l.add_xpath('officePhone', '//div[@id="popoverBrokerage"]//li[contains(span/@class, "fa-phone")]/text()')

                if not l.get_output_value('officePhone'):
                    for node in response.xpath('//li/i[contains(@class, "fa-phone")]/..'):
                        if 'Office:' in node.extract() or 'Fax:' in node.extract():
                            l.add_value('officePhone', node.xpath('./a/span/text()').extract_first())
                            break                
                '''

                yield l.load_item()
        except Exception as e:
            print(e)
