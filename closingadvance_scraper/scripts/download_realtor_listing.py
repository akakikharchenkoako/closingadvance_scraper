#!/usr/bin/env python

print('If you get error "ImportError: No module named \'six\'" install six:\n'+\
    '$ sudo pip install six');

import sys
import os
import re
from fake_useragent import UserAgent
from random import shuffle
import requests
import json

ua = UserAgent()

with open(os.path.dirname(os.path.realpath(__file__)) + "/../external_data/output/failure_list.csv", "w") as output_file:
    output_file.write("")

output_file.close()
listing_urls_list = []

with open(os.path.dirname(os.path.realpath(__file__)) + "/../external_data/output/qualified_realtor_sold_listings.csv") as f:
    for line in f:
        listing_urls_list.append(line.strip())

shuffle(listing_urls_list)

for listing_url in listing_urls_list:
    try:
        payload = {"headers": {}, "method": "GET", "url": listing_url}
        headers = {}
        headers['User-Agent'] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
        headers['Content-Type'] = "application/json"
        response_json = json.loads(requests.post("http://127.0.0.1:22999/api/test/24000", data=payload).text)
        html_content = response_json["response"]["body"]

        if html_content:
            html_content = html_content.encode('utf-8')
            try:
                listing_id = re.findall(re.compile(r'"property_id":(.*?),', flags=re.DOTALL), html_content)[0].strip()
                if listing_id:
                    with open(os.path.dirname(os.path.realpath(__file__)) + "/../external_data/output/listing_pages/{0}.html".format(listing_id), "w") as listing_file:
                        listing_file.write(html_content)
            except Exception as e:
                with open(os.path.dirname(os.path.realpath(__file__)) + "/../external_data/output/failure_list.csv",
                          "a") as output_file:
                    output_file.write(listing_url + "\n")
    except Exception as e:
        print(e)
