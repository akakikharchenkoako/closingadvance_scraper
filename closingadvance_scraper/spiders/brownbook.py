# -*- coding: utf-8 -*-

import scrapy
from closingadvance_scraper.items import BrownBookItem
from closingadvance_scraper.loaders import BrownBookLoader


class BrownBookSpider(scrapy.Spider):
    name = 'brownbook'
    allowed_domains = ['www.brownbook.net']
    start_url = 'http://www.brownbook.net/united-states/categories'

    def start_requests(self):
        yield scrapy.Request(self.start_url, callback=self.parse_categories_list_page)

    def parse_categories_list_page(self, response):
        for category_link in response.xpath('//div[@id="promo_full"]//table//td/a/@href').extract():
            yield response.follow(category_link, self.parse_category_page, cookies={'setcountry': 'us'})

    def parse_category_page(self, response):
        business_infos_list = []

        for business_block in response.xpath('//div[@id="business_inner"]//div[@class="h-card vcard"]'):
            l = BrownBookLoader(item=BrownBookItem(), response=response)

            is_summary_view = business_block.xpath('.//img[@alt="This is my business"]')

            if is_summary_view:
                yield response.follow(business_block.xpath('.//h2[contains(@class, "business_sub_head_title")]/a/@href').extract_first(), self.parse_business_page, cookies={'setcountry': 'us'})
            else:
                business_info = {}

                business_info['title'] = business_block.xpath('.//h2[contains(@class, "business_sub_head_title")]//span/text()').extract_first()
                business_info['link'] = business_block.xpath('.//h2[contains(@class, "business_sub_head_title")]/a/@href').extract_first()
                business_info['address'] = " " . join(business_block.xpath('.//td[@class="adr"]/a[1]//span/text()').extract())
                business_info['telephone'] = business_block.xpath('.//span[@class="tel p-tel"]/text()').extract_first()
                business_info['mobile'] = business_block.xpath('.//span[@class="tel p-tel-mobile"]/text()').extract_first()
                business_info['email'] = business_block.xpath('.//a[contains(@class, "p-email")]/text()').extract_first()
                business_info['website'] = business_block.xpath('.//a[contains(@class, "bb_website")]/@href').extract_first()
                business_info['business_tags'] = "," .join(business_block.xpath('.//div[@class="category listingtags clearfix"]'
                                                                      '//b[text()="Business tags:"]/..'
                                                                      '/following-sibling::*[1]'
                                                                      '/span[@class="p-category"]/text()').extract())

                print(business_info["link"])
                print(business_info)

                for key in business_info:
                    l.add_value(key, business_info[key])

                yield l.load_item()

        next_page_link = response.xpath('//div[@class="pages"]/a[@class="standardlink" and contains(text(), "next page")]/@href').extract_first()

        if next_page_link:
            yield response.follow(next_page_link, self.parse_category_page, cookies={'setcountry': 'us'})

    def parse_business_page(self, response):
        l = BrownBookLoader(item=BrownBookItem(), response=response)

        business_info = {}

        business_info['title'] = response.xpath(
            '//h1[@class="business_sub_head_title"]/span/text()').extract_first()
        business_info['link'] = response.url
        business_info['address'] = " " .join(response.xpath(
            '//div[@class="business_listingbox"]/div[@class="adr"]//span/text()').extract())
        business_info['telephone'] = response.xpath('//div[@class="business_listingbox"]/span[@class="tel"]'
                                                    '/span[@class="business_details p-tel"]/text()').extract_first()
        business_info['mobile'] = response.xpath('//div[@class="business_listingbox"]/span[@class="tel"]'
                                                    '/span[@class="business_details p-tel-mobile"]/text()').extract_first()
        business_info['email'] = response.xpath('//div[@class="business_listingbox"]/div[@class="email"]'
                                                '/a/text()').extract_first()
        business_info['website'] = response.xpath('//div[@class="business_listingbox"]'
                                                  '//a[@class="standardlink actOn url bb_website"]/@href').extract_first()
        business_info['business_tags'] = ",".join(response.xpath('.//div[@id="promo_hatch_inner"]'
                                                                 '//b[text()="Business Tags"]/../..'
                                                                 '/following-sibling::*[1]'
                                                                 '/a[@class="standardlink p-category"]/text()').extract())

        print(business_info["link"])
        print(business_info)

        for key in business_info:
            l.add_value(key, business_info[key])

        yield l.load_item()
