from datetime import datetime, timedelta

from closingadvance_scraper.models import TruliaListing as Listing, Agent


def main():
    today = datetime.now()
    last_week = today - timedelta(days=7)
    realtor_count = 0
    zillow_count = 0
    total = Listing.select().where(
                Listing.listingStatus == 'Pending',
                Listing.agentMobile.is_null(False),
                Listing.created.between(last_week, today)).count()
    for listing in Listing.select().where(
            Listing.listingStatus == 'Pending',
            Listing.agentMobile.is_null(False),
            Listing.created.between(last_week, today)):
        try:
            row = Agent.get(Agent.agentMobile == listing.agentMobile)
            if row.salesLast12Months is not None and row.salesLast12Months > 0:
                Listing.update(verified=True).where(Listing.originUrl == listing.originUrl).execute()
                print('Verified %s' % row.originUrl)
                if 'realtor' in row.originUrl:
                    realtor_count += 1
                else:
                    zillow_count += 1
        except Agent.DoesNotExist:
            # print('Agent not found %s' % listing.originUrl)
            pass
    print('total listing', total)
    print('total verified ', realtor_count + zillow_count)
    print('realtor count ', realtor_count)
    print('zillow count ', zillow_count)


if __name__ == '__main__':
    main()

