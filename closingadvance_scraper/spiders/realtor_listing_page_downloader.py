# -*- coding: utf-8 -*-

import logging
import scrapy
import csv
import os
import json
import re
from closingadvance_scraper.locations import states
from closingadvance_scraper.items import RealtorListingForJulienItem
from closingadvance_scraper.loaders import RealtorListingJulienLoader
from closingadvance_scraper.processors import to_datetime


logger = logging.getLogger('peewee')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())
from closingadvance_scraper.models import *


class RealtorListingFromQualifiedUrlsSpider(scrapy.Spider):
    handle_httpstatus_list = [400, 404, 503, 500]
    name = 'realtor_listing_page_downloader'
    base_url = "https://www.realtor.com"
    allowed_domains = ['www.realtor.com']

    def start_requests(self):
        with open(os.path.dirname(os.path.realpath(__file__)) + "/../external_data/output/failure_list.csv", "w") as output_file:
                output_file.write("")

        output_file.close()

        with open(os.path.dirname(os.path.realpath(__file__)) + "/../external_data/output/realtor_listing_urls.csv") as f:
            for line in f:
                yield scrapy.Request(line.strip(),
                                     callback=self.parse_listing,
                                     headers={'X-Crawlera-Profile': 'desktop'})

    def parse_listing(self, response):
        self.logger.info('Crawled (%d) %s' % (response.status, response.url))

        if response.status == 200:
            try:
                listing_id = re.findall(re.compile(r'"listing_id":(.*?),', flags=re.DOTALL), response.text)[0].strip()
                if listing_id:
                    with open(os.path.dirname(os.path.realpath(__file__)) + "/../external_data/output/listing_pages/{0}.html".format(listing_id), "w") as listing_file:
                        listing_file.write(response.text)
            except Exception as e:
                with open(os.path.dirname(os.path.realpath(__file__)) + "/../external_data/output/failure_list.csv",
                          "a") as output_file:
                    output_file.write(response.url + "\n")

