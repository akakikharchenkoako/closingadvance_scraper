# -*- coding: utf-8 -*-

import re
import scrapy

from closingadvance_scraper.models import Agent


class TruliaAgentSpider(scrapy.Spider):
    name = 'trulia_agent'
    allowed_domains = ['www.trulia.com']
    search_url = 'https://www.trulia.com/directory/{}-agent-{}/'
    count = 0

    def start_requests(self):
        for row in Agent.select(Agent.originUrl, Agent.agentName).where(Agent.forSale >= 1, ~(Agent.originUrl.contains('%_CA%')), ~(Agent.originUrl.contains('%_NY%')), ~(Agent.originUrl.contains('%_OH%')), ~(Agent.originUrl.contains('%_AK%')), ~(Agent.originUrl.contains('%_MA%')), ~(Agent.originUrl.contains('%_MD%')), Agent.agentMobile.is_null()):
            self.logger.info(row.originUrl)
            try:
                city = re.search(r'_(.+)_[A-Z]{2}', row.originUrl).group(1)
            except AttributeError:
                city = ''
            url = self.search_url.format(city, '+'.join(row.agentName.split()))
            yield scrapy.Request(url, callback=self.parse, meta={'originUrl': row.originUrl, 'agentName': row.agentName})

    def parse(self, response):
        self.logger.info('Crawled (%d) %s' % (response.status, response.url))
        for node in response.xpath('//h5[contains(@class, "agent_name_link")]'):
            agent_name = node.xpath('./a[contains(@onclick, "AgentName_link")]/text()').extract_first()
            # self.logger.info(agent_name)
            # self.logger.info(response.meta['agentName'])
            names = agent_name.strip().split()
            match = True
            for name in names:
                if name.lower() not in response.meta['agentName'].lower():
                    match = False
                    break
            if match:
                self.count += 1
                self.logger.info('Count %d' % self.count)
                self.logger.info('Found %s' % response.meta['agentName'])
                self.logger.info('originUrl %s' % response.meta['originUrl'])
                self.logger.info('Trulia URL %s' % response.url)

