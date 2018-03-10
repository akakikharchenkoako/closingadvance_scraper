# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ListingItem(scrapy.Item):
    originUrl = scrapy.Field()
    propertyType = scrapy.Field()
    listingStatus = scrapy.Field()
    mlsId = scrapy.Field()
    zipCode = scrapy.Field()
    purchasePrice = scrapy.Field()
    daysOnMarket = scrapy.Field()
    yearBuilt = scrapy.Field()
    beds = scrapy.Field()
    baths = scrapy.Field()
    sqft = scrapy.Field()
    lotSize = scrapy.Field()
    photoCount = scrapy.Field()
    listingUpdated = scrapy.Field()
    openHouse = scrapy.Field()
    propertyAddress = scrapy.Field()
    priceHistories = scrapy.Field()


class TruliaListingItem(ListingItem):
    agentName = scrapy.Field()
    agentMobile = scrapy.Field()
    officeName = scrapy.Field()
    officePhone = scrapy.Field()


class ZillowListingItem(ListingItem):
    agent = scrapy.Field()
    officeName = scrapy.Field()
    officePhone = scrapy.Field()


class RedfinListingItem(ListingItem):
    pass


class RealtorListingItem(ListingItem):
    agent_id = scrapy.Field()
    officeName = scrapy.Field()
    officePhone = scrapy.Field()


class AgentItem(scrapy.Item):
    originUrl = scrapy.Field()
    brokerUrl = scrapy.Field()
    agentName = scrapy.Field()
    agentMobile = scrapy.Field()
    designation = scrapy.Field()
    activeListings = scrapy.Field()
    salesLast12Months = scrapy.Field()
    officeName = scrapy.Field()
    officePhone = scrapy.Field()
    officeAddress = scrapy.Field()
    location = scrapy.Field()


class ZillowAgentItem(AgentItem):
    pass


class BrokerItem(scrapy.Item):
    originUrl = scrapy.Field()
    brokerName = scrapy.Field()
    brokerTitle = scrapy.Field()
    brokerMobile = scrapy.Field()
    officeName = scrapy.Field()
    officePhone = scrapy.Field()
    officeAddress = scrapy.Field()
    location = scrapy.Field()


class ZillowBrokerItem(BrokerItem):
    pass


class RealtorBrokerItem(BrokerItem):
    teamUrl = scrapy.Field()
    search_keyword = scrapy.Field()
    brokerMobile2 = scrapy.Field()
    brokerMobile3 = scrapy.Field()
    brokerMobile4 = scrapy.Field()
    pass


class RealtorAgentItem(AgentItem):
    teamUrl = scrapy.Field()
    search_keyword = scrapy.Field()
    forSale = scrapy.Field()
    recentlySold = scrapy.Field()
    pass


class Century21AgentItem(scrapy.Item):
    agentUrl = scrapy.Field()
    agentName = scrapy.Field()
    agentPhone = scrapy.Field()
    agentMobile = scrapy.Field()
    officeName = scrapy.Field()
    officePhone = scrapy.Field()
    officeAddress = scrapy.Field()


class Century21OfficeItem(scrapy.Item):
    officeUrl = scrapy.Field()
    officeName = scrapy.Field()
    officePhone = scrapy.Field()
    officeAddress = scrapy.Field()
    officeWebsite = scrapy.Field()


class CompanyItem(scrapy.Item):
    url = scrapy.Field()
    name = scrapy.Field()
    address = scrapy.Field()
    phone = scrapy.Field()
    fax = scrapy.Field()
    email = scrapy.Field()
    website = scrapy.Field()
    categories = scrapy.Field()


class HomeClosingItem(scrapy.Item):
    url = scrapy.Field()
    name = scrapy.Field()
    address = scrapy.Field()
    phone = scrapy.Field()
    fax = scrapy.Field()
    email = scrapy.Field()
    website = scrapy.Field()
    categories = scrapy.Field()


class AttorneyItem(scrapy.Item):
    originUrl = scrapy.Field()
    name = scrapy.Field()
    address = scrapy.Field()
    phone = scrapy.Field()
    website = scrapy.Field()
    practice_areas = scrapy.Field()
    licensed_since = scrapy.Field()
    pictureUrl = scrapy.Field()


class BankInfoItem(scrapy.Item):
    routing_number = scrapy.Field()
    bank_name = scrapy.Field()
    address = scrapy.Field()
    city = scrapy.Field()
    state = scrapy.Field()
    zip_code = scrapy.Field()
    telephone = scrapy.Field()
    revision_date = scrapy.Field()


class LenderItem(scrapy.Item):
    link = scrapy.Field()
    name = scrapy.Field()
    address = scrapy.Field()
    cellPhone = scrapy.Field()
    officePhone = scrapy.Field()
    website = scrapy.Field()
    email = scrapy.Field()
