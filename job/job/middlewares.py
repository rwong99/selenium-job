# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from fake_useragent import UserAgent
import browsercookie
from scrapy.downloadermiddlewares.cookies import CookiesMiddleware


class RandomUserAgentMiddleware(object):
    def process_request(self, request, spider):
        ua = UserAgent()
        request.headers['User-Agent'] = ua.random



class BrowserCookiesDownloaderMiddleware(CookiesMiddleware):
    """
    创建一个DownloaderMiddleware调用browsercookie获取浏览器cookies
    继承自scrapy内置的CookiesMiddleware
    在settings中禁用CookiesMiddleware，启用自定义的DownloaderMiddleware
    在发送Request时，加入参数 meta={'cookiejar':COOKIEJAR}
    """
    def __init__(self, debug=False):
        super().__init__(debug)
        self.load_browser_cookies()

    def load_browser_cookies(self):
        jar = self.jars['chrome']
        chrome_cookies = browsercookie.chrome()
        for cookie in chrome_cookies:
            jar.set_cookie(cookie)