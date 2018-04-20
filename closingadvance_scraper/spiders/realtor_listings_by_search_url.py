# -*- coding: utf-8 -*-

import logging
import scrapy
import os
import json

logger = logging.getLogger('peewee')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


class RealtorListingsBySearchUrl(scrapy.Spider):
    name = 'realtor_listings_by_search_url_spider'
    allowed_domains = ['www.realtor.com']
    search_controller = "Search::RecentlySoldController"
    search_criteria = "New-York_NY/type-single-family-home"
    pagination_url = 'https://www.realtor.com/pagination_result'
    handle_httpstatus_list = [400, 404]

    def start_requests(self):
        meta_dict = {}

        with open(os.path.dirname(os.path.realpath(__file__)) + "/../external_data/output/realtor_listing_urls.csv", "w") as output_file:
                output_file.write("")

        output_file.close()

        if True:
            post_params = {}
            post_params["city"] = "Las Vegas"
            post_params["county"] = "Clark"
            post_params["discovery_mode"] = False
            post_params["facets"] = {}
            if True:
                post_params["facets"]["acre_max"] = None
                post_params["facets"]["age_max"] = None
                post_params["facets"]["age_min"] = None
                post_params["facets"]["baths_max"] = None
                post_params["facets"]["baths_min"] = None
                post_params["facets"]["beds_max"] = None
                post_params["facets"]["beds_min"] = None
                post_params["facets"]["days_on_market"] = ""
                post_params["facets"]["features_hash"] = []
                post_params["facets"]["foreclosure"] = None
                post_params["facets"]["include_pending_contingency"] = False
                post_params["facets"]["lot_unit"] = None
                post_params["facets"]["multi_search"] = {}
                post_params["facets"]["new_construction"] = None
                post_params["facets"]["open_house"] = None
                post_params["facets"]["pending"] = None
                post_params["facets"]["pets"] = []
                post_params["facets"]["prop_type"] = "single-family-home"
                post_params["facets"]["radius"] = None
                post_params["facets"]["show_listings"] = ""
                post_params["facets"]["sqft_max"] = None
                post_params["facets"]["sqft_min"] = None
            post_params["neighborhood"] = None
            post_params["page"] = 1
            post_params["page_size"] = 15
            post_params["pin_height"] = 25
            post_params["pos"] = None
            post_params["position"] = None
            post_params["postal"] = None
            post_params["school"] = None
            post_params["searchFacetsToDTM"] = ["prop_type"]
            post_params["searchFeaturesToDTM"] = []
            post_params["searchType"] = "city"
            post_params["search_controller"] = self.search_controller
            post_params["search_criteria"] = self.search_criteria
            post_params["sort"] = None
            post_params["state"] = "NV"
            post_params["street"] = None
            post_params["types"] = ["property"]
            post_params["viewport_height"] = 442

        meta_dict["post_params"] = post_params

        yield scrapy.Request(self.pagination_url,
                             method="POST",
                             body=json.dumps(meta_dict["post_params"]),
                             callback=self.parse,
                             headers={'Content-Type': 'application/json',
                                      'X-Crawlera-Profile': 'desktop'},
                             meta=meta_dict)

    def parse(self, response):
        self.logger.info('Crawled (%d) %s' % (response.status, response.url))

        sub_urls = response.xpath('//ul[contains(@class, "srp-list-marginless list-unstyled")]/li/@data-url').extract()
        property_urls = ["https://www.realtor.com" + url for url in sub_urls]

        with open(os.path.dirname(os.path.realpath(__file__)) + "/../external_data/output/realtor_listing_urls.csv", "a") as output_file:
            for url in property_urls:
                output_file.write(url + "\n")

        output_file.close()

        page_number = response.xpath('//span[@class="page current"]/text()').extract_first()
        page_number = page_number.strip() if page_number else None

        print(page_number)
        print(len(property_urls))
        print(response.meta["post_params"]["search_criteria"])

        if "retry" in response.meta:
            print("-----retry " + str(response.meta["retry"]))

        if not page_number or (page_number and int(page_number) != response.meta["post_params"]["page"]):
            if "retry" in response.meta:
                if response.meta["retry"] > 0:
                    response.meta["retry"] = response.meta["retry"] - 1
                else:
                    return
            else:
                response.meta["retry"] = 5
        else:
            if "retry" in response.meta:
                response.meta.pop('retry', None)

        if "retry" not in response.meta:
            response.meta["post_params"]["search_criteria"] = self.search_criteria + "/pg-" + str(response.meta["post_params"]["page"])
            response.meta["post_params"]["page"] = response.meta["post_params"]["page"] + 1

        yield scrapy.Request(self.pagination_url,
                             method="POST",
                             body=json.dumps(response.meta["post_params"]),
                             callback=self.parse,
                             headers={'Content-Type': 'application/json', 'X-Crawlera-Profile': 'desktop'},
                             dont_filter=True,
                             meta=response.meta)
