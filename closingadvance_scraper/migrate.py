from playhouse.migrate import *

from closingadvance_scraper.database import db

migrator = MySQLMigrator(db)

location = CharField(null=True, unique=True)

migrate(
    migrator.add_column('realtor_brokers', 'location', location),
)

migrate(
    migrator.add_column('realtor_agents', 'location', location),
)
