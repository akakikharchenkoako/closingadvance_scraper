import os
import pymysql
import json
import datetime
import re
from dateutil.parser import parse as to_datetime
from lxml import etree

base_url = "https://www.realtor.com"

# Open database connection
db = pymysql.connect("127.0.0.1", "root", "ceg2ececeg2ece", "closing_advance")

# prepare a cursor object using cursor() method
cursor = db.cursor()

for root, subdirs, files in os.walk(os.path.dirname(os.path.realpath(__file__)) + "/../external_data/output/listing_pages_by_zip_codes"):
    for filename in files:
        file_path = os.path.join(root, filename)
        print(file_path)

        try:
            parser = etree.HTMLParser()
            page_tree = etree.parse(file_path, parser)
            listing_id = str(filename[:-5])
            originUrl = page_tree.xpath("//link[@rel='canonical']/@href")[0]
            print("|-listing_id: " + listing_id)
            print("|-originUrl: " + originUrl)
            sql = "INSERT INTO realtor_crawled_listings(" \
                  "listing_id, " \
                  "originUrl, " \
                  "VALUES " \
                  "(%s,%s)"
            cursor.execute(sql,
                           (listing_id,
                            originUrl))
            # Commit your changes in the database
            db.commit()
        except Exception as e:
            print(str(e))
            # Rollback in case there is any error
            db.rollback()

# disconnect from server
db.close()
