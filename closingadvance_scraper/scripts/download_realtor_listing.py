#!/usr/bin/env python

print('If you get error "ImportError: No module named \'six\'" install six:\n'+\
    '$ sudo pip install six');


import os
import re
import sys
import requests
import json

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

with open(os.path.dirname(os.path.realpath(__file__)) + "/../external_data/output/listing_searches_by_zip_codes/florida_{0}_listings_list.csv".format(zipcode)) as f:
    for line in f:
        if line.strip() not in success_listing_urls_list:
            new_listing_urls_list.append(line.strip())

continuous_failure = 0

for listing_url in new_listing_urls_list:
    print listing_url

    try:
        retry_limit = 3

        while retry_limit > 0:
            try:
                payload = {"headers": {}, "method": "GET", "url": listing_url}
                response_json = json.loads(requests.post("http://127.0.0.1:22999/api/test/24000", data=payload).text)
                html_content = response_json["response"]["body"]
                break
            except Exception as e:
                retry_limit -= 1

        if retry_limit == 0:
            raise Exception()

        if html_content:
            html_content = html_content.encode('utf-8')
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
                continuous_failure = 0
    except Exception as e:
        print(e)
        continuous_failure += 1
        if continuous_failure > 3:
            print("Proxy doesn't work properly!!!")
            break

