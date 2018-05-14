import os
import re
from lxml import etree

for listing_page in os.listdir(os.path.dirname(os.path.realpath(__file__)) + "/../external_data/output/listing_pages"):
    if listing_page.endswith(".html"):
        try:
            parser = etree.HTMLParser()
            page_tree = etree.parse(os.path.dirname(
                os.path.realpath(__file__)) + "/../external_data/output/listing_pages/" + listing_page, parser)

            listing_id = re.findall(re.compile(r'"property_id":(.*?),', flags=re.DOTALL), open(os.path.dirname(
                os.path.realpath(__file__)) + "/../external_data/output/listing_pages/" + listing_page, "r").read())[0].strip()

            os.rename(os.path.dirname(
                os.path.realpath(__file__)) + "/../external_data/output/listing_pages/" + listing_page, os.path.dirname(
                os.path.realpath(__file__)) + "/../external_data/output/listing_pages/" + listing_id + ".html")
        except Exception as e:
            print(e)
