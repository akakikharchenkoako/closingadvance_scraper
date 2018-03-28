import re

from w3lib.html import remove_tags
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose, Join, Identity

from closingadvance_scraper.processors import serialize_number, to_datetime, acres_to_sqft


class ListingLoader(ItemLoader):
    default_input_processor = MapCompose(remove_tags, str.strip)
    default_output_processor = TakeFirst()

    agentMobile_in = MapCompose(serialize_number)
    officePhone_in = MapCompose(serialize_number)
    purchasePrice_in = MapCompose(serialize_number)
    photoCount_in = MapCompose(serialize_number)
    sqft_in = MapCompose(serialize_number)
    lotSize_in = MapCompose(acres_to_sqft)
    listingUpdated_in = MapCompose(to_datetime)
    agent_in = Identity()


class RealtorListingLoader(ItemLoader):
    default_input_processor = MapCompose(remove_tags, str.strip)
    default_output_processor = TakeFirst()
    agentMobile_in = MapCompose(serialize_number)
    officePhone_in = MapCompose(serialize_number)
    purchasePrice_in = MapCompose(serialize_number)
    photoCount_in = MapCompose(serialize_number)
    sqft_in = MapCompose(serialize_number)
    listingUpdated_in = MapCompose(to_datetime)
    agent_in = Identity()


class RealtorListingAllLoader(ItemLoader):
    default_input_processor = MapCompose(remove_tags, str.strip)
    default_output_processor = TakeFirst()
    agentMobile_in = MapCompose(serialize_number)
    officePhone_in = MapCompose(serialize_number)
    purchasePrice_in = MapCompose(serialize_number)
    photoCount_in = MapCompose(serialize_number)
    sqft_in = MapCompose(serialize_number)
    listingUpdated_in = MapCompose(to_datetime)
    agent_in = Identity()


class RealtorListingJulienLoader(ItemLoader):
    default_input_processor = MapCompose(remove_tags, str.strip)
    default_output_processor = TakeFirst()
    agentMobile_in = MapCompose(serialize_number)
    purchasePrice_in = MapCompose(serialize_number)
    photoCount_in = MapCompose(serialize_number)
    sqft_in = MapCompose(serialize_number)
    lotSize_in = MapCompose(serialize_number)
    agent_in = Identity()


class AgentLoader(ItemLoader):
    default_input_processor = MapCompose(remove_tags, str.strip)
    default_output_processor = TakeFirst()

    agentMobile_in = MapCompose(serialize_number)
    officePhone_in = MapCompose(serialize_number)


class BrokerLoader(ItemLoader):
    default_input_processor = MapCompose(remove_tags, str.strip)
    default_output_processor = TakeFirst()

    brokerMobile_in = MapCompose(serialize_number)
    officePhone_in = MapCompose(serialize_number)


class RealtorBrokerLoader(BrokerLoader):
    brokerMobile2_in = MapCompose(serialize_number)
    brokerMobile3_in = MapCompose(serialize_number)
    brokerMobile4_in = MapCompose(serialize_number)


class Century21AgentLoader(ItemLoader):
    default_input_processor = MapCompose(remove_tags, str.strip)
    default_output_processor = TakeFirst()

    agentPhone_in = MapCompose(serialize_number)
    agentMobile_in = MapCompose(serialize_number)
    officePhone_in = MapCompose(serialize_number)
    officeAddress_out = Join(', ')


class Century21OfficeLoader(ItemLoader):
    default_input_processor = MapCompose(remove_tags, str.strip)
    default_output_processor = TakeFirst()

    officePhone_in = MapCompose(serialize_number)
    officeAddress_out = Join(', ')


class CompanyLoader(ItemLoader):
    default_input_processor = MapCompose(remove_tags, str.strip)
    default_output_processor = TakeFirst()

    phone_in = MapCompose(serialize_number)
    fax_in = MapCompose(serialize_number)
    address_in = Join('')
    categories_in = Join(', ')


class AttorneyLoader(ItemLoader):
    default_input_processor = MapCompose(remove_tags, str.strip)
    default_output_processor = TakeFirst()

    phone_in = MapCompose(serialize_number)

