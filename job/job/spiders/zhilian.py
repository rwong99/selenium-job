# -*- coding: utf-8 -*-
import json
import platform
import time
from datetime import datetime
from urllib import parse

import scrapy
from fake_useragent import UserAgent
from lxml import etree
from scrapy import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait

from job.items import *

from job.utils.common import *


class ZhilianSpider(scrapy.Spider):
    name = 'zhilian'
    allowed_domains = ['zhaopin.com']
    start_urls = ['https://sou.zhaopin.com/']

    driver = None
    chrome_options = webdriver.ChromeOptions()
    # proxy_url = get_random_proxy()
    # print(proxy_url + "代理服务器正在爬取")
    # chrome_options.add_argument('--proxy-server=https://' + proxy_url.strip())
    prefs = {
        'profile.default_content_setting_values': {
            'images': 1,  # 不加载图片
            "User-Agent": UserAgent().random,  # 更换UA
        }
    }
    chrome_options.add_experimental_option("prefs", prefs)
    if platform.system() == "Windows":
        driver = webdriver.Chrome('chromedriver.exe', chrome_options=chrome_options)
    elif platform.system() == "Linux":
        chrome_options.add_argument("--headless")
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        driver = webdriver.Chrome(
            executable_path="/usr/bin/chromedriver",
            chrome_options=chrome_options)
    wait = WebDriverWait(driver, 15)

    def start_requests(self):
        data = ["游戏", "期货", "贷款"]
        for kw in data:
            yield Request(
                url="https://fe-api.zhaopin.com/c/i/sou?start=0&pageSize=90&cityId=639&salary=0,0&workExperience=-1&education=-1&companyType=-1&employmentType=-1&jobWelfareTag=-1&kw=" + kw + "&kt=3",
                meta={"kw": kw},
                callback=self.parse_pages)  # response获取meta

    def parse_pages(self, response):
        numtotal = json.loads(response.text)["data"]["count"]
        kw = response.meta.get("kw", "游戏")
        for i in range(0, numtotal // 90 + 1):
            url = "https://fe-api.zhaopin.com/c/i/sou?start=" + str(
                90 * i) + "&pageSize=90&cityId=639&salary=0,0&workExperience=-1&education=-1&companyType=-1&employmentType=-1&jobWelfareTag=-1&kw=" + kw + "&kt=3"
            yield Request(
                url=url,
                meta={"kw": kw},
                callback=self.parse)  # response获取meta

    def parse(self, response):
        job_list = json.loads(response.text)["data"]["results"]
        for job in job_list:
            yield Request(url=job["positionURL"], callback=self.parse_detail,
                          meta={'cookiejar': 'chrome', 'kw': response.meta.get("kw", "")})

    def parse_detail(self, response):
        print(response.url)
        self.driver.get(response.url)
        self.driver.refresh()
        time.sleep(5)
        self.driver.implicitly_wait(20)
        dom = etree.HTML(self.driver.page_source)
        item = JobItem()
        item['source'] = "智联招聘"
        item['recruitment_position'] = null_if(dom.xpath('//*[@class="summary-plane__title"]'))
        item['update_date'] = dom.xpath('//span[@class="summary-plane__time"]/text()')[0]
        item['salary'] = null_if(dom.xpath('//*[@class="summary-plane__salary"]'))
        item['company_name'] = dom.xpath('//*[@class="company__title"]')[0].text
        item['work_experience'] = dom.xpath('//ul[@class="summary-plane__info"]/li[2]')[0].text
        item['education_background'] = dom.xpath('//ul[@class="summary-plane__info"]/li[3]')[0].text
        item['job_requirements'] = remove_html(
            etree.tostring(dom.xpath('//div[@class="describtion__detail-content"]')[0], encoding="utf-8").decode(
                'utf-8'))
        item['company_info'] = null_if(dom.xpath('//div[@class="company__description"]'))
        item['company_address'] = remove_html(
            etree.tostring(dom.xpath('//span[@class="job-address__content-text"]')[0], encoding="utf-8").decode(
                'utf-8'))
        if len(dom.xpath('//div[@class="highlights__content"]')):
            item['company_welfare'] = remove_html(etree.tostring(dom.xpath('//div[@class="highlights__content"]')[0], encoding="utf-8").decode('utf-8'))
        else:
            item['company_welfare'] = '无'
        item['id'] = get_md5(self.driver.current_url)
        item['keyword'] = response.meta.get("kw", "")
        item['url'] = response.url
        item['crawl_date'] = datetime.now().strftime("%Y-%m-%d")
        yield item
