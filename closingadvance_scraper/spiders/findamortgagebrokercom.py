# -*- coding: utf-8 -*-

from urllib.parse import urljoin

import scrapy
import zipcodes
import csv
import re
import os


class FindAMortgageBrokerComSpider(scrapy.Spider):
    name = 'findamortgagebroker'
    allowed_domains = ['findamortgagebroker.com']
    search_url = 'https://findamortgagebroker.com/Search/FuzzySearch'

    def start_requests(self):
        with open(os.path.dirname(os.path.realpath(__file__)) + "/../external_data/output/findamortgagebrokercom.csv", 'w') as csvfile:
            fieldnames = ['Organization',
                          'Full Name',
                          'Zipcode',
                          'Address',
                          'Email',
                          'NMLS',
                          'Website',
                          'Phone']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

        for zipcode in zipcodes.filter_by(zipcodes.list_all(), active=True):
            formData = {"Criteria": zipcode['zip_code']}
            print(zipcode['zip_code'])
            yield scrapy.FormRequest(self.search_url, callback=self.parse, formdata=formData)

    def parse(self, response):
        # self.logger.info('Crawled (%d) %s' % (response.status, response.url))

        with open(os.path.dirname(os.path.realpath(__file__)) + "/../external_data/output/findamortgagebrokercom.csv", 'w') as csvfile:
            fieldnames = ['Organization',
                          'Full Name',
                          'Zipcode',
                          'Address',
                          'Email',
                          'NMLS',
                          'Website',
                          'Phone']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            for broker_node in response.xpath('//div[@class="search-results vcard"]'):
                try:
                    organization = broker_node.xpath('.//h2[@class="org"]/text()').extract_first()
                    family_name = broker_node.xpath('.//h3[@class="n"]//text()').extract()
                    family_name = [sub_name for sub_name in family_name if sub_name.strip()]
                    family_name = ' ' . join(family_name)
                    zipcode = broker_node.xpath('.//span[@class="postal-code"]/text()').extract_first()
                    address = broker_node.xpath('.//div[@class="adr"]//text()').extract()
                    address = [sub_address for sub_address in address if sub_address.strip()]
                    address = (' ' . join(address)).strip()
                    email = broker_node.xpath('.//span[@class="email"]/text()').extract_first()
                    nmls = broker_node.xpath('.//a[@class="nmls"]//text()').extract_first()
                    nmls = re.sub("[^\d\.]", "", nmls) if nmls else None
                    website = broker_node.xpath('.//div[@class="broker-site"]//span[@class="url"]/text()').extract_first()
                    phone = broker_node.xpath('.//div[@class="broker-phone"]//span[@class="tel"]/text()').extract_first()
                    phone = re.sub("[^\d\.]", "", phone) if phone else None
                    brokerInfo = {'Organization': organization,
                                  'Full Name': family_name,
                                  'Zipcode': zipcode,
                                  'Address': address,
                                  'Email': email,
                                  'NMLS': nmls,
                                  'Website': website,
                                  'Phone': phone}
                    writer.writerow(brokerInfo)
                except Exception as e:
                    print(e)
