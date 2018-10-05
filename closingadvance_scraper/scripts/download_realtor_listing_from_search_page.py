#!/usr/bin/env python

# SEARCH URL SAMPLE: https://www.realtor.com/realestateandhomes-search/33466/type-single-family-home/price-150000-550000/nc-hide
# Description:
#   - Downloads all listing pages from realtor search url by looping page number

import os
import os.path
import sys
import requests
from lxml import html
import zipcodes
import json

realtor_home_url = "https://www.realtor.com"
search_url = "https://www.realtor.com/realestateandhomes-search/{0}/type-single-family-home/price-150000-550000/nc-hide"

new_zipcodes_list = []
for zipcode in zipcodes.filter_by(zipcodes.list_all(), active=True):
    if zipcode['state'] == "FL" and \
            not os.path.isfile(os.path.dirname(os.path.realpath(__file__)) + "/../external_data/output/listing_searches_by_zip_codes/florida_{0}_listings_list.csv".format(zipcode['zip_code'])):
        new_zipcodes_list.append(zipcode['zip_code'])

for zipcode in new_zipcodes_list:
    retry_limit = 3

    while retry_limit > 0:
        try:
            import sys

            if sys.version_info[0] == 2:
                import six
                from six.moves.urllib import request

                opener = request.build_opener(
                    request.ProxyHandler(
                        {
                            'http': 'http://lum-customer-creditadvisory-zone-dedicated-country-us:sjuk34itz0oe@zproxy.lum-superproxy.io:22225'}))
                html_content = opener.open(search_url.format(zipcode)).read()
            if sys.version_info[0] == 3:
                import urllib.request

                opener = urllib.request.build_opener(
                    urllib.request.ProxyHandler(
                        {
                            'http': 'http://lum-customer-creditadvisory-zone-dedicated-country-us:sjuk34itz0oe@zproxy.lum-superproxy.io:22225'}))
                html_content = opener.open(search_url.format(zipcode)).read()

            break
        except Exception as e:
            retry_limit -= 1

    if retry_limit == 0:
        break

    print search_url.format(zipcode)

    with open(os.path.dirname(os.path.realpath(__file__)) + "/../external_data/output/listing_searches_by_zip_codes/florida_{0}_listings_list.csv".format(zipcode), "w") as output_file:
        output_file.write("")

        while html_content:
            urls_list = []
            html_content = html_content.encode('utf-8')
            page_tree = html.fromstring(html_content)
            urls_list = [realtor_home_url + str(url) for url in page_tree.xpath("//ul[@id='radius-properties']/li/@data-url")]

            if not urls_list:
                urls_list = [realtor_home_url + str(url) for url in page_tree.xpath("//div[@id='srp-list']//ul[contains(@class, 'prop-list')]/li/@data-url")]

            if not urls_list:
                break

            for url in urls_list:
                output_file.write(url + '\n')

            next_page_url = page_tree.xpath("//div[@id='ResultsPerPageBottom']//a[@data-omtag='srp:paging:next']/@href")

            if not next_page_url:
                break

            next_page_url = search_url.format(zipcode) + "/" + str(next_page_url[0].split("/")[-1])

            print " |-" + next_page_url

            retry_limit = 3

            while retry_limit > 0:
                try:
                    payload = {"headers": {}, "method": "GET", "url": next_page_url}

                    import sys

                    if sys.version_info[0] == 2:
                        import six
                        from six.moves.urllib import request

                        opener = request.build_opener(
                            request.ProxyHandler(
                                {
                                    'http': 'http://lum-customer-creditadvisory-zone-dedicated-country-us:sjuk34itz0oe@zproxy.lum-superproxy.io:22225'}))
                        html_content = opener.open(next_page_url).read()
                    if sys.version_info[0] == 3:
                        import urllib.request

                        opener = urllib.request.build_opener(
                            urllib.request.ProxyHandler(
                                {
                                    'http': 'http://lum-customer-creditadvisory-zone-dedicated-country-us:sjuk34itz0oe@zproxy.lum-superproxy.io:22225'}))
                        html_content = opener.open(next_page_url).read()

                    break
                except Exception as e:
                    retry_limit -= 1

            if retry_limit == 0:
                break

    output_file.close()
