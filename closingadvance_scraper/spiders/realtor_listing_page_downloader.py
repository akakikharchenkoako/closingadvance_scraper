# -*- coding: utf-8 -*-

import logging
import scrapy
import json
import os
import re
from random import shuffle


logger = logging.getLogger('peewee')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


class RealtorListingFromQualifiedUrlsSpider(scrapy.Spider):
    handle_httpstatus_list = [400, 404, 503, 500]
    name = 'realtor_listing_page_downloader'
    base_url = "https://www.realtor.com"
    allowed_domains = ['www.realtor.com']

    def start_requests(self):
        with open(os.path.dirname(os.path.realpath(__file__)) + "/../external_data/output/failure_list.csv", "w") as output_file:
                output_file.write("")

        output_file.close()
        listing_urls_list = []

        with open(os.path.dirname(os.path.realpath(__file__)) + "/../external_data/output/qualified_realtor_sold_listings.csv") as f:
            for line in f:
                listing_urls_list.append(line.strip())

        shuffle(listing_urls_list)

        headers = {}
        headers['User-Agent'] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
        headers['Content-Type'] = "application/json"

        for listing_url in listing_urls_list:
            payload = {"headers": {}, "method": "GET", "url": listing_url}
            yield scrapy.Request("http://127.0.0.1:22999/api/test/24000",
                                 method="POST",
                                 headers=headers,
                                 body=json.dumps(payload),
                                 callback=self.parse_listing)

    def parse_listing(self, response):
        self.logger.info('Crawled (%d) %s' % (response.status, response.url))

        if response.status == 200:
            try:
                listing_id = re.findall(re.compile(r'"property_id":(.*?),', flags=re.DOTALL), response.text)[0].strip()
                if listing_id:
                    with open(os.path.dirname(os.path.realpath(__file__)) + "/../external_data/output/listing_pages/{0}.html".format(listing_id), "w") as listing_file:
                        listing_file.write(response.text)
            except Exception as e:
                with open(os.path.dirname(os.path.realpath(__file__)) + "/../external_data/output/failure_list.csv",
                          "a") as output_file:
                    output_file.write(response.url + "\n")
