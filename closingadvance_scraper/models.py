import datetime

from peewee import *

from closingadvance_scraper.database import db


class Agent(Model):
    originUrl = CharField(null=True, unique=True)
    brokerUrl = CharField(null=True, index=True)
    agentName = CharField(null=True)
    designation = CharField(null=True)
    agentMobile = CharField(null=True, index=True)
    activeListings = IntegerField(null=True, index=True)
    salesLast12Months = IntegerField(null=True, index=True)
    officeName = CharField(null=True)
    officePhone = CharField(null=True, index=True)
    officeAddress = CharField(null=True)
    location = CharField(null=True)
    created = DateTimeField(default=datetime.datetime.now)
    modified = DateTimeField(null=True)

    class Meta:
        db_table = 'agents'
        database = db


class RealtorAgent(Agent):
    teamUrl = CharField(null=True)
    search_keyword = CharField(null=True)
    forSale = IntegerField(null=True)
    recentlySold = IntegerField(null=True)

    class Meta:
        db_table = 'realtor_agents'
        database = db


class ZillowAgent(Agent):

    class Meta:
        db_table = 'zillow_agents'
        database = db


class Broker(Model):
    originUrl = CharField(null=True, unique=True)
    brokerName = CharField(null=True)
    brokerTitle = CharField(null=True)
    brokerMobile = CharField(null=True, index=True)
    officeName = CharField(null=True)
    officePhone = CharField(null=True, index=True)
    officeAddress = CharField(null=True)
    location = CharField(null=True)

    class Meta:
        db_table = 'brokers_all'
        database = db


class ZillowBroker(Broker):
    created = DateTimeField(default=datetime.datetime.now)
    modified = DateTimeField(null=True)

    class Meta:
        db_table = 'zillow_brokers'
        database = db


class RealtorBroker(Broker):
    id = IntegerField(null=False, primary_key=True)
    teamUrl = CharField(null=True)
    search_keyword = CharField(null=True)
    created = DateTimeField(default=datetime.datetime.now)
    modified = DateTimeField(null=True)
    brokerMobile2 = CharField(null=True, index=True)
    brokerMobile3 = CharField(null=True, index=True)
    brokerMobile4 = CharField(null=True, index=True)

    class Meta:
        db_table = 'realtor_brokers'
        database = db


class Listing(Model):
    originUrl = CharField(null=True, unique=True)
    listingStatus = CharField(null=True, index=True)
    listingUpdated = DateField(null=True)
    openHouse = CharField(null=True)
    mlsId = CharField(null=True, index=True)
    zipCode = CharField(null=True)
    yearBuilt = IntegerField(null=True)
    sqft = IntegerField(null=True)
    lotSize = IntegerField(null=True)
    beds = FloatField(null=True)
    baths = FloatField(null=True)
    photoCount = IntegerField(null=True)
    daysOnMarket = IntegerField(null=True)
    purchasePrice = CharField(null=True)
    propertyAddress = CharField(null=True)


class TruliaListing(Listing):
    agentName = CharField(null=True)
    agentMobile = CharField(null=True, index=True)
    officeName = CharField(null=True)
    officePhone = CharField(null=True, index=True)
    verified = BooleanField(default=False, index=True)
    created = DateTimeField(default=datetime.datetime.now)
    modified = DateTimeField(null=True)

    class Meta:
        db_table = 'trulia_listings'
        database = db


class RealtorListing(Listing):
    agent = ForeignKeyField(RealtorAgent)
    officeName = CharField(null=True)
    officePhone = CharField(null=True)
    created = DateTimeField(default=datetime.datetime.now)
    modified = DateTimeField(null=True)
    propertyTax = CharField(null=True)
    medianDaysOnMarket = IntegerField(null=True)
    daysOnMarket = IntegerField(null=True)
    daysOnRealtor = IntegerField(null=True)
    lastSoldPrice = CharField(null=True)
    agentName = CharField(null=True)
    agentMobile = CharField(null=True)

    class Meta:
        db_table = 'realtor_listings'
        database = db


class ZillowListing(Listing):
    agent = ForeignKeyField(Agent)
    officeName = CharField(null=True)
    officePhone = CharField(null=True)
    created = DateTimeField(default=datetime.datetime.now)
    modified = DateTimeField(null=True)

    class Meta:
        db_table = 'zillow_listings'
        database = db


