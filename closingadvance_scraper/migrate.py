from playhouse.migrate import *

from closingadvance_scraper.database import db

migrator = MySQLMigrator(db)

Fax = CharField(null=True, unique=True)

migrate(
    migrator.add_column('realtor_agents', 'fax', Fax),
)

migrate(
    migrator.add_column('realtor_brokers', 'fax', Fax),
)

