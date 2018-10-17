#!/usr/bin/env python

print('If you get error "ImportError: No module named \'six\'" install six:\n'+\
    '$ sudo pip install six');


import os
import re
import requests
import time
import random
import sys
import json
from lxml import etree
from fake_useragent import UserAgent


reload(sys)
sys.setdefaultencoding('utf8')

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
    try:
        agent_profile_link = page_tree.xpath("//a[@data-omtag='ldp:listingProvider:agentProfile']/@href")
        print file_path
    except Exception as e:
        print e
        continue

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
                from six.moves.urllib import request

                opener = request.build_opener(
                    request.ProxyHandler(
                        {'https': 'http://127.0.0.1:24000'}))
                #            html_content = opener.open(
                #                'https://www.realtor.com/realestateandhomes-search/32615/type-single-family-home/price-150000-550000/nc-hide').read()

                html_content = opener.open(agent_profile_link).read()
                html_content = html_content.decode('utf-8')

                if html_content.startswith("<html><body>You are being "):
                    agent_profile_link = re.findall(re.compile(r'<a href="(.*?)">', flags=re.DOTALL), html_content)[
                        0].strip()

                    from six.moves.urllib import request

                    opener = request.build_opener(
                        request.ProxyHandler(
                            {'https': 'http://127.0.0.1:24000'}))
                    #            html_content = opener.open(
                    #                'https://www.realtor.com/realestateandhomes-search/32615/type-single-family-home/price-150000-550000/nc-hide').read()

                    html_content = opener.open(agent_profile_link).read()
                    html_content = html_content.decode('utf-8')

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

