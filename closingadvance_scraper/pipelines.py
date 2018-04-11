# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import logging
import datetime
import ast
import json
from closingadvance_scraper.items import *
from closingadvance_scraper.models import *

logger = logging.getLogger('peewee')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


class MySQLPipeline(object):

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.stats)

    def __init__(self, stats):
        db.connect()

    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        db.close()

    def process_item(self, item, spider):
        if isinstance(item, ZillowAgentItem):
            return self.process_zillow_agent_item(item, spider)
        elif isinstance(item, ZillowBrokerItem):
            return self.process_zillow_broker_item(item, spider)
        elif isinstance(item, ZillowListingItem):
            return self.process_zillow_listing_item(item, spider)
        elif isinstance(item, TruliaListingItem):
            return self.process_trulia_listing_item(item, spider)
        elif isinstance(item, Century21AgentItem):
            return self.process_century21_agent_item(item, spider)
        elif isinstance(item, Century21OfficeItem):
            return self.process_century21_office_item(item, spider)
        elif isinstance(item, HomeClosingItem):
            return self.process_homeclosing_item(item, spider)
        elif isinstance(item, CompanyItem):
            return self.process_company_item(item, spider)
        elif isinstance(item, AttorneyItem):
            return self.process_attorney_item(item, spider)
        elif isinstance(item, BankInfoItem):
            return self.process_bank_info_item(item, spider)
        elif isinstance(item, LenderItem):
            return self.process_lender_item(item, spider)
        elif isinstance(item, RealtorAgentItem):
            return self.process_realtor_agent_item(item, spider)
        elif isinstance(item, RealtorBrokerItem):
            return self.process_realtor_broker_item(item, spider)
        elif isinstance(item, RealtorListingItem):
            return self.process_realtor_listing_item(item, spider)
        elif isinstance(item, RealtorListingAllItem):
            return self.process_realtor_listing_all_item(item, spider)
        elif isinstance(item, RealtorListingForJulienItem):
            return self.process_realtor_listing_for_julien_item(item, spider)
        elif isinstance(item, RealtorListingFix1ForJulienItem):
            return self.process_realtor_listing_fix1_for_julien_item(item, spider)
        else:
            return item

    def process_zillow_agent_item(self, item, spider):
        try:
            ZillowAgent.get(ZillowAgent.originUrl == item['originUrl'])
        except ZillowAgent.DoesNotExist:
            ZillowAgent.create(
                originUrl=item.get('originUrl'),
                brokerUrl=item.get('brokerUrl'),
                agentName=item.get('agentName'),
                designation=item.get('designation'),
                agentMobile=item.get('agentMobile'),
                activeListings=item.get('activeListings'),
                salesLast12Months=item.get('salesLast12Months'),
                officeName=item.get('officeName'),
                officePhone=item.get('officePhone'),
                officeAddress=item.get('officeAddress'),
                location=item.get('location'),
            )
        else:
            q = ZillowAgent.update(
                brokerUrl=item.get('brokerUrl'),
                agentName=item.get('agentName'),
                designation=item.get('designation'),
                agentMobile=item.get('agentMobile'),
                activeListings=item.get('activeListings'),
                salesLast12Months=item.get('salesLast12Months'),
                officeName=item.get('officeName'),
                officePhone=item.get('officePhone'),
                officeAddress=item.get('officeAddress'),
                location=item.get('location'),
                modified=datetime.datetime.now()
            ).where(ZillowAgent.originUrl == item['originUrl'])
            q.execute()
        return item

    def process_zillow_broker_item(self, item, spider):
        try:
            ZillowBroker.get(ZillowBroker.originUrl == item['originUrl'])
        except ZillowBroker.DoesNotExist:
            ZillowBroker.create(
                originUrl=item.get('originUrl'),
                brokerName=item.get('brokerName'),
                brokerTitle=item.get('brokerTitle'),
                brokerMobile=item.get('brokerMobile'),
                officeName=item.get('officeName'),
                officePhone=item.get('officePhone'),
                officeAddress=item.get('officeAddress'),
                location=item.get('location'),
            )
        else:
            q = ZillowBroker.update(
                brokerName=item.get('brokerName'),
                brokerTitle=item.get('brokerTitle'),
                brokerMobile=item.get('brokerMobile'),
                officeName=item.get('officeName'),
                officePhone=item.get('officePhone'),
                officeAddress=item.get('officeAddress'),
                location=item.get('location'),
                modified=datetime.datetime.now()
            ).where(ZillowBroker.originUrl == item['originUrl'])
            q.execute()
        return item

    def process_trulia_listing_item(self, item, spider):
        try:
            TruliaListing.get(TruliaListing.originUrl == item['originUrl'])
        except TruliaListing.DoesNotExist:
            TruliaListing.create(
                originUrl=item.get('originUrl'),
                listingStatus=item.get('listingStatus'),
                purchasePrice=item.get('purchasePrice'),
                mlsId=item.get('mlsId'),
                zipCode=item.get('zipCode'),
                daysOnMarket=item.get('daysOnMarket'),
                yearBuilt=item.get('yearBuilt'),
                beds=item.get('beds'),
                baths=item.get('baths'),
                sqft=item.get('sqft'),
                lotSize=item.get('lotSize'),
                photoCount=item.get('photoCount'),
                listingUpdated=item.get('listingUpdated'),
                agentName=item.get('agentName'),
                agentMobile=item.get('agentMobile'),
                officeName=item.get('officeName'),
                officePhone=item.get('officePhone'),
                propertyAddress=item.get('propertyAddress')
            )
        else:
            q = TruliaListing.update(
                listingStatus=item.get('listingStatus'),
                purchasePrice=item.get('purchasePrice'),
                mlsId=item.get('mlsId'),
                zipCode=item.get('zipCode'),
                daysOnMarket=item.get('daysOnMarket'),
                yearBuilt=item.get('yearBuilt'),
                beds=item.get('beds'),
                baths=item.get('baths'),
                sqft=item.get('sqft'),
                lotSize=item.get('lotSize'),
                photoCount=item.get('photoCount'),
                listingUpdated=item.get('listingUpdated'),
                agentName=item.get('agentName'),
                agentMobile=item.get('agentMobile'),
                officeName=item.get('officeName'),
                officePhone=item.get('officePhone'),
                propertyAddress=item.get('propertyAddress'),
                modified=datetime.datetime.now()
            ).where(TruliaListing.originUrl == item['originUrl'])
            q.execute()
        return item

    def process_zillow_listing_item(self, item, spider):
        if item['listingStatus'] == 'Sold':
            try:
                ZillowListing.get(ZillowListing.originUrl == item['originUrl'])
            except ZillowListing.DoesNotExist:
                ZillowListing.create(
                    originUrl=item.get('originUrl'),
                    listingStatus=item.get('listingStatus'),
                    purchasePrice=item.get('purchasePrice'),
                    mlsId=item.get('mlsId'),
                    zipCode=item.get('zipCode'),
                    daysOnMarket=item.get('daysOnMarket'),
                    yearBuilt=item.get('yearBuilt'),
                    beds=item.get('beds'),
                    baths=item.get('baths'),
                    sqft=item.get('sqft'),
                    lotSize=item.get('lotSize'),
                    photoCount=item.get('photoCount'),
                    listingUpdated=item.get('listingUpdated'),
                    openHouse=item.get('openHouse'),
                    propertyAddress=item.get('propertyAddress'),
                    agent=item.get('agent'),
                    officeName=item.get('officeName'),
                    officePhone=item.get('officePhone'))
            else:
                q = ZillowListing.update(
                    listingStatus=item.get('listingStatus')
                ).where(ZillowListing.originUrl == item['originUrl'])
                q.execute()
            return item

        try:
            ZillowListing.get(ZillowListing.originUrl == item['originUrl'])
        except ZillowListing.DoesNotExist:
            listing = ZillowListing.create(
                originUrl=item.get('originUrl'),
                listingStatus=item.get('listingStatus'),
                purchasePrice=item.get('purchasePrice'),
                mlsId=item.get('mlsId'),
                zipCode=item.get('zipCode'),
                daysOnMarket=item.get('daysOnMarket'),
                yearBuilt=item.get('yearBuilt'),
                beds=item.get('beds'),
                baths=item.get('baths'),
                sqft=item.get('sqft'),
                lotSize=item.get('lotSize'),
                photoCount=item.get('photoCount'),
                listingUpdated=item.get('listingUpdated'),
                openHouse=item.get('openHouse'),
                propertyAddress=item.get('propertyAddress'),
                agent=item.get('agent'),
                officeName=item.get('officeName'),
                officePhone=item.get('officePhone'),
            )
            for idx, entry in enumerate(item.get('priceHistories')):
                id = '{}{}'.format(listing.id, idx + 1)
                try:
                    PriceHistory.get(PriceHistory.id == id)
                except PriceHistory.DoesNotExist:
                    PriceHistory.create(
                        id=id,
                        listing=listing,
                        listingDate=entry.get('listingDate'),
                        purchasePrice=entry.get('purchasePrice'),
                        listingEvent=entry.get('listingEvent'),
                        listingSource=entry.get('listingSource'),
                        listingAgent=entry.get('listingAgent')
                    )
                else:
                    PriceHistory.update(
                        id=id,
                        listing=listing,
                        listingDate=entry.get('listingDate'),
                        purchasePrice=entry.get('purchasePrice'),
                        listingEvent=entry.get('listingEvent'),
                        listingSource=entry.get('listingSource'),
                        listingAgent=entry.get('listingAgent'),
                        modified=datetime.datetime.now()
                    )
        else:
            q = ZillowListing.update(
                listingStatus=item.get('listingStatus'),
                purchasePrice=item.get('purchasePrice'),
                mlsId=item.get('mlsId'),
                zipCode=item.get('zipCode'),
                daysOnMarket=item.get('daysOnMarket'),
                yearBuilt=item.get('yearBuilt'),
                beds=item.get('beds'),
                baths=item.get('baths'),
                sqft=item.get('sqft'),
                lotSize=item.get('lotSize'),
                photoCount=item.get('photoCount'),
                listingUpdated=item.get('listingUpdated'),
                openHouse=item.get('openHouse'),
                propertyAddress=item.get('propertyAddress'),
                agent=item.get('agent'),
                officeName=item.get('officeName'),
                officePhone=item.get('officePhone'),
                modified=datetime.datetime.now()
            ).where(ZillowListing.originUrl == item['originUrl'])
            q.execute()
            listing = ZillowListing.get(ZillowListing.originUrl == item['originUrl'])
            for idx, entry in enumerate(item.get('priceHistories')):
                id = '{}{}'.format(listing.id, idx + 1)
                try:
                    PriceHistory.get(PriceHistory.id == id)
                except PriceHistory.DoesNotExist:
                    PriceHistory.create(
                        id=id,
                        listing=listing,
                        listingDate=entry.get('listingDate'),
                        purchasePrice=entry.get('purchasePrice'),
                        listingEvent=entry.get('listingEvent'),
                        listingSource=entry.get('listingSource'),
                        listingAgent=entry.get('listingAgent')
                    )
                else:
                    PriceHistory.update(
                        id=id,
                        listing=listing,
                        listingDate=entry.get('listingDate'),
                        purchasePrice=entry.get('purchasePrice'),
                        listingEvent=entry.get('listingEvent'),
                        listingSource=entry.get('listingSource'),
                        listingAgent=entry.get('listingAgent'),
                        modified=datetime.datetime.now()
                    )

        return item

    def process_century21_agent_item(self, item, spider):
        try:
            Century21Agent.get(Century21Agent.agentUrl == item['agentUrl'])
        except Century21Agent.DoesNotExist:
            Century21Agent.create(
                agentUrl=item.get('agentUrl'),
                agentName=item.get('agentName'),
                agentPhone=item.get('agentPhone'),
                agentMobile=item.get('agentMobile'),
                officeName=item.get('officeName'),
                officePhone=item.get('officePhone'),
                officeAddress=item.get('officeAddress'),
            )
        else:
            q = Century21Agent.update(
                agentUrl=item.get('agentUrl'),
                agentName=item.get('agentName'),
                agentPhone=item.get('agentPhone'),
                agentMobile=item.get('agentMobile'),
                officeName=item.get('officeName'),
                officePhone=item.get('officePhone'),
                officeAddress=item.get('officeAddress'),
                modified=datetime.datetime.now()
            ).where(Century21Agent.agentUrl == item['agentUrl'])
            q.execute()
        return item

    def process_century21_office_item(self, item, spider):
        try:
            Century21Office.get(Century21Office.officeUrl == item['officeUrl'])
        except Century21Office.DoesNotExist:
            Century21Office.create(
                officeUrl=item.get('officeUrl'),
                officeName=item.get('officeName'),
                officePhone=item.get('officePhone'),
                officeAddress=item.get('officeAddress'),
                officeWebsite=item.get('officeWebsite'),
            )
        else:
            q = Century21Office.update(
                officeUrl=item.get('officeUrl'),
                officeName=item.get('officeName'),
                officePhone=item.get('officePhone'),
                officeAddress=item.get('officeAddress'),
                officeWebsite=item.get('officeWebsite'),
                modified=datetime.datetime.now()
            ).where(Century21Office.officeUrl == item['officeUrl'])
            q.execute()
        return item

    def process_company_item(self, item, spider):
        try:
            Company.get(Company.url == item['url'])
        except Company.DoesNotExist:
            Company.create(
                url=item.get('url'),
                name=item.get('name'),
                address=item.get('address'),
                phone=item.get('phone'),
                fax=item.get('fax'),
                email=item.get('email'),
                website=item.get('website'),
                categories=item.get('categories')
            )
        else:
            q = Company.update(
                url=item.get('url'),
                name=item.get('name'),
                address=item.get('address'),
                phone=item.get('phone'),
                fax=item.get('fax'),
                email=item.get('email'),
                website=item.get('website'),
                categories=item.get('categories'),
                modified=datetime.datetime.now()
            ).where(Company.url == item['url'])
            q.execute()
        return item

    def process_homeclosing_item(self, item, spider):
        try:
            Company.get(Company.phone == item['phone'])
        except Company.DoesNotExist:
            Company.create(
                url=item.get('url'),
                name=item.get('name'),
                address=item.get('address'),
                phone=item.get('phone'),
                fax=item.get('fax'),
                email=item.get('email'),
                website=item.get('website'),
            )
        # else:
        #     q = Company.update(
        #         url=item.get('url'),
        #         name=item.get('name'),
        #         address=item.get('address'),
        #         phone=item.get('phone'),
        #         fax=item.get('fax'),
        #         email=item.get('email'),
        #         website=item.get('website'),
        #         modified=datetime.datetime.now()
        #     ).where(Company.phone == item['phone'])
        #     q.execute()
        return item

    def process_attorney_item(self, item, spider):
        try:
            Attorney.get(Attorney.originUrl == item['originUrl'])
        except Attorney.DoesNotExist:
            Attorney.create(
                originUrl=item.get('originUrl'),
                name=item.get('name'),
                address=item.get('address'),
                phone=item.get('phone'),
                website=item.get('website'),
                practice_areas=item.get('practice_areas'),
                licensed_since=item.get('licensed_since'),
                pictureUrl=item.get('pictureUrl'),
            )
        else:
            q = Attorney.update(
                originUrl=item.get('originUrl'),
                name=item.get('name'),
                address=item.get('address'),
                phone=item.get('phone'),
                website=item.get('website'),
                practice_areas=item.get('practice_areas'),
                licensed_since=item.get('licensed_since'),
                pictureUrl=item.get('pictureUrl'),
                modified=datetime.datetime.now()
            ).where(Attorney.originUrl == item['originUrl'])
            q.execute()
        return item

    def process_bank_info_item(self, item, spider):
        try:
            BankInfo.get(BankInfo.routing_number == item['routing_number'])
        except BankInfo.DoesNotExist:
            BankInfo.create(
                address=item.get('address'),
                state=item.get('state'),
                city=item.get('city'),
                bank_name=item.get('bank_name'),
                routing_number=item.get('routing_number'),
                telephone=item.get('telephone'),
                zip_code=item.get('zip_code'),
                revision_date=item.get('revision_date')
            )
        else:
            q = BankInfo.update(
                address=item.get('address'),
                state=item.get('state'),
                city=item.get('city'),
                bank_name=item.get('bank_name'),
                telephone=item.get('telephone'),
                revision_date=item.get('revision_date'),
                modified=datetime.datetime.now()
            ).where(BankInfo.routing_number == item['routing_number'])
            q.execute()
        return item

    def process_lender_item(self, item, spider):
        try:
            Lender.get(Lender.link == item['link'])
        except Lender.DoesNotExist:
            Lender.create(
                link=item.get('link'),
                name=item.get('name'),
                address=item.get('address'),
                website=item.get('website'),
                cellPhone=item.get('cellPhone'),
                officePhone=item.get('officePhone'),
                email=item.get('email')
            )
        else:
            q = Lender.update(
                name=item.get('name'),
                address=item.get('address'),
                website=item.get('website'),
                cellPhone=item.get('cellPhone'),
                officePhone=item.get('officePhone'),
                email=item.get('email'),
                modified=datetime.datetime.now()
            ).where(Lender.link == item['link'])
            q.execute()
        return item

    def process_realtor_agent_item(self, item, spider):
        try:
            RealtorAgent.get(RealtorAgent.originUrl == item['originUrl'])
        except RealtorAgent.DoesNotExist:
            RealtorAgent.create(
                originUrl=item.get('originUrl'),
                brokerUrl=item.get('brokerUrl'),
                agentName=item.get('agentName'),
                designation=item.get('designation'),
                agentMobile=item.get('agentMobile'),
                activeListings=item.get('activeListings'),
                salesLast12Months=item.get('salesLast12Months'),
                officeName=item.get('officeName'),
                officePhone=item.get('officePhone'),
                officeAddress=item.get('officeAddress'),
                forSale=item.get('forSale'),
                recentlySold=item.get('recentlySold'),
                location=item.get('location'),
                teamUrl=item.get('teamUrl'),
                search_keyword=item.get('search_keyword'),
            )
        else:
            q = RealtorAgent.update(
                agentName=item.get('agentName'),
                designation=item.get('designation'),
                agentMobile=item.get('agentMobile'),
                activeListings=item.get('activeListings'),
                salesLast12Months=item.get('salesLast12Months'),
                officeName=item.get('officeName'),
                officePhone=item.get('officePhone'),
                officeAddress=item.get('officeAddress'),
                location=item.get('location'),
                forSale=item.get('forSale'),
                recentlySold=item.get('recentlySold'),
                modified=datetime.datetime.now(),
                teamUrl=item.get('teamUrl'),
                search_keyword=item.get('search_keyword'),
            ).where(RealtorAgent.originUrl == item['originUrl'])
            q.execute()
        return item

    def process_realtor_broker_item(self, item, spider):
        try:
            RealtorBroker.get(RealtorBroker.originUrl == item['originUrl'])
        except RealtorBroker.DoesNotExist:
            RealtorBroker.create(
                originUrl=item.get('originUrl'),
                brokerName=item.get('brokerName'),
                brokerTitle=item.get('brokerTitle'),
                brokerMobile=item.get('brokerMobile'),
                brokerMobile2=item.get('brokerMobile2'),
                brokerMobile3=item.get('brokerMobile3'),
                brokerMobile4=item.get('brokerMobile4'),
                officeName=item.get('officeName'),
                officePhone=item.get('officePhone'),
                officeAddress=item.get('officeAddress'),
                location=item.get('location'),
                teamUrl=item.get('teamUrl'),
                search_keyword=item.get('search_keyword'),
            )
        else:
            q = RealtorBroker.update(
                brokerName=item.get('brokerName'),
                brokerTitle=item.get('brokerTitle'),
                brokerMobile=item.get('brokerMobile'),
                brokerMobile2=item.get('brokerMobile2'),
                brokerMobile3=item.get('brokerMobile3'),
                brokerMobile4=item.get('brokerMobile4'),
                officeName=item.get('officeName'),
                officePhone=item.get('officePhone'),
                officeAddress=item.get('officeAddress'),
                location=item.get('location'),
                modified=datetime.datetime.now(),
                teamUrl=item.get('teamUrl'),
                search_keyword=item.get('search_keyword'),
            ).where(RealtorBroker.originUrl == item['originUrl'])
            q.execute()
        return item

    def process_realtor_listing_item(self, item, spider):
        agent = RealtorAgent.get(RealtorAgent.id == item['agent_id'])
        try:
            RealtorListing.get(RealtorListing.originUrl == item['originUrl'])
        except RealtorListing.DoesNotExist:
            listing = RealtorListing.create(
                originUrl=item.get('originUrl'),
                listingStatus=item.get('listingStatus'),
                purchasePrice=item.get('purchasePrice'),
                mlsId=item.get('mlsId'),
                zipCode=item.get('zipCode'),
                daysOnMarket=item.get('daysOnMarket'),
                yearBuilt=item.get('yearBuilt'),
                beds=item.get('beds'),
                baths=item.get('baths'),
                sqft=item.get('sqft'),
                lotSize=item.get('lotSize'),
                photoCount=item.get('photoCount'),
                listingUpdated=item.get('listingUpdated'),
                openHouse=item.get('openHouse'),
                propertyAddress=item.get('propertyAddress'),
                agent=agent,
                officeName=item.get('officeName'),
                officePhone=item.get('officePhone'),
                agentMobile=item.get('agentMobile'),
                agentName=item.get('agentName'),
                medianDaysOnMarket=item.get('medianDaysOnMarket'),
                daysOnRealtor=item.get('daysOnRealtor'),
                propertyTax=item.get('propertyTax'),
                lastSoldPrice=item.get('lastSoldPrice'),
            )
            if 'sold' not in item['listingStatus'].lower():
                for idx, entry in enumerate(ast.literal_eval(item.get('priceHistories'))):
                    id = '{}{}'.format(listing.id, idx + 1)
                    try:
                        RealtorPriceHistory.get(RealtorPriceHistory.id == id)
                    except RealtorPriceHistory.DoesNotExist:
                        RealtorPriceHistory.create(
                            id=id,
                            listing=listing,
                            listingDate=entry.get('listingDate'),
                            purchasePrice=entry.get('purchasePrice'),
                            listingEvent=entry.get('listingEvent'),
                            listingSource=entry.get('listingSource'),
                        )
                    else:
                        RealtorPriceHistory.update(
                            id=id,
                            listing=listing,
                            listingDate=entry.get('listingDate'),
                            purchasePrice=entry.get('purchasePrice'),
                            listingEvent=entry.get('listingEvent'),
                            listingSource=entry.get('listingSource'),
                            modified=datetime.datetime.now()
                        )
        else:
            if 'sold' in item['listingStatus'].lower():
                q = RealtorListing.update(
                    listingStatus=item.get('listingStatus')
                ).where(RealtorListing.originUrl == item['originUrl'])
                q.execute()
            else:
                q = RealtorListing.update(
                    listingStatus=item.get('listingStatus'),
                    purchasePrice=item.get('purchasePrice'),
                    mlsId=item.get('mlsId'),
                    zipCode=item.get('zipCode'),
                    daysOnMarket=item.get('daysOnMarket'),
                    yearBuilt=item.get('yearBuilt'),
                    beds=item.get('beds'),
                    baths=item.get('baths'),
                    sqft=item.get('sqft'),
                    lotSize=item.get('lotSize'),
                    photoCount=item.get('photoCount'),
                    listingUpdated=item.get('listingUpdated'),
                    openHouse=item.get('openHouse'),
                    propertyAddress=item.get('propertyAddress'),
                    agent=agent,
                    officeName=item.get('officeName'),
                    officePhone=item.get('officePhone'),
                    agentMobile=item.get('agentMobile'),
                    agentName=item.get('agentName'),
                    medianDaysOnMarket=item.get('medianDaysOnMarket'),
                    daysOnRealtor=item.get('daysOnRealtor'),
                    propertyTax=item.get('propertyTax'),
                    lastSoldPrice=item.get('lastSoldPrice'),
                    modified=datetime.datetime.now()
                ).where(RealtorListing.originUrl == item['originUrl'])
                q.execute()
                listing = RealtorListing.get(RealtorListing.originUrl == item['originUrl'])
                for idx, entry in enumerate(ast.literal_eval(item.get('priceHistories'))):
                    id = '{}{}'.format(listing.id, idx + 1)
                    try:
                        RealtorPriceHistory.get(RealtorPriceHistory.id == id)
                    except RealtorPriceHistory.DoesNotExist:
                        RealtorPriceHistory.create(
                            id=id,
                            listing=listing,
                            listingDate=entry.get('listingDate'),
                            purchasePrice=entry.get('purchasePrice'),
                            listingEvent=entry.get('listingEvent'),
                            listingSource=entry.get('listingSource'),
                        )
                    else:
                        RealtorPriceHistory.update(
                            id=id,
                            listing=listing,
                            listingDate=entry.get('listingDate'),
                            purchasePrice=entry.get('purchasePrice'),
                            listingEvent=entry.get('listingEvent'),
                            listingSource=entry.get('listingSource'),
                            modified=datetime.datetime.now()
                        )

        for broker_id in item.get('brokers_list').split(' '):
            broker = RealtorBroker.get(RealtorBroker.id == broker_id)
            RealtorListinBroker.create(
                listing=listing,
                broker=broker,
            )

        return item

    def process_realtor_listing_all_item(self, item, spider):
        try:
            RealtorListingAll.get(RealtorListingAll.originUrl == item['originUrl'])
        except RealtorListingAll.DoesNotExist:
            listing = RealtorListingAll.create(
                originUrl=item.get('originUrl'),
                listingStatus=item.get('listingStatus'),
                purchasePrice=item.get('purchasePrice'),
                mlsId=item.get('mlsId'),
                zipCode=item.get('zipCode'),
                daysOnMarket=item.get('daysOnMarket'),
                yearBuilt=item.get('yearBuilt'),
                beds=item.get('beds'),
                baths=item.get('baths'),
                sqft=item.get('sqft'),
                lotSize=item.get('lotSize'),
                photoCount=item.get('photoCount'),
                listingUpdated=item.get('listingUpdated'),
                openHouse=item.get('openHouse'),
                propertyAddress=item.get('propertyAddress'),
                agent=item.get('agent_id'),
                officeName=item.get('officeName'),
                officePhone=item.get('officePhone'),
                agentMobile=item.get('agentMobile'),
                agentName=item.get('agentName'),
                medianDaysOnMarket=item.get('medianDaysOnMarket'),
                daysOnRealtor=item.get('daysOnRealtor'),
                propertyTax=item.get('propertyTax'),
                lastSoldPrice=item.get('lastSoldPrice'),
            )
        else:
            if 'sold' in item['listingStatus'].lower():
                q = RealtorListingAll.update(
                    listingStatus=item.get('listingStatus')
                ).where(RealtorListingAll.originUrl == item['originUrl'])
                q.execute()
            else:
                q = RealtorListingAll.update(
                    listingStatus=item.get('listingStatus'),
                    purchasePrice=item.get('purchasePrice'),
                    mlsId=item.get('mlsId'),
                    zipCode=item.get('zipCode'),
                    daysOnMarket=item.get('daysOnMarket'),
                    yearBuilt=item.get('yearBuilt'),
                    beds=item.get('beds'),
                    baths=item.get('baths'),
                    sqft=item.get('sqft'),
                    lotSize=item.get('lotSize'),
                    photoCount=item.get('photoCount'),
                    listingUpdated=item.get('listingUpdated'),
                    openHouse=item.get('openHouse'),
                    propertyAddress=item.get('propertyAddress'),
                    agent=item.get('agent_id'),
                    officeName=item.get('officeName'),
                    officePhone=item.get('officePhone'),
                    agentMobile=item.get('agentMobile'),
                    agentName=item.get('agentName'),
                    medianDaysOnMarket=item.get('medianDaysOnMarket'),
                    daysOnRealtor=item.get('daysOnRealtor'),
                    propertyTax=item.get('propertyTax'),
                    lastSoldPrice=item.get('lastSoldPrice'),
                    modified=datetime.datetime.now()
                ).where(RealtorListingAll.originUrl == item['originUrl'])
                q.execute()
        return item

    def process_realtor_listing_for_julien_item(self, item, spider):
        try:
            RealtorListingJulien.get(RealtorListingJulien.originUrl == item['originUrl'])
        except RealtorListingJulien.DoesNotExist:
            try:
                listing = RealtorListingJulien.create(
                    originUrl=item.get('originUrl'),
                    agent=item.get('agent_id'),
                    agentName=item.get('agentName'),
                    agentMobile=item.get('agentMobile'),
                    status=item.get('status'),
                    soldDate=item.get('soldDate'),
                    worked=item.get('worked'),
                    beds=item.get('beds'),
                    baths=item.get('baths'),
                    sqft=item.get('sqft'),
                    lotSize=item.get('lotSize'),
                    photoCount=item.get('photoCount'),
                    purchasePrice=item.get('purchasePrice'),
                    currentPrice=item.get('currentPrice'),
                    propertyAddress=item.get('propertyAddress'),
                    zipCode=item.get('zipCode'),
                    moreExpensiveThanNearbyProperties=item.get('moreExpensiveThanNearbyProperties'),
                    lessExpensiveThanNearbyProperties=item.get('lessExpensiveThanNearbyProperties'),
                    daysOnMarket=item.get('daysOnMarket'),
                    soldHigherThanTheListedPrice=item.get('soldHigherThanTheListedPrice'),
                    soldLowerThanTheListedPrice=item.get('soldLowerThanTheListedPrice'),
                    pricePerSqFt=item.get('pricePerSqFt'),
                    propertyType=item.get('propertyType'),
                    yearBuilt=item.get('yearBuilt'),
                    medianListingPrice=item.get('medianListingPrice'),
                    medianSalePrice=item.get('medianSalePrice'),
                    medianDaysOnMarket=item.get('medianDaysOnMarket'),
                    averagePricePerSqFt=item.get('averagePricePerSqFt'),
                )

                if item.get('priceHistories'):
                    for idx, entry in enumerate(ast.literal_eval(item.get('priceHistories'))):
                        RealtorPriceHistoryForJulien.create(
                            listing=listing,
                            listingDate=entry.get('listingDate'),
                            purchasePrice=entry.get('purchasePrice'),
                            listingEvent=entry.get('listingEvent'),
                            listingSource=entry.get('listingSource'),
                        )

                if item.get('taxHistories'):
                    for idx, entry in enumerate(ast.literal_eval(item.get('taxHistories'))):
                        RealtorTaxHistoryForJulien.create(
                            listing=listing,
                            listingDate=entry.get('listingDate'),
                            taxPrice=entry.get('taxPrice'),
                        )

                if item.get('nearbyPriceHistories'):
                    for idx, entry in enumerate(ast.literal_eval(item.get('nearbyPriceHistories'))):
                        RealtorNearbyHistoryForJulien.create(
                            listing=listing,
                            nearbyPrice=entry.get('estimatePrice'),
                        )
            except Exception as e:
                print(e)
                pass
        else:
            q = RealtorListingJulien.update(
                status=item.get('status'),
                soldDate=item.get('soldDate'),
                worked=item.get('worked'),
                beds=item.get('beds'),
                baths=item.get('baths'),
                sqft=item.get('sqft'),
                lotSize=item.get('lotSize'),
                photoCount=item.get('photoCount'),
                purchasePrice=item.get('purchasePrice'),
                currentPrice=item.get('currentPrice'),
                propertyAddress=item.get('propertyAddress'),
                zipCode=item.get('zipCode'),
                moreExpensiveThanNearbyProperties=item.get('moreExpensiveThanNearbyProperties'),
                lessExpensiveThanNearbyProperties=item.get('lessExpensiveThanNearbyProperties'),
                daysOnMarket=item.get('daysOnMarket'),
                soldHigherThanTheListedPrice=item.get('soldHigherThanTheListedPrice'),
                soldLowerThanTheListedPrice=item.get('soldLowerThanTheListedPrice'),
                pricePerSqFt=item.get('pricePerSqFt'),
                propertyType=item.get('propertyType'),
                yearBuilt=item.get('yearBuilt'),
                medianListingPrice=item.get('medianListingPrice'),
                medianSalePrice=item.get('medianSalePrice'),
                medianDaysOnMarket=item.get('medianDaysOnMarket'),
                averagePricePerSqFt=item.get('averagePricePerSqFt'),
                modified=datetime.datetime.now()
            ).where(RealtorListingJulien.originUrl == item['originUrl'])
            q.execute()
        return item

    def process_realtor_listing_fix1_for_julien_item(self, item, spider):
        q = RealtorListingJulien.update(
            beds=item.get('beds'),
            baths=item.get('baths'),
        ).where(RealtorListingJulien.originUrl == item['originUrl'])
        q.execute()

        return item
