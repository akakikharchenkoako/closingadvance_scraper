#!/usr/bin/env python

print('If you get error "ImportError: No module named \'six\'" install six:\n'+\
    '$ sudo pip install six');


import os
import re
import requests
import time
import random
import json
from lxml import etree
from fake_useragent import UserAgent

luminati_port = '22999'
realtor_home_url = "https://www.realtor.com"

if not os.path.exists(os.path.dirname(os.path.realpath(__file__)) + "/../external_data/output/agent_profile_pages"):
    os.mkdir(os.path.dirname(os.path.realpath(__file__)) + "/../external_data/output/agent_profile_pages")

new_listing_urls_list = []
ua = UserAgent()
continuous_failure = 0

listing_pages_path_list = []

for root, subdirs, files in os.walk(os.path.dirname(os.path.realpath(__file__)) + "/../external_data/output/listing_pages_by_zip_codes"):
    for filename in files:
        file_path = os.path.join(root, filename)
        listing_pages_path_list.append(file_path)

random.shuffle(listing_pages_path_list)
print "Total listings: " + str(len(listing_pages_path_list))

for file_path in listing_pages_path_list:
    parser = etree.HTMLParser()
    page_tree = etree.parse(file_path, parser)
    agent_profile_link = page_tree.xpath("//a[@data-omtag='ldp:listingProvider:agentProfile']/@href")
    print file_path

    if not agent_profile_link:
        print "|-agent profile doesn't exist"
        continue

    agent_profile_link = realtor_home_url + agent_profile_link[0]
    agent_profile_page_name = agent_profile_link[agent_profile_link.rfind('/') + 1:]

    if os.path.exists(os.path.dirname(os.path.realpath(__file__)) +
                      "/../external_data/output/agent_profile_pages/{0}.html".format(agent_profile_page_name)):
        print "|-agent profile was already crawled before"
        continue

    try:
        retry_limit = 10

        while retry_limit > 0:
            try:
                headers = {}
                headers['User-Agent'] = ua.chrome
                headers['Content-Type'] = "application/json"
                payload = {"headers": headers, "method": "GET", "url": agent_profile_link}
                response_json = json.loads(requests.post("http://127.0.0.1:{0}/api/test/24000".format(luminati_port), data=payload).text)
                html_content = response_json["response"]["body"]
                html_content = html_content.encode('utf-8')

                if html_content.startswith("<html><body>You are being "):
                    agent_profile_link = re.findall(re.compile(r'<a href="(.*?)">', flags=re.DOTALL), html_content)[
                        0].strip()

                    payload["url"] = agent_profile_link
                    response_json = json.loads(requests.post("http://127.0.0.1:{0}/api/test/24000".format(luminati_port),
                                                             data=payload).text)
                    html_content = response_json["response"]["body"]
                    html_content = html_content.encode('utf-8')

                print "|-agent profile was crawled successfully"
                break
            except Exception as e:
                time.sleep(6)
                retry_limit -= 1

        if retry_limit == 0:
            raise Exception()

        if html_content:
            with open(os.path.dirname(os.path.realpath(__file__)) +
                      "/../external_data/output/agent_profile_pages/{0}.html".format(
                          agent_profile_page_name), "w") as agent_profile_file:
                agent_profile_file.write(html_content)
                agent_profile_file.close()

            continuous_failure = 0
            print agent_profile_link
    except Exception as e:
        print(e)
        continuous_failure += 1
        if continuous_failure > 10:
            print("Proxy doesn't work properly!!!")
            break

