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
    handle_httpstatus_list = [404, 500]
    name = 'realtor_listing_from_qualified_urls_spider'
    allowed_domains = ['www.realtor.com']
    listingStatus = ['Active', 'Contingent', 'For Sale', 'New', 'Pending', 'Sold', 'Under Contract']
    statesAbbrList = [state['abbr'] for state in states]

    def start_requests(self):
        self.listingStatus = [user._data['status'] for user in ListingStatus.select()]

        with open(os.path.dirname(os.path.realpath(__file__)) + "/../external_data/output/200_list.csv", "w") as output_file:
                output_file.write("")

        output_file.close()

        with open(os.path.dirname(os.path.realpath(__file__)) + "/../external_data/output/404_list.csv", "w") as output_file:
                output_file.write("")

        output_file.close()

        with open(os.path.dirname(os.path.realpath(__file__)) + "/../external_data/output/realtor_listing_urls.csv") as f:
            for line in f:
                yield scrapy.Request(line.strip(),
                                     callback=self.parse_listing,
                                     headers={'X-Crawlera-Profile': 'desktop'})

    def parse_listing(self, response):
        if response.status == 200:
            with open(os.path.dirname(os.path.realpath(__file__)) + "/../external_data/output/200_list.csv", "a") as output_file:
                output_file.write(response.url + "\n")
        else:
            with open(os.path.dirname(os.path.realpath(__file__)) + "/../external_data/output/404_list.csv",
                      "a") as output_file:
                output_file.write(response.url + "\n")

