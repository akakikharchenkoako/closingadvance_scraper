import os
import pymysql
import json
import datetime
import re
from dateutil.parser import parse as to_datetime
from lxml import etree

base_url = "https://www.realtor.com"

# Open database connection
db = pymysql.connect("127.0.0.1", "root", "password", "cag")

# prepare a cursor object using cursor() method
cursor = db.cursor()

for root, subdirs, files in os.walk(os.path.dirname(os.path.realpath(__file__)) + "/../external_data/output/listing_pages_by_zip_codes"):
    for filename in files:
        file_path = os.path.join(root, filename)

        try:
            parser = etree.HTMLParser()
            page_tree = etree.parse(file_path, parser)
            listing_id = str(filename[:-5])
            listingPropertyJson = json.loads(
                re.findall(re.compile(r'MOVE_DATA.propertyDetails,(.*?)\);\n', flags=re.DOTALL),
                           etree.tostring(page_tree).decode("utf-8"))[0].strip())
            listingProvider = listingPropertyJson.get("listing_provider", {})
            originUrl = page_tree.xpath("//link[@rel='canonical']/@href")[0]
            agent_profile_link = page_tree.xpath("//a[@data-omtag='ldp:listingProvider:agentProfile']/@href")

            if not agent_profile_link:
                continue

            agentUrl = base_url + agent_profile_link[0]
            agent_profile_page_name = agentUrl[agentUrl.rfind('/') + 1:]
            agent_profile_page_path = os.path.dirname(os.path.realpath(__file__)) + \
                                      "/../external_data/output/agent_profile_pages/{0}.html".format(agent_profile_page_name)

            if not os.path.exists(agent_profile_page_path):
                continue

            agent_parser = etree.HTMLParser()
            agent_page_tree = etree.parse(agent_profile_page_path, agent_parser)
            agentMobiles = [None, None, None, None]
            agentOffice = None
            mobileIndex = 0

            for node in agent_page_tree.xpath('//div[@id="modalcontactInfo"]//li/i[contains(@class, "fa-phone")]'):
                if 'Office:' in node.tail:
                    agentOffice = node.xpath('./parent::*/a/span/text()')[0]
                    continue

                if 'Mobile:' in node.tail and node.xpath('./parent::*/a/span/text()'):
                    agentMobiles[mobileIndex] = node.xpath('./parent::*/a/span/text()')[0]
                    mobileIndex += 1

                    if mobileIndex >= 4:
                        break

            agentName = listingProvider.get("agent_name")
            brokerName = listingProvider.get("broker_name")
            brokerMobile = listingProvider.get("broker_number")
            brokerOfficePhone = listingProvider.get("office_contact")
            status = listingPropertyJson.get("property_status")
            soldDate = page_tree.xpath("//span[@data-label='property-meta-sold-date']/text()")
            if soldDate:
                soldDate = soldDate[0]
                soldDate = soldDate[soldDate.find(" on ") + 4:].strip()
                soldDate = datetime.datetime.strptime(soldDate, '%B %d, %Y').strftime("%Y-%m-%d")
            else:
                soldDate = None
            beds = str(listingPropertyJson.get("beds", ""))
            baths = str(listingPropertyJson.get("baths" ""))
            if not baths.isdigit():
                baths = str(re.sub("[^\d\.]", "", baths))
            sqft = str(listingPropertyJson.get("sqft", ""))
            lotSize = str(listingPropertyJson.get("lot_size", ""))
            photoCount = page_tree.xpath('//a[@id="hero-view-photo"]/span[3]/text()')
            if photoCount:
                photoCount = photoCount[0]
                photoCount = str(re.sub("[^\d\.]", "", photoCount))
            else:
                photoCount = 1
            lastSoldPrice = str(listingPropertyJson.get("price", ""))
            propertyAddress = listingPropertyJson.get("full_address_display")
            zipCode = page_tree.xpath("//meta[@property='og:postal-code']/@content")
            if zipCode:
                zipCode = zipCode[0]
            moreExpensiveThanNearbyProperties = page_tree.xpath('//span[contains(text(), "More expensive than")]'
                                                                '/preceding-sibling::div/text()')
            if moreExpensiveThanNearbyProperties:
                moreExpensiveThanNearbyProperties = re.sub("[^\d\.]", "",
                                                           moreExpensiveThanNearbyProperties[0]).strip()
            lessExpensiveThanNearbyProperties = page_tree.xpath('//span[contains(text(), "Less expensive than")]'
                                                                '/preceding-sibling::div/text()')
            if lessExpensiveThanNearbyProperties:
                lessExpensiveThanNearbyProperties = re.sub("[^\d\.]", "",
                                                           lessExpensiveThanNearbyProperties[0]).strip()
            daysOnMarket = page_tree.xpath(
                '//span[contains(text(), "Days on market")]/preceding-sibling::div[@class="summary-datapoint"]/text()')
            if daysOnMarket:
                daysOnMarket = re.sub("[^\d\.]", "", daysOnMarket[0]).strip()
            soldHigherThanTheListedPrice = page_tree.xpath('//span[contains(text(), "Sold higher than")]'
                                                           '/preceding-sibling::div/text()')
            if soldHigherThanTheListedPrice:
                soldHigherThanTheListedPrice = re.sub("[^\d\.]", "", soldHigherThanTheListedPrice[0]).strip()
            soldLowerThanTheListedPrice = page_tree.xpath('//span[contains(text(), "Sold lower than")]'
                                                          '/preceding-sibling::div/text()')
            if soldLowerThanTheListedPrice:
                soldLowerThanTheListedPrice = re.sub("[^\d\.]", "", soldLowerThanTheListedPrice[0]).strip()
            pricePerSqFt = page_tree.xpath(
                '//div[contains(text(), "Price/Sq Ft")]/following-sibling::div/text()')
            if pricePerSqFt:
                pricePerSqFt = re.sub("[^\d\.]", "", pricePerSqFt[0]).strip()
            yearBuilt = str(listingPropertyJson.get("year_built", ""))
            medianListingPrice = page_tree.xpath(
                '//div[text()="Median Listing Price"]/preceding-sibling::p/text()')
            if medianListingPrice:
                medianListingPrice = re.sub("[^\d\.]", "", medianListingPrice[0]).strip()
            medianDaysOnMarket = page_tree.xpath(
                '//div[text()="Median Days on Market"]/preceding-sibling::p/text()')
            if medianDaysOnMarket:
                medianDaysOnMarket = re.sub("[^\d\.]", "", medianDaysOnMarket[0]).strip()
            averagePricePerSqFt = page_tree.xpath(
                '//div[text()="Price Per Sq Ft"]/preceding-sibling::p/text()')
            if averagePricePerSqFt:
                averagePricePerSqFt = re.sub("[^\d\.]", "", averagePricePerSqFt[0]).strip()

            print(originUrl)

            averageNearbySchoolRating = 0

            nearby_schools_block_list = page_tree.xpath('//div[@id="load-more-schools"]//table/tbody/tr')
            nearby_schools_dict_list = []
            for nearby_school in nearby_schools_block_list:
                rating = nearby_school.xpath('./td[1]/span/text()')[0] if nearby_school.xpath('./td[1]/span/text()') else None
                if rating and not rating.isdigit():
                    continue
                school_name = nearby_school.xpath('./td[2]/a/text()')[0] if nearby_school.xpath('./td[2]/a/text()') else None
                nearby_school_dict = {'rating': rating, 'school_name': school_name}
                sql = "INSERT INTO realtor_nearby_schools_julien(" \
                      "listing_id, " \
                      "rating, " \
                      "schoolName) " \
                      "VALUES " \
                      "(%s,%s,%s)"
                cursor.execute(sql,
                               (listing_id,
                                rating if rating else None,
                                school_name if school_name else None))
                averageNearbySchoolRating += int(rating)
                nearby_schools_dict_list.append(nearby_school_dict)
            if nearby_schools_dict_list:
                pass

            print("|-nearby")

            price_history_block_list = page_tree.xpath('//div[@id="ldp-history-price"]//table/tbody/tr')
            price_history_dict_list = []
            for price_record in price_history_block_list:
                listingDate = price_record.xpath('./td[1]/text()')
                if listingDate:
                    if listingDate[0].lower() == "today":
                        listingDate = datetime.date.today().strftime("%Y-%m-%d")
                    else:
                        listingDate = listingDate[0]
                listingEvent = price_record.xpath('./td[2]/text()')[0] if price_record.xpath('./td[2]/text()') else None
                purchasePrice = price_record.xpath('./td[3]/text()')[0] if price_record.xpath('./td[3]/text()') else None
                listingSource = price_record.xpath('./td[5]/text()')[0] if price_record.xpath('./td[5]/text()') else None
                if purchasePrice:
                    purchasePrice = re.sub("[^\d\.]", "", purchasePrice)
                price_history_dict = {'listingDate': to_datetime(listingDate).strftime("%Y-%m-%d"),
                                      'listingEvent': listingEvent,
                                      'purchasePrice': purchasePrice,
                                      'listingSource': listingSource}
                if not purchasePrice.isdigit():
                    del price_history_dict['purchasePrice']
                sql = "INSERT INTO realtor_price_histories_julien(" \
                      "listing_id, " \
                      "listingDate, " \
                      "listingEvent, " \
                      "purchasePrice, " \
                      "listingSource) " \
                      "VALUES " \
                      "(%s,%s,%s,%s,%s)"
                cursor.execute(sql,
                            (listing_id,
                            price_history_dict.get('listingDate', None),
                            price_history_dict.get('listingEvent', None),
                            price_history_dict.get('purchasePrice', None),
                            price_history_dict.get('listingSource', None)))
                price_history_dict_list.append(price_history_dict)
            if price_history_dict_list:
                pass

            print("|-price_history")

            mostRecentTaxPrice = None

            tax_history_block_list = page_tree.xpath('//div[@id="ldp-history-taxes"]//table/tbody/tr')
            tax_history_dict_list = []
            for tax_record in tax_history_block_list:
                print(tax_record)
                listingDate = tax_record.xpath('./td[1]/text()')[0] if tax_record.xpath('./td[1]/text()') else 'NULL'
                taxPrice = tax_record.xpath('./td[2]/text()')
                if taxPrice:
                    taxPrice = re.sub("[^\d\.]", "", taxPrice[0])
                tax_history_dict = {'listingDate': listingDate, 'taxPrice': taxPrice if taxPrice else None}
                if not taxPrice.isdigit():
                    del tax_history_dict['taxPrice']
                sql = "INSERT INTO realtor_tax_histories_julien(" \
                      "listing_id, " \
                      "listingDate, " \
                      "taxPrice) " \
                      "VALUES " \
                      "(%s,%s,%s)"
                cursor.execute(sql,
                                (listing_id,
                                tax_history_dict.get('listingDate', None),
                                tax_history_dict.get('taxPrice', None)))
                tax_history_dict_list.append(tax_history_dict)
            if tax_history_dict_list:
                mostRecentTaxPrice = tax_history_dict_list[0]['taxPrice']

            print("|-tax")

            # Prepare SQL query to INSERT a record into the database.
            sql = "INSERT INTO realtor_listings_julien(" \
                  "id, " \
                  "originUrl, " \
                  "agentUrl, " \
                  "agentName, " \
                  "agentMobile1, " \
                  "agentMobile2, " \
                  "agentMobile3, " \
                  "agentMobile4, " \
                  "brokerName, " \
                  "brokerMobile, " \
                  "brokerOffice, " \
                  "status, " \
                  "soldDate, " \
                  "beds, " \
                  "baths, " \
                  "sqft, " \
                  "lotSize, " \
                  "photoCount, " \
                  "lastSoldPrice, " \
                  "mostRecentTaxPrice, " \
                  "propertyAddress, " \
                  "zipCode, " \
                  "averageNearbySchoolRating, " \
                  "nearbySchoolsCount, " \
                  "moreExpensiveThanNearbyProperties, " \
                  "lessExpensiveThanNearbyProperties, " \
                  "daysOnMarket, " \
                  "soldHigherThanTheListedPrice, " \
                  "soldLowerThanTheListedPrice, " \
                  "pricePerSqFt, " \
                  "yearBuilt, " \
                  "medianListingPrice, " \
                  "medianDaysOnMarket, " \
                  "neighborhoodPricePerSqFt) " \
                  "VALUES " \
                  "(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s," \
                  "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s," \
                  "%s,%s,%s,%s,%s,%s,%s)"

            cursor.execute(sql,
                           (listing_id,
                            originUrl,
                            agentUrl,
                            agentName if agentName else None,
                            agentMobiles[0],
                            agentMobiles[1],
                            agentMobiles[2],
                            agentMobiles[3],
                            brokerName if brokerName else None,
                            brokerMobile if brokerMobile else None,
                            brokerOfficePhone if brokerOfficePhone else None,
                            status if status else None,
                            soldDate if soldDate else None,
                            beds if beds else None,
                            baths if baths else None,
                            sqft if sqft else None,
                            lotSize if lotSize else None,
                            photoCount if photoCount else None,
                            lastSoldPrice if lastSoldPrice else None,
                            mostRecentTaxPrice if mostRecentTaxPrice else None,
                            propertyAddress if propertyAddress else None,
                            zipCode if zipCode else None,
                            averageNearbySchoolRating / len(
                                nearby_schools_dict_list) if nearby_schools_dict_list else None,
                            len(nearby_schools_dict_list),
                            moreExpensiveThanNearbyProperties if moreExpensiveThanNearbyProperties else None,
                            lessExpensiveThanNearbyProperties if lessExpensiveThanNearbyProperties else None,
                            daysOnMarket if daysOnMarket else None,
                            soldHigherThanTheListedPrice if soldHigherThanTheListedPrice else None,
                            soldLowerThanTheListedPrice if soldLowerThanTheListedPrice else None,
                            pricePerSqFt if pricePerSqFt else None,
                            yearBuilt if yearBuilt else None,
                            medianListingPrice if medianListingPrice else None,
                            medianDaysOnMarket if medianDaysOnMarket else None,
                            averagePricePerSqFt if averagePricePerSqFt else None)
                           )
            print("|-listing")
            # Commit your changes in the database
            db.commit()
        except Exception as e:
            print("|->>>>" + str(e))
            # Rollback in case there is any error
            db.rollback()

# disconnect from server
db.close()
