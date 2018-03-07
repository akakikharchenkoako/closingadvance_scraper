from playhouse.migrate import *

from closingadvance_scraper.database import db

migrator = MySQLMigrator(db)


verified = BooleanField(default=False, index=True)


migrate(
    migrator.add_column('trulia_listings', 'verified', verified),
)

