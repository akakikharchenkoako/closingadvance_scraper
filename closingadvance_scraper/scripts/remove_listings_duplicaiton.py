import csv
import os
import sys

realtor_listing_urls = []

if len(sys.argv) < 2:
    print("Please input csv file name.")
    exit(0)

with open(os.path.dirname(os.path.realpath(__file__)) + "/../external_data/output/" + sys.argv[1]) as infile:
    for line in infile:
        if line.strip() not in realtor_listing_urls:
            realtor_listing_urls.append(line.strip())

realtor_listing_urls = list(set(realtor_listing_urls))

with open(os.path.dirname(os.path.realpath(__file__)) + "/../external_data/output/" + sys.argv[1], "w") as output_file:
    for url in realtor_listing_urls:
        output_file.write(url + "\n")
