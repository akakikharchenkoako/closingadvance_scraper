import re
import datetime

from closingadvance_scraper.database import db
from closingadvance_scraper.models import Agent, Broker, ZillowAgent, ZillowBroker, Company, Attorney, BrokerOffice # noqa


def aggregate_agent_profile():
    db.connect()
    db.create_tables([Agent], safe=True)

    for row in ZillowAgent.select().where(ZillowAgent.agentMobile.is_null(False), ZillowAgent.activeListings.is_null(False), ZillowAgent.salesLast12Months.is_null(False), ZillowAgent.created >= '2018-02-13'):
        try:
            Agent.get(Agent.originUrl == row.originUrl)
        except Agent.DoesNotExist:
            Agent.create(
                originUrl=row.originUrl,
                brokerUrl=row.brokerUrl,
                agentName=row.agentName,
                designation=row.designation,
                agentMobile=row.agentMobile,
                activeListings=row.activeListings,
                salesLast12Months=row.salesLast12Months,
                officeName=row.officeName,
                officePhone=row.officePhone,
                officeAddress=row.officeAddress,
                location=row.location,
            )
            print('Added %s' % row.originUrl)
        else:
            q = Agent.update(
                originUrl=row.originUrl,
                brokerUrl=row.brokerUrl,
                agentName=row.agentName,
                designation=row.designation,
                agentMobile=row.agentMobile,
                activeListings=row.activeListings,
                salesLast12Months=row.salesLast12Months,
                officeName=row.officeName,
                officePhone=row.officePhone,
                officeAddress=row.officeAddress,
                location=row.location,
            ).where(Agent.originUrl == row.originUrl)
            q.execute()
            print('Updated %s' % row.originUrl)


def aggregate_broker_profile():
    db.connect()
    db.create_tables([Broker], safe=True)

    for row in ZillowBroker.select().where(ZillowBroker.brokerMobile.is_null(False)):
        try:
            Broker.get(Broker.originUrl == row.originUrl)
        except Broker.DoesNotExist:
            Broker.create(
                originUrl=row.originUrl,
                brokerName=row.brokerName,
                brokerTitle=row.brokerTitle,
                brokerMobile=row.brokerMobile,
                officeName=row.officeName,
                officePhone=row.officePhone,
                officeAddress=row.officeAddress,
                location=row.location,
            )
            print('Added %s' % row.originUrl)
        else:
            q = Broker.update(
                originUrl=row.originUrl,
                brokerName=row.brokerName,
                brokerTitle=row.brokerTitle,
                brokerMobile=row.brokerMobile,
                officeName=row.officeName,
                officePhone=row.officePhone,
                officeAddress=row.officeAddress,
                location=row.location,
            ).where(Broker.originUrl == row.originUrl)
            q.execute()
            print('Updated %s' % row.originUrl)


def aggregate_closing_company():
    for row in Attorney.select().where(Attorney.phone.is_null(False)):
        try:
            Company.get(Company.url == row.originUrl)
        except Company.DoesNotExist:
            Company.create(
                url=row.originUrl,
                name=row.name,
                address=row.address,
                phone=row.phone,
                fax=row.fax,
                website=row.website,
                categories=row.practice_areas
            )
            print('Added %s' % row.originUrl)
        else:
            q = Company.update(
                url=row.originUrl,
                name=row.name,
                address=row.address,
                phone=row.phone,
                fax=row.fax,
                website=row.website,
                categories=row.practice_areas,
                modified=datetime.datetime.now()
            ).where(Company.url == row.originUrl)
            q.execute()

            print('Updated %s' % row.originUrl)


def aggregate_attorneys():
    db.connect()
    db.create_tables([Attorney, Company], safe=True)

    for row in Attorney.select():
        try:
            Company.get(Company.url == row.originUrl)
        except Company.DoesNotExist:
            Company.create(
                url=row.originUrl,
                name=row.name,
                phone=row.phone,
                address=row.address,
                website=row.website,
            )
            print('Added %s' % row.originUrl)
        else:
            q = Company.update(
                url=row.originUrl,
                name=row.name,
                phone=row.phone,
                address=row.address,
                website=row.website,
                modified=datetime.datetime.now()
            ).where(Company.url == row.originUrl)
            q.execute()

            print('Updated %s' % row.originUrl)


def aggregate_broker_office():
    db.connect()
    db.create_tables([BrokerOffice], safe=True)

    for row in Company.select().where(Company.phone.is_null(False), Company.url.contains('yellowpages'), Company.categories.contains('Brokers')):
        try:
            BrokerOffice.get(BrokerOffice.url == row.url)
        except BrokerOffice.DoesNotExist:
            BrokerOffice.create(
                url=row.url,
                name=row.name,
                phone=row.phone,
                address=row.address,
                website=row.website,
                fax=row.fax,
                email=row.email,
            )
            print('Added %s' % row.url)
        else:
            q = BrokerOffice.update(
                url=row.url,
                name=row.name,
                phone=row.phone,
                address=row.address,
                website=row.website,
                fax=row.fax,
                email=row.email,
                modified=datetime.datetime.now()
            ).where(BrokerOffice.url == row.url)
            q.execute()

            print('Updated %s' % row.url)


def aggregate_broker_all():
    db.connect()
    db.create_tables([BrokerOffice], safe=True)

    for row in BrokerOffice.select().where(BrokerOffice.phone.is_null(False)):
        try:
            Broker.get(Broker.brokerMobile == row.phone | Broker.officePhone == row.phone)
        except Broker.DoesNotExist:
            Broker.create(
                originUrl=row.url,
                officeName=row.name,
                officePhone=row.phone,
                officeAddress=row.address,
            )
            print('Added %s' % row.url)
        else:
            q = Broker.update(
                originUrl=row.url,
                officeName=row.name,
                officePhone=row.phone,
                officeAddress=row.address,
                modified=datetime.datetime.now()
            ).where(Broker.brokerMobile == row.phone | Broker.officePhone == row.phone)
            q.execute()
            print('Updated %s' % row.url)


def analyze_sale_pending():
    cursor = db.execute_sql('select distinct z.id from zillow_listings z inner join price_histories  p on p.listing_id=z.id where p.listingDate >= "2017-08-01" and p.listingEvent="Pending sale" and z.mlsid is not null;')
    total_pending = 0
    back_to_market = 0
    for row in cursor.fetchall():
        total_pending += 1
        events = db.execute_sql('select listingEvent from price_histories where listing_id = %s order by listingDate desc;' % row[0]).fetchall()
        for event in events:
            if 'Back on market' == event[0]:
                back_to_market += 1

    print('total_pending', total_pending)
    print('back_to_market', back_to_market)


if __name__ == '__main__':
    aggregate_agent_profile()
    aggregate_broker_profile()
    # aggregate_closing_company()
    # aggregate_broker_office()
    # deduplicate_homeclosing()
    # analyze_sale_pending()
    # aggregate_attorneys()
    # aggregate_broker_all()

