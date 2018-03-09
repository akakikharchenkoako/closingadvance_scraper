from playhouse.migrate import *

from closingadvance_scraper.database import db

migrator = MySQLMigrator(db)

search_keyword = CharField(null=True)

migrate(
    migrator.add_column('realtor_agents', 'search_keyword', search_keyword),
)

migrate(
    migrator.add_column('realtor_brokers', 'search_keyword', search_keyword),
)
