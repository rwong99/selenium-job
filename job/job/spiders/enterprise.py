# -*- coding: utf-8 -*-
import platform
import re

import requests
import time
import random
import json

import scrapy

from job.items import CompanyItem

from job.utils.corpcrawl import *
from job.utils.common import company_info
from scrapy import Request


class EnterPriseSpider(scrapy.Spider):
    name = 'enterprise'
    allowed_domains = ['gsxt.gov.cn']
    start_urls = ['http://www.gsxt.gov.cn/index.html']

    def __init__(self, word=None, *args, **kwargs):
        super(eval(self.__class__.__name__), self).__init__(*args, **kwargs)
        self.word = word

    def start_requests(self):
        init_url = "http://www.gsxt.gov.cn/SearchItemCaptcha"
        index_url = "http://www.gsxt.gov.cn/index.html"
        base_url = 'http://www.gsxt.gov.cn'
        result_parse_rule = {'search_result_url': '//*[@id="advs"]/div/div[2]/a/@href'}


        max_click = 10
        chm_headers = ['Host="www.gsxt.gov.cn"',
                       'Connection="keep-alive"',
                       'User-Agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"',
                       'Upgrade-Insecure-Requests=1',
                       'Accept="text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"',
                       'Accept-Encoding="gzip, deflate"',
                       'Accept-Language="zh-CN,zh;q=0.9"']

        search = CorpSearch(init_url, index_url, chm_headers, max_click)
        search.main(self.word)
        cookie_html = search.to_dict()
        search_result = SearchResultParse(cookie_html['page'], base_url, result_parse_rule)
        url_list = search_result.search_result_parse()


        yield Request(url="https://www.baidu.com/",callback=self.parse,
                      meta={'url_list': url_list})

    def parse(self, response):
        detail_parse_rule = {
            'primaryinfo': ['string(//*[@id="primaryInfo"]/div/div[@class="overview"]/dl[{}])'.format(i) for i in
                            range(15)], }
        url_list = response.meta.get("url_list", "")
        detail_request = CookieRequest(url_list=url_list)
        detail_result = detail_request.cookie_requests()
        for pg in detail_result:
            pg_detail = PageDetailParse(pg, detail_parse_rule)
            detail = pg_detail.search_result_parse()
            m = re.findall(r'\[(.*?)\]', str(detail))
            info_list = m[0].replace('\'', '').split(', ')
            item = CompanyItem()
            item['name'] = company_info(info_list, "企业名称：")
            item['code'] = company_info(info_list, "统一社会信用代码：")
            item['type'] = company_info(info_list, "类型：")

            start = company_info(info_list, "营业期限自：")
            partner_start = company_info(info_list, "合伙期限自：")
            item['start'] = start if "无" == partner_start else partner_start
            end = company_info(info_list, "合伙期限自：")
            partner_end = company_info(info_list, "合伙期限至：")
            item['end'] = end if "无" == partner_end else partner_end

            item['capital'] = company_info(info_list, "注册资本：")
            item['owner'] = company_info(info_list, "法定代表人：")
            item['establish'] = company_info(info_list, "成立日期：")
            item['registration'] = company_info(info_list, "登记机关：")
            item['check'] = company_info(info_list, "核准日期：")
            item['status'] = company_info(info_list, "登记状态：")
            address1 = company_info(info_list, "住所：")
            address2 = company_info(info_list, "主要经营场所：")
            address3 = company_info(info_list, "营业场所：")
            if address1 != "无":
                item['address'] = address1
            elif address2 != "无":
                item['address'] = address2
            else:
                item['address'] = address3
            item['scope'] = company_info(info_list, "经营范围：")
            item['partner'] = company_info(info_list, "执行事务合伙人:")
            yield item
