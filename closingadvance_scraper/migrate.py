from playhouse.migrate import *

from closingadvance_scraper.database import db

migrator = MySQLMigrator(db)

teamUrl = CharField(null=True)
location = CharField(null=True)
brokerMobile2 = CharField(null=True)
brokerMobile3 = CharField(null=True)
brokerMobile4 = CharField(null=True)

migrate(
    migrator.add_column('realtor_brokers', 'teamUrl', teamUrl),
)

migrate(
    migrator.add_column('realtor_brokers', 'location', location),
)

migrate(
    migrator.add_column('realtor_brokers', 'brokerMobile2', brokerMobile2),
)

migrate(
    migrator.add_column('realtor_brokers', 'brokerMobile3', brokerMobile3),
)

migrate(
    migrator.add_column('realtor_brokers', 'brokerMobile4', brokerMobile4),
)


forSale = IntegerField(null=True)
recentlySold = IntegerField(null=True)
brokerUrl = CharField(null=True)

migrate(
    migrator.add_column('realtor_agents', 'teamUrl', teamUrl),
)

migrate(
    migrator.add_column('realtor_agents', 'brokerUrl', brokerUrl),
)

migrate(
    migrator.add_column('realtor_agents', 'location', location),
)

migrate(
    migrator.add_column('realtor_agents', 'forSale', forSale),
)

migrate(
    migrator.add_column('realtor_agents', 'recentlySold', recentlySold),
)
