#!/usr/bin/env python

print('If you get error "ImportError: No module named \'six\'" install six:\n'+\
    '$ sudo pip install six');


import os
import re
import sys
import requests
import time
import pymysql
import random
import json
from fake_useragent import UserAgent

db = pymysql.connect("127.0.0.1", "root", "ceg2ececeg2ece", "closing_advance")
cursor = db.cursor()

if len(sys.argv) > 1:
    zipcode = sys.argv[1]
else:
    zipcode = '33316'

if not os.path.exists(os.path.dirname(os.path.realpath(__file__)) + "/../external_data/output/listing_pages_by_zip_codes/{}".format(zipcode)):
    os.mkdir(os.path.dirname(os.path.realpath(__file__)) + "/../external_data/output/listing_pages_by_zip_codes/{}".format(zipcode))

success_listing_urls_list = []

if os.path.exists(os.path.dirname(os.path.realpath(__file__)) + "/../external_data/output/listing_pages_by_zip_codes/{}/success_list.csv".format(zipcode)):
    with open(os.path.dirname(os.path.realpath(
            __file__)) + "/../external_data/output/listing_pages_by_zip_codes/{}/success_list.csv".format(zipcode),
              "r") as success_output_file:
        for line in success_output_file:
            success_listing_urls_list.append(line.strip())

    success_output_file.close()
else:
    with open(os.path.dirname(os.path.realpath(
            __file__)) + "/../external_data/output/listing_pages_by_zip_codes/{}/success_list.csv".format(zipcode),
              "w") as success_output_file:
        success_output_file.write("")

    success_output_file.close()

new_listing_urls_list = []
ua = UserAgent()

with open(os.path.dirname(os.path.realpath(__file__)) + "/../external_data/output/listing_searches_by_zip_codes/florida_{0}_listings_list.csv".format(zipcode)) as f:
    for line in f:
        if line.strip() not in success_listing_urls_list:
            new_listing_urls_list.append(line.strip())

random.shuffle(new_listing_urls_list)
continuous_failure = 0

for listing_url in new_listing_urls_list:
    print listing_url

    sql = "SELECT * FROM realtor_crawled_listings " \
          "WHERE originUrl=%s"
    row_count = cursor.execute(sql, (listing_url))

    if row_count > 0:
        with open(os.path.dirname(os.path.realpath(
                __file__)) + "/../external_data/output/listing_pages_by_zip_codes/{}/success_list.csv".format(
            zipcode),
                  "a") as success_output_file:
            success_output_file.write(listing_url + "\n")
        success_output_file.close()
        print "|-crawled before by other zipcodes"
        continue

    try:
        retry_limit = 10

        while retry_limit > 0:
            try:
                from six.moves.urllib import request

                opener = request.build_opener(
                    request.ProxyHandler(
                        {'https': 'http://127.0.0.1:24000'}))
                #            html_content = opener.open(
                #                'https://www.realtor.com/realestateandhomes-search/32615/type-single-family-home/price-150000-550000/nc-hide').read()

                html_content = opener.open(listing_url).read()
                break
            except Exception as e:
                time.sleep(6)
                retry_limit -= 1

        if retry_limit == 0:
            raise Exception()

        if html_content:
            html_content = html_content.decode('utf-8')
            listing_id = re.findall(re.compile(r'"property_id":(.*?),', flags=re.DOTALL), html_content)[0].strip()
            if listing_id:
                with open(os.path.dirname(os.path.realpath(__file__)) + "/../external_data/output/listing_pages_by_zip_codes/{0}/{1}.html".format(zipcode, listing_id), "w") as listing_file:
                    listing_file.write(html_content)
                listing_file.close()
                with open(os.path.dirname(os.path.realpath(
                        __file__)) + "/../external_data/output/listing_pages_by_zip_codes/{}/success_list.csv".format(
                    zipcode),
                          "a") as success_output_file:
                    success_output_file.write(listing_url + "\n")
                success_output_file.close()
                try:
                    sql = "INSERT INTO realtor_crawled_listings(" \
                          "listing_id, " \
                          "originUrl) " \
                          "VALUES " \
                          "(%s,%s)"
                    cursor.execute(sql,
                                   (listing_id,
                                    listing_url))
                    db.commit()
                except:
                    print "|-crawled a few mins ago by zip codes scraper"
                    pass

                continuous_failure = 0
    except Exception as e:
        print(e)
        continuous_failure += 1
        if continuous_failure > 10:
            print("Proxy doesn't work properly!!!")
            break

db.close()
