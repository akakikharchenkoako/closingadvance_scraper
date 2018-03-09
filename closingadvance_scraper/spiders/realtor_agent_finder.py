# -*- coding: utf-8 -*-

from urllib.parse import urljoin

import scrapy
import zipcodes
import re
from closingadvance_scraper.locations import states
from closingadvance_scraper.items import RealtorAgentItem, RealtorBrokerItem
from closingadvance_scraper.loaders import AgentLoader, RealtorBrokerLoader


class RealtorAgentFinderSpider(scrapy.Spider):
    name = 'realtor_agent_finder'
    allowed_domains = ['www.realtor.com']
    search_url = 'https://www.realtor.com/realestateteam/teamname-{}'

    def start_requests(self):
        """
        yield scrapy.Request('https://www.realtor.com/realestateteam/89138', callback=self.parse, meta={'search_keyword': '89138'})
        target_states = [state['abbr'] for state in states]
        for zipcode in zipcodes.filter_by(zipcodes.list_all(), active=True):
            if zipcode['state'] in target_states:
                url = self.search_url.format(zipcode['city'], zipcode['state'], zipcode['zip_code'])
                yield scrapy.Request(url, callback=self.parse)

        for zipcode in zipcodes.filter_by(zipcodes.list_all(), active=True):
            url = self.search_url.format(zipcode['zip_code'])
            yield scrapy.Request(url, callback=self.parse, meta={'search_keyword': zipcode['zip_code']})
        """
        import string

        for alphabet in list(string.ascii_lowercase):
            url = self.search_url.format(alphabet)
            yield scrapy.Request(url, callback=self.parse, meta={'search_keyword': alphabet})

    def parse(self, response):
        # self.logger.info('Crawled (%d) %s' % (response.status, response.url))

        for agent_node in response.xpath('//div[@id="agent_list_wrapper"]/div'):
            yield response.follow(agent_node.xpath('./@data-url').extract_first(), self.parse_team, meta={'search_keyword': response.meta.get('search_keyword')})

        if response.xpath('//nav[@class="pagination"]/span[@class="next"]/a[@class="next"]/@href').extract_first():
            yield scrapy.Request(response.xpath('//nav[@class="pagination"]/span[@class="next"]'
                                                '/a[@class="next"]/@href').extract_first(),
                                 self.parse, meta={'dont_cache': True, 'search_keyword': response.meta.get('search_keyword')})

    def parse_team(self, response):
        # self.logger.info('Crawled (%d) %s' % (response.status, response.url))

        for agent_profile_link in response.xpath('//div[@id="teams-section"]//div[@class="agent-simple-card"]/a'):
            yield response.follow(agent_profile_link.xpath('./@href').extract_first(),
                                  self.parse_agent_profile, meta={'teamUrl': response.url, 'search_keyword': response.meta.get('search_keyword')})

    def parse_agent_profile(self, response):
        # self.logger.info('Crawled (%d) %s' % (response.status, response.url))

        contact_info_block = response.xpath("//div[@id='modalcontactInfo']")
        designation = contact_info_block.xpath(".//p[@class='modal-agent-name']/text()").extract_first()

        if not designation:
            designation = response.xpath('//div[@id="button_group_coverwrap"]//h1[@class="profile-name"]'
                                         '/span[@class="agent-name"]/text()').extract_first()

        print(designation)

        designation = designation.strip() if designation else None
        full_name = designation

        is_broker = False

        if designation:
            if ' - ' in designation:
                full_name = re.search(r'^(.*?)-', full_name).group(1)
                designation = re.search(r' \- (.+)', designation).group(1)
            elif ', ' in designation:
                full_name = re.search(r'^(.*?),', full_name).group(1)
                designation = re.search(r'\, (.+)', designation).group(1)
            elif ' | ' in designation:
                full_name = re.search(r'^(.*?)\|', full_name).group(1)
                designation = re.search(r' \| (.+)', designation).group(1)

            full_name = full_name.strip()
            designation = designation.strip()

            broker_indicators = ['Broker', 'CEO', 'Owner', 'President', 'Chairman', 'Principal']

            if ('-' . join(full_name.split(' '))).lower() in response.meta['teamUrl'].lower():
                is_broker = True
            else:
                for indicator in broker_indicators:
                    if indicator.lower() in designation.lower():
                        is_broker = True
                        break
        try:
            if is_broker:
                l = RealtorBrokerLoader(item=RealtorBrokerItem(), response=response)
                l.add_value('teamUrl', response.meta.get('teamUrl'))
                l.add_value('originUrl', response.url)
                l.add_value('brokerTitle', designation)
                l.add_value('search_keyword', response.meta.get('search_keyword'))
                l.add_value('brokerName', full_name)
                l.add_xpath('officeName', '//div[@id="popoverBrokerage"]//h4/text()')

                mobileIndex = 1

                for node in response.xpath('//div[@id="modalcontactInfo"]//li/i[contains(@class, "fa-phone")]/..'):
                    if 'Office:' in node.extract():
                        l.add_value('officePhone', node.xpath('./a/span/text()').extract_first())
                        continue

                    if 'Mobile:' in node.extract():
                        if mobileIndex == 1:
                            l.add_value('brokerMobile', node.xpath('./a/span/text()').extract_first())
                        else:
                            l.add_value('brokerMobile{0}'.format(mobileIndex), node.xpath('./a/span/text()').extract_first())

                        mobileIndex += 1

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
                l.add_value('search_keyword', response.meta.get('search_keyword'))
                l.add_value('agentName', full_name)

                for node in response.xpath('//div[@id="modalcontactInfo"]//li/i[contains(@class, "fa-phone")]/..'):
                    if 'Office:' in node.extract():
                        l.add_value('officePhone', node.xpath('./a/span/text()').extract_first())
                        continue

                    if 'Mobile:' in node.extract():
                        l.add_value('agentMobile', node.xpath('./a/span/text()').extract_first())

                l.add_xpath('officeName', '//div[@id="popoverBrokerage"]//h4/text()')
                l.add_xpath('officeAddress',
                            '//div[@id="modalcontactInfo"]//span[@itemprop="streetAddress"]/text()')

                l.add_xpath('forSale', '//a[@data-nav-type="for_sale"]/@data-nav-count')
                l.add_xpath('recentlySold', '//a[@data-nav-type="recently_sold"]/@data-nav-count')

                yield l.load_item()
        except Exception as e:
            print(e)