class Century21Agent(Model):
    originUrl = CharField(null=True, unique=True)
    agentName = CharField(null=True, index=True)
    agentPhone = CharField(null=True, index=True)
    agentMobile = CharField(null=True, index=True)
    officeName = CharField(null=True)
    officePhone = CharField(null=True)
    officeAddress = CharField(null=True)
    created = DateTimeField(default=datetime.datetime.now)
    modified = DateTimeField(null=True)

    class Meta:
        db_table = 'century21_agents'
        database = db


class Century21Office(Model):
    officeUrl = CharField(null=True, unique=True)
    officeName = CharField(null=True, index=True)
    officePhone = CharField(null=True, index=True)
    officeAddress = CharField(null=True)
    officeWebsite = CharField(null=True)
    created = DateTimeField(default=datetime.datetime.now)
    modified = DateTimeField(null=True)

    class Meta:
        db_table = 'century21_offices'
        database = db


class Company(Model):
    url = CharField(null=True, unique=True)
    name = CharField(null=True)
    address = CharField(null=True)
    phone = CharField(null=True, index=True)
    fax = CharField(null=True)
    email = CharField(null=True)
    website = CharField(null=True)
    categories = TextField(null=True)
    created = DateTimeField(default=datetime.datetime.now)
    modified = DateTimeField(null=True)

    class Meta:
        db_table = 'title_companies'
        database = db


class Deal(Model):
    loanrequestID = IntegerField(null=True, primary_key=True)
    closingDate = CharField(null=True)
    advanceAmount = CharField(null=True)
    netCommission = IntegerField(null=True)
    propertyUrl = CharField(null=True)
    propertyAddress = CharField(null=True)
    mlsId = CharField(null=True)
    agentName = CharField(null=True)
    agentEmail = CharField(null=True)
    agentPhone = CharField(null=True)
    brokerEmail = CharField(null=True)
    brokerPhone = CharField(null=True)
    pipedriveId = IntegerField(null=True)
    created = DateTimeField(null=True)
    modified = DateTimeField(null=True)

    class Meta:
        db_table = 'loanrequests'
        database = db


class PriceHistory(Model):
    id = CharField(null=False, primary_key=True, max_length=11)
    listing = ForeignKeyField(ZillowListing)
    listingDate = DateField(null=True)
    listingEvent = CharField(null=True)
    purchasePrice = IntegerField(null=True)
    listingAgent = CharField(null=True)
    listingSource = CharField(null=True)
    created = DateTimeField(default=datetime.datetime.now)
    modified = DateTimeField(null=True)

    class Meta:
        db_table = 'price_histories'
        database = db


class Attorney(Model):
    originUrl = CharField(null=True, unique=True)
    name = CharField(null=True)
    address = CharField(null=True)
    phone = CharField(null=True)
    website = CharField(null=True)
    practice_areas = CharField(null=True)
    licensed_since = IntegerField(null=True)
    pictureUrl = CharField(null=True)
    created = DateTimeField(default=datetime.datetime.now)
    modified = DateTimeField(null=True)

    class Meta:
        db_table = 'attorneys'
        database = db


class BrokerOffice(Model):
    url = CharField(null=True, unique=True)
    name = CharField(null=True)
    phone = CharField(null=True, index=True)
    fax = CharField(null=True, index=True)
    email = CharField(null=True)
    website = CharField(null=True)
    address = CharField(null=True)
    created = DateTimeField(default=datetime.datetime.now)
    modified = DateTimeField(null=True)

    class Meta:
        db_table = 'broker_offices'
        database = db


class BankInfo(Model):
    routing_number = CharField(null=False, unique=True)
    bank_name = CharField(null=True)
    address = CharField(null=True)
    state = CharField(null=True)
    city = CharField(null=True)
    zip_code = CharField(null=True)
    telephone = CharField(null=True)
    revision_date = CharField(null=True)
    created = DateTimeField(default=datetime.datetime.now)
    modified = DateTimeField(null=True)

    class Meta:
        db_table = 'bank_info'
        database = db


