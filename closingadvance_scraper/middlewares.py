# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html


from fake_useragent import UserAgent


class RandomUserAgentMiddleware(object):

    def __init__(self):
        super(RandomUserAgentMiddleware, self).__init__()

        self.ua = UserAgent()

    def process_request(self, request, spider):
        request.headers.setdefault('User-Agent', self.ua.random)
