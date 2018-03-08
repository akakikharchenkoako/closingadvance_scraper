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
    teamUrl = CharField(null=True, unique=True)

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
    teamUrl = CharField(null=True, unique=True)
    originUrl = CharField(null=True, unique=True)
    created = DateTimeField(default=datetime.datetime.now)
    modified = DateTimeField(null=True)

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
    agentName = CharField(null=True)
    agentMobile = CharField(null=True, index=True)
    agentProfile = CharField(null=True, index=True)
    officeName = CharField(null=True)
    officePhone = CharField(null=True, index=True)
    verified = BooleanField(default=False, index=True)
    created = DateTimeField(default=datetime.datetime.now)
    modified = DateTimeField(null=True)

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