class Lender(Model):
    link = CharField(null=False, unique=True)
    name = CharField(null=False)
    address = CharField(null=True)
    cellPhone = CharField(null=True, index=True)
    officePhone = CharField(null=True, index=True)
    website = CharField(null=True)
    email = CharField(null=True)
    created = DateTimeField(default=datetime.datetime.now)
    modified = DateTimeField(null=True)

    class Meta:
        db_table = 'lenders'
        database = db


class RealtorPriceHistory(Model):
    id = CharField(null=False, primary_key=True, max_length=11)
    listing = ForeignKeyField(RealtorListing)
    listingDate = DateField(null=True)
    listingEvent = CharField(null=True)
    purchasePrice = IntegerField(null=True)
    listingAgent = CharField(null=True)
    listingSource = CharField(null=True)
    created = DateTimeField(default=datetime.datetime.now)
    modified = DateTimeField(null=True)

    class Meta:
        db_table = 'realtor_price_histories'
        database = db


class ListingStatus(Model):
    status = CharField(null=False, unique=True)

    class Meta:
        db_table = 'listingStatus'
        database = db


class RealtorListingAll(Listing):
    agent = ForeignKeyField(RealtorAgent)
    officeName = CharField(null=True)
    officePhone = CharField(null=True)
    created = DateTimeField(default=datetime.datetime.now)
    modified = DateTimeField(null=True)
    propertyTax = CharField(null=True)
    medianDaysOnMarket = IntegerField(null=True)
    daysOnMarket = IntegerField(null=True)
    daysOnRealtor = IntegerField(null=True)
    lastSoldPrice = CharField(null=True)
    agentName = CharField(null=True)
    agentMobile = CharField(null=True)

    class Meta:
        db_table = 'realtor_listings_all'
        database = db


class RealtorListinBroker(Listing):
    listing = ForeignKeyField(RealtorListing)
    broker = ForeignKeyField(RealtorBroker)

    class Meta:
        db_table = 'realtor_listing_broker'
        database = db


class RealtorListingJulien(Model):
    agent = ForeignKeyField(RealtorAgent)
    originUrl = CharField(null=True)
    agentName = CharField(null=True)
    agentMobile = CharField(null=True)
    status = CharField(null=True)
    soldDate = DateField(null=True)
    worked = CharField(null=True)
    beds = IntegerField(null=True)
    baths = IntegerField(null=True)
    sqft = IntegerField(null=True)
    lotSize = IntegerField(null=True)
    photoCount = IntegerField(null=True)
    purchasePrice = FloatField(null=True)
    currentPrice = FloatField(null=True)
    propertyAddress = CharField(null=True)
    zipCode = CharField(null=True)
    moreExpensiveThanNearbyProperties = FloatField(null=True)
    lessExpensiveThanNearbyProperties = FloatField(null=True)
    daysOnMarket = IntegerField(null=True)
    soldHigherThanTheListedPrice = FloatField(null=True)
    soldLowerThanTheListedPrice = FloatField(null=True)
    pricePerSqFt = FloatField(null=True)
    propertyType = CharField(null=True)
    yearBuilt = IntegerField(null=True)
    medianListingPrice = FloatField(null=True)
    medianSalePrice = FloatField(null=True)
    medianDaysOnMarket = IntegerField(null=True)
    averagePricePerSqFt = FloatField(null=True)
    created = DateTimeField(default=datetime.datetime.now)
    modified = DateTimeField(null=True)

    class Meta:
        db_table = 'realtor_listings_julien'
        database = db


class RealtorPriceHistoryForJulien(Model):
    listing = ForeignKeyField(RealtorListingJulien)
    listingDate = DateField(null=True)
    listingEvent = CharField(null=True)
    purchasePrice = IntegerField(null=True)
    listingSource = CharField(null=True)

    class Meta:
        db_table = 'realtor_price_histories_julien'
        database = db


class RealtorTaxHistoryForJulien(Model):
    listing = ForeignKeyField(RealtorListingJulien)
    listingDate = CharField(null=True)
    taxPrice = IntegerField(null=True)

    class Meta:
        db_table = 'realtor_tax_histories_julien'
        database = db


class RealtorNearbyHistoryForJulien(Model):
    listing = ForeignKeyField(RealtorListingJulien)
    nearbyPrice = IntegerField(null=True)

    class Meta:
        db_table = 'realtor_nearby_histories_julien'
        database = db
