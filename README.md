# Scraper Guides

1. Export CSV from realtor_agents using following query before running realtor_listing_by_agent scraper
```
select count(b.id) from cag.realtor_brokers as a 
inner join cag.realtor_agents as b on a.officePhone= b.officePhone
where a.officePhone is not null and 
b.officePhone is not null and 
(a.brokerMobile is not null or a.brokerMobile2 is not null or a.brokerMobile3 is not null or a.brokerMobile4 is not null)
```
```
select * from cag.realtor_agents as a
inner join cag.realtor_brokers as b on a.officePhone = b.officePhone
where a.officePhone is not null and b.officePhone is not null and 
(b.brokerMobile is not null or b.brokerMobile2 is not null or b.brokerMobile3 is not null or b.brokerMobile4 is not null)
```
I have to confirm following:
```
        if listing_status:
            if 'active' in listing_status.lower():
                listing_status = 'Active'
            elif 'new' in listing_status.lower():
                listing_status = 'New'
            elif 'sold' in listing_status.lower():
                listing_status = 'Sold'
            elif 'for sale' in listing_status.lower():
                listing_status = 'For Sale'
            elif 'pending' in listing_status.lower():
                listing_status = 'Pending'
            elif "under contract" in listing_status.lower():
                listing_status = 'Under Contract'
            elif "contingent" in listing_status.lower():
                listing_status = 'Contingent'
            else:
                listing_status = None
```
And realtor_listing_by_agent scraper uses this csv file as an input.
This file should contain columns like id 
