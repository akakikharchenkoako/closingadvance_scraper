# Scraper Guides

1. Export CSV files with full data from realtor_agents and realtor_brokers
1. Place realtor_agents.csv and realtor_brokers.csv files in closingadvance_scraper/external_data/input/ under the project dir.
These will be input data to filter_realtor_agents.py which is filter out agents associate at least one brokers via office name, office address and
office phone.
We ignore any listing can't be reached to the broker mobile.
1. Run filter_realtor_agents.py and this will generate 'filtered agent list.csv' inclosingadvance_scraper/external_data/output/ under the project dir.
