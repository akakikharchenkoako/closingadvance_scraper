from peewee import *
from playhouse.shortcuts import RetryOperationalError
from scrapy.utils.project import get_project_settings


SETTINGS = get_project_settings()


class MyRetryDB(RetryOperationalError, MySQLDatabase):
    pass


db = MyRetryDB(
    host=SETTINGS['DB_HOST'],
    user=SETTINGS['DB_USER'],
    password=SETTINGS['DB_PASSWD'],
    port=int(SETTINGS['DB_PORT']),
    database=SETTINGS['DB_DB'],
    charset='utf8',
    use_unicode=True
)

