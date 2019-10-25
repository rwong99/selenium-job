# -*- coding: utf-8 -*-
import json
import os
import platform
import time
import urllib
from datetime import datetime
from urllib import parse

import fake_useragent
import scrapy
from fake_useragent import UserAgent
from lxml import etree
from scrapy import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC, expected_conditions
from selenium.webdriver.common.by import By

from job.items import *

from job.utils.common import *

from job.items import JobItem

from job.utils.common import *

from job.utils.common import remove_html, remove_html_list



class BossSpider(scrapy.Spider):
    name = 'boss'
    allowed_domains = ['zhipin.com']
    start_urls = ['https://www.zhipin.com/']
    nodes = []

    def closed(self, reason):
        self.driver.close()
        self.driver.quit()
        print('spider关闭原因:', reason)

    def parse(self, response):

        driver = None
        chrome_options = webdriver.ChromeOptions()
        # proxy_url = get_random_proxy()
        # print(proxy_url + "代理服务器正在爬取")
        # chrome_options.add_argument('--proxy-server=https://' + proxy_url.strip())
        prefs = {
            'profile.default_content_setting_values': {
                'images': 1,  # 加载图片
                "User-Agent": UserAgent().random,  # 更换UA
            }
        }
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        if platform.system() == "Windows":
            driver = webdriver.Chrome('chromedriver.exe', chrome_options=chrome_options)
        elif platform.system() == "Linux":
            chrome_options.add_argument("--headless")
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--no-sandbox')
            driver = webdriver.Chrome(
                executable_path="/usr/bin/chromedriver",
                chrome_options=chrome_options)
        driver.set_window_size(100, 100)

        data = ["游戏", "期货", "贷款"]
        for kw in data:
            url = "https://www.zhipin.com/c101190400/?query={}".format(kw)
            driver.get(url)
            time.sleep(2)
            # 获取信息
            last_url = driver.current_url
            source = etree.HTML(driver.page_source)
            links = source.xpath("//div[@class='job-primary']/div[@class='info-primary']//a/@href")
            global nodes
            nodes = list(map(lambda x: "https://www.zhipin.com{}".format(x), links))

            while len(source.xpath('//div[@class="page"]/a[@class="next" and @ka="page-next"]')) == 1:
                next_page = driver.find_element_by_xpath(
                    '//div[@class="page"]/a[@class="next" and @ka="page-next"]')
                WebDriverWait(driver, 10).until(expected_conditions.element_to_be_clickable(
                    (By.XPATH, '//div[@class="page"]/a[@class="next" and @ka="page-next"]')))
                current_url = driver.current_url
                while last_url == current_url:
                    self.loop_try(next_page)
                    last_url = driver.current_url
                print(driver.current_url)
                source = etree.HTML(driver.page_source)
                new_links = source.xpath("//div[@class='job-primary']/div[@class='info-primary']//a/@href")
                new_nodes = list(map(lambda x: "https://www.zhipin.com{}".format(x), new_links))
                nodes.extend(new_nodes)
            yield Request(url="https://www.zhipin.com", callback=self.parse_detail,
                          meta={'params': (nodes, driver, kw)},dont_filter=True)

    def parse_detail(self,response):
        nodes, driver, kw = response.meta.get("params")
        for node in nodes:
            print(node)
            driver.execute_script("window.open('%s')" % node)
            time.sleep(2)
            driver.switch_to.window(driver.window_handles[1])
            WebDriverWait(driver, timeout=10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='detail-content']"))
            )
            html = etree.HTML(driver.page_source)
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

            item = JobItem()
            item['recruitment_position'] = html.xpath(
                "//div[@class='job-primary detail-box']/div[@class='info-primary']/div[@class='name']/h1/text()")[0]
            item['salary'] = html.xpath(
                "//div[@class='job-primary detail-box']/div[@class='info-primary']/div[@class='name']/span/text()")[
                0]
            item['keyword'] = kw
            item['url'] = node
            item['source'] = "BOSS直聘"
            item['update_date'] = html.xpath('//div[@class="sider-company"]/p[last()]/text()')[0]
            item['company_name'] = html.xpath('//a[@ka="job-detail-company_custompage"]')[0].attrib.get('title').strip().replace("\n招聘","")
            # item['company_name'] = html.xpath('//div[@class="level-list"]/preceding-sibling::div[1]/text()')[0]
            item['work_experience'] = html.xpath('//*[@class="job-primary detail-box"]/div[2]/p/text()')[1]
            item['education_background'] = html.xpath('//*[@class="job-primary detail-box"]/div[2]/p/text()')[2]
            item['job_requirements'] = "".join(
                html.xpath('//div[@class="detail-content"]/div[@class="job-sec"]/div[@class="text"]/text()'))
            item['company_info'] = "".join(
                html.xpath('//div[@class="job-sec company-info"]//div[@class="text"]/text()'))
            item['company_address'] = html.xpath('//*[@class="location-address"]/text()')[0]
            item['company_welfare'] = ",".join(html.xpath(
                '//div[@class="job-banner"]/div[@class="job-primary detail-box"]/div[@class="info-primary"]/div[@class="tag-container"]/div[@class="job-tags"]/text()'))
            item['id'] = get_md5(node)
            item['crawl_date'] = datetime.now().strftime("%Y-%m-%d")
            yield item

    def loop_try(self,next_page):
        try:
            next_page.click()
        except:
            self.loop_try(next_page)
