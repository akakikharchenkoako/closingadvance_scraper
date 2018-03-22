# -*- coding: utf-8 -*-

import logging
import scrapy
import csv
import os
import json
from closingadvance_scraper.locations import states


logger = logging.getLogger('peewee')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


class ZillowLendersAllSpider(scrapy.Spider):
    name = 'zillow_lenders_all'
    allowed_domains = ['www.zillow.com']
    start_url = 'https://mortgageapi.zillow.com/getNearbyCities?partnerId=RD-CZMBMCZ&stateAbbreviation={0}&count={1}'
    lenders_url_by_city = 'https://mortgageapi.zillow.com/getLenderDirectoryListings?partnerId=RD-JGLGMSG'
    lender_profile_url = 'https://mortgageapi.zillow.com/getRegisteredLender?partnerId=RD-CZMBMCZ'
    pageSize = 20
    id_list = []
    # scraping fields
    # first_name, last_name, mls_number, mobile_phone, office_phone, email

    def start_requests(self):
        target_states = [state['abbr'] for state in states]

        for state_abbr in target_states[:1]:
            yield scrapy.Request(self.start_url.format(state_abbr, 1000), callback=self.parse_state_cities_json)

    def parse_state_cities_json(self, response):
        self.logger.info('Crawled (%d) %s' % (response.status, response.url))

        cities_list = json.loads(response.text)["cityNames"]

        for city in cities_list[:1]:
            payload = {
                'fields': ['screenName'],
                'location': city,
                'page': 1,
                'pageSize': self.pageSize,
                'sort': 'Relevance'
            }

            yield scrapy.Request(
                self.lenders_url_by_city, method='POST',
                callback=self.parse_lenders_list,
                body=json.dumps(payload),
                headers={'Content-Type': 'application/json'},
                meta={'payload': payload},
                dont_filter=True)

    def parse_lenders_list(self, response):
        self.logger.info('Crawled (%d) %s' % (response.status, response.url))

        total_lenders = json.loads(response.text)["totalLenders"]

        payload_from_response = response.meta['payload']

        lenders_list = json.loads(response.text)["lenders"]

        for lender in lenders_list:
            payload = {"fields": ["aboutMe",
                                  "address",
                                  "cellPhone",
                                  "contactLenderFormDisclaimer",
                                  "companyName",
                                  "employerScreenName",
                                  "equalHousingLogo",
                                  "faxPhone",
                                  "imageId",
                                  "individualName",
                                  "languagesSpoken",
                                  "memberFDIC",
                                  "nationallyRegistered",
                                  "nmlsId",
                                  "nmlsType",
                                  "officePhone",
                                  "rating",
                                  "screenName",
                                  "stateLicenses",
                                  "stateSponsorships",
                                  "title",
                                  "totalReviews",
                                  "website"],
                       "lenderRef": {"screenName": lender['screenName']}}

            yield scrapy.Request(
                self.lender_profile_url, method='POST',
                callback=self.parse_lender_profile_page,
                body=json.dumps(payload),
                headers={'Content-Type': 'application/json'},
                meta={'payload': payload},
                dont_filter=True)

        current_page_index = payload_from_response['page']

        if total_lenders > current_page_index * self.pageSize:
            current_page_index += 1
            payload = {
                'fields': ['screenName'],
                'location': payload_from_response['location'],
                'page': current_page_index,
                'pageSize': self.pageSize,
                'sort': 'Relevance'
            }

            yield scrapy.Request(
                self.lenders_url_by_city, method='POST',
                callback=self.parse_lenders_list,
                body=json.dumps(payload),
                headers={'Content-Type': 'application/json'},
                meta={'payload': payload},
                dont_filter=True)

    def parse_lender_profile_page(self, response):
        lender_json = json.loads(response.text)["lender"]

        if not lender_json["id"] in self.id_list:
            self.id_list.append(lender_json["id"])

            fieldnames = ['First Name', 'Last Name', 'NMLS number', 'Mobile Phone', 'Office Phone', 'Email']

            if not os.path.exists(os.path.dirname(os.path.abspath(__file__)) + "/../external_data/output/output_file.csv"):
                with open(os.path.dirname(os.path.abspath(__file__)) + "/../external_data/output/output_file.csv", 'w') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
            else:
                with open(os.path.dirname(os.path.abspath(__file__)) + "/../external_data/output/output_file.csv", 'a') as csvfile:
                    try:
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        dict_row = {'First Name': lender_json["individualName"]["firstName"],
                                    'Last Name': lender_json["individualName"]["lastName"],
                                    'NMLS number': lender_json["nmlsId"]}
                        if "cellPhone" in lender_json:
                            dict_row["Mobile Phone"] = lender_json["cellPhone"]["areaCode"] + \
                                                       lender_json["cellPhone"]["prefix"] + \
                                                       lender_json["cellPhone"]["number"]
                        if "officePhone" in lender_json:
                            dict_row["Office Phone"] = lender_json["officePhone"]["areaCode"] + \
                                                       lender_json["officePhone"]["prefix"] + \
                                                       lender_json["officePhone"]["number"]

                        if "email" in lender_json:
                            dict_row["Email"] = lender_json["email"]

                        writer.writerow(dict_row)
                    except Exception as e:
                        pass

            # first_name, last_name, mls_number, mobile_phone, office_phone, email
            print(json.loads(response.text)["lender"]["screenName"])
