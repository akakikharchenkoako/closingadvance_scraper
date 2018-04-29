import csv
import os
import sys

realtor_listing_urls = []

if len(sys.argv) < 2:
    print("Please input csv file names.")
    exit(0)

with open(os.path.dirname(os.path.realpath(__file__)) + "/../external_data/output/" + sys.argv[2], "w") as output_file:
    with open(os.path.dirname(os.path.realpath(__file__)) + "/../external_data/output/" + sys.argv[1]) as infile:
        for line in infile:
            if line.strip() not in realtor_listing_urls:
                realtor_listing_urls.append(line.strip())
                output_file.write(line.strip() + "\n")
