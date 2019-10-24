# -*- coding: utf-8 -*-
import json
import os
import platform
import time
import urllib
from datetime import datetime
from urllib import parse
from PIL import Image
import fake_useragent
import scrapy
from fake_useragent import UserAgent
from io import BytesIO
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
import numpy as np
from job.items import *

from job.utils.common import *


from job.utils.common import *

from job.utils.common import remove_html, remove_html_list

from job.items import StandardCompanyItem


class TianYanSpider(scrapy.Spider):
    name = 'tianyan'
    allowed_domains = ['tianyancha.com']
    start_urls = ['https://www.tianyancha.com']
    nodes = []
    base_url = "https://www.tianyancha.com/search?key="
    driver = None
    chrome_options = webdriver.ChromeOptions()
    # proxy_url = get_random_proxy()
    # print(proxy_url + "代理服务器正在爬取")
    # chrome_options.add_argument('--proxy-server=https://' + proxy_url.strip())
    prefs = {
        'profile.default_content_setting_values': {
            # 'images': 2,  # 不加载图片
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

    def __init__(self, word,*args, **kwargs):
        super(eval(self.__class__.__name__), self).__init__(*args, **kwargs)
        self.word = word

    def start_requests(self):
        source = self.autologin(text_login='请输入11位手机号码', text_password='请输入登录密码',username="15806204096",password="Wangjian123456")
        yield Request(url="https://www.tianyancha.com", callback=self.parse,
                      meta={'params': (self.word, source)}, dont_filter=True)

    def parse(self, response):
        word, source = response.meta.get("params")
        links = source.xpath("//div[@class='search-result-single   ']/div[@class='content']/div[@class='header']/a/@href")
        while len(source.xpath('//a[@class="num -next"]')) == 1:
            next_page = self.driver.find_element_by_xpath('//a[@class="num -next"]')
            next_page.click()
            print(self.driver.current_url)
            time.sleep(2)
            source = etree.HTML(self.driver.page_source)
            new_links = source.xpath("//div[@class='search-result-single   ']/div[@class='content']/div[@class='header']/a/@href")
            links.extend(new_links)
        yield Request(url="https://www.tianyancha.com", callback=self.parse_detail,
                      meta={'params': (self.word, links)}, dont_filter=True)

    def parse_detail(self,response):
        word, links = response.meta.get("params")
        for link in links:
            print(link)
            self.driver.execute_script("window.open('%s')" % link)
            time.sleep(5)
            self.driver.switch_to.window(self.driver.window_handles[1])
            try:
                WebDriverWait(self.driver, timeout=10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@class='block-data-group ']"))
                )
            except:
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
                continue
            html = etree.HTML(self.driver.page_source)
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            item = StandardCompanyItem()
            try:
                item["legal_representative"]= html.xpath("//div[@class='humancompany']/div[@class='name']/a/text()")[0]
            except:
                item["legal_representative"] = remove_html(etree.tostring(html.xpath("//div[@class='legal-representative']")[0],encoding='utf-8').decode('utf-8'))
            table=html.xpath("//table[@class='table -striped-col -border-top-none -breakall']")[0]
            item["registered_capital"] = remove_html(etree.tostring(table.xpath("./tbody/tr[1]/td[2]")[0],encoding='utf-8').decode('utf-8'))
            item["reality_capital"] = table.xpath("./tbody/tr[1]/td[4]/text()")[0]
            item["establishment_date"] = remove_html(etree.tostring(table.xpath("./tbody/tr[2]/td[2]")[0],encoding='utf-8').decode('utf-8'))
            item["business_status"] = table.xpath("./tbody/tr[2]/td[4]/text()")[0]
            item["social_credit_code"] = table.xpath("./tbody/tr[3]/td[2]/text()")[0]
            item["business_registration_num"] = table.xpath("./tbody/tr[3]/td[4]/text()")[0]
            item["taxpayer_num"] = table.xpath("./tbody/tr[4]/td[2]/text()")[0]
            item["organization_code"] = table.xpath("./tbody/tr[4]/td[4]/text()")[0]
            item["company_type"] = table.xpath("./tbody/tr[5]/td[2]/text()")[0]
            item["industry"] = table.xpath("./tbody/tr[5]/td[4]/text()")[0]
            item["approval_date"] = table.xpath("./tbody/tr[6]/td[2]/text()")[0]
            item["registration_authority"] = table.xpath("./tbody/tr[6]/td[4]/text()")[0]
            item["operating_period"] = remove_html(etree.tostring(table.xpath("./tbody/tr[7]/td[2]")[0],encoding='utf-8').decode('utf-8'))
            item["taxpayer_qualification"] = table.xpath("./tbody/tr[7]/td[4]/text()")[0].replace("-","")
            item["staff_size"] = table.xpath("./tbody/tr[8]/td[2]/text()")[0].replace("-","")
            item["participants_num"] = table.xpath("./tbody/tr[8]/td[4]/text()")[0].replace("-","")
            item["used_name"] = remove_html(etree.tostring(table.xpath("./tbody/tr[9]/td[2]")[0],encoding='utf-8').decode('utf-8'))
            item["english_name"] = table.xpath("./tbody/tr[9]/td[4]/text()")[0]
            item["registered_address"] = table.xpath("./tbody/tr[10]/td[2]/text()")[0]
            item["business_scope"] = remove_html(etree.tostring(table.xpath("./tbody/tr[11]/td[2]")[0],encoding='utf-8').decode('utf-8'))
            item["company_name"] = html.xpath("//div[@class='content']/div[@class='header']/h1/text()")[0]
            item["telephone"] = html.xpath("//div[@class='in-block sup-ie-company-header-child-1']/span[2]/text()")[0]
            item["url"] = link
            item["address"] = html.xpath("//div[@class='in-block sup-ie-company-header-child-2']/div/div/text()")[0]
            item["introduction"] = remove_html(etree.tostring(html.xpath("//div[@class='summary']")[0],encoding='utf-8').decode('utf-8'))
            item["job_company_name"] = word
            yield item



    '''
        @description: 滑块位移的计算
        @param {type} 
        @return: 
    '''
    def get_tracks(self,distance, seconds):
        tracks = [0]
        offsets = [0]
        for t in np.arange(0.0, seconds, 0.1):
            offset = round(self.ease_out_expo(t / seconds) * distance)
            tracks.append(offset - offsets[-1])
            offsets.append(offset)
        return offsets, tracks


    '''
    @description: 登录方法
    @param {type} 
    @return: 
    '''
    def autologin(self, text_login, text_password,username,password):
        self.driver.get('http://www.tianyancha.com')
        time.sleep(2)
        self.driver.maximize_window()
        # driver.set_window_size(500, 200)
        self.driver.implicitly_wait(10)
        # 关底部
        try:
            self.driver.find_element_by_xpath('//*[@id="tyc_banner_close"]').click()
        except:
            pass


        with open("tianyan.html", "a+") as f:
            f.writelines(self.driver.page_source)
            f.writelines("\n")
        # 登陆按钮
        self.driver.find_element_by_xpath('//*[@id="web-content"]/div/div[1]/div[1]/div/div/div[2]/div/div[4]/a').click()
        time.sleep(2)

        # 这里点击密码登录时用id去xpath定位是不行的，因为这里的id是动态变化的，所以这里换成了class定位
        self.driver.find_element_by_xpath(
            './/div[@class="modal-dialog -login-box animated"]/div/div[2]/div/div/div[3]/div[1]/div[2]').click()
        time.sleep(2)
        # 天眼查官方会频繁变化登录框的占位符,所以设置两个新参数来定义占位符
        # 输入用户名和密码
        self.driver.find_elements_by_xpath("//input[@placeholder='{}']".format(text_login))[-2].send_keys(username)
        self.driver.find_elements_by_xpath("//input[@placeholder='{}']".format(text_password))[-1].send_keys(password)
        clixp = './/div[@class="modal-dialog -login-box animated"]/div/div[2]/div/div/div[3]/div[2]/div[5]'
        self.driver.find_element_by_xpath(clixp).click()
        time.sleep(2)

        # 获取图
        img = self.driver.find_element_by_xpath('/html/body/div[10]/div[2]/div[2]/div[1]/div[2]/div[1]')
        time.sleep(0.5)
        location = img.location
        size = img.size
        top, bottom, left, right = location['y'], location['y'] + size['height'], location['x'], location['x'] + size[
            'width']
        # 截取第一张图片(无缺口的)
        screenshot = self.driver.get_screenshot_as_png()
        time.sleep(2)
        screenshot = Image.open(BytesIO(screenshot))
        captcha1 = screenshot.crop((left, top, right, bottom))
        print('--->', captcha1.size)
        captcha1.save('captcha1.png')

        # 获取第二张图，先点击滑块
        self.driver.find_element_by_xpath('/html/body/div[10]/div[2]/div[2]/div[2]/div[2]').click()
        time.sleep(2)
        img1 = self.driver.find_element_by_xpath('/html/body/div[10]/div[2]/div[2]/div[1]/div[2]/div[1]')
        time.sleep(0.5)
        location1 = img1.location
        size1 = img1.size
        top1, bottom1, left1, right1 = location1['y'], location1['y'] + size1['height'], location1['x'], location1[
            'x'] + size1['width']
        screenshot = self.driver.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))
        captcha2 = screenshot.crop((left1, top1, right1, bottom1))
        captcha2.save('captcha2.png')

        # 获取偏移量
        left = 50  # 这个是去掉开始的一部分
        for i in range(left, captcha1.size[0]):  # 长
            for j in range(captcha1.size[1]):  # 宽
                # 判断两个像素点是否相同
                pixel1 = captcha1.load()[i, j]
                pixel2 = captcha2.load()[i, j]
                threshold = 60
                if abs(pixel1[0] - pixel2[0]) < threshold and abs(pixel1[1] - pixel2[1]) < threshold and abs(
                        pixel1[2] - pixel2[2]) < threshold:
                    pass
                else:
                    left = i
        print('缺口位置', left)

        time.sleep(3)

        left -= 50
        # 开始移动
        offsets, tracks = self.get_tracks(left, 12)
        # 拖动滑块
        starttime = time.time()
        slider = self.driver.find_element_by_xpath('/html/body/div[10]/div[2]/div[2]/div[2]/div[2]')

        ActionChains(self.driver).click_and_hold(slider).perform()

        for x in tracks:
            ActionChains(self.driver).move_by_offset(xoffset=x, yoffset=0).perform()
        ActionChains(self.driver).release().perform()

        endtime = time.time()
        print("时间：")
        print(endtime - starttime)
        time.sleep(1)
        try:
            if self.driver.find_element_by_xpath('/html/body/div[10]/div[2]/div[2]/div[2]/div[2]'):
                print('能找到滑块，重新试')
                self.driver.delete_all_cookies()
                self.driver.refresh()
                self.autologin(text_login, text_password,username="15599029013",password="zhao1234")  # 重新登陆
            else:
                print('login success')
        except:
            print('login success')
        time.sleep(2)
        self.driver.get(self.base_url + self.word)
        source = etree.HTML(self.driver.page_source)
        print(source.xpath('//*[@id="web-content"]/div/div[1]/div[3]/div[2]/div[1]/div/div[3]/div[1]/a/@href'))
        return source



    def ease_out_quad(self,x):
        return 1 - (1 - x) * (1 - x)

    def ease_out_quart(self,x):
        return 1 - pow(1 - x, 4)

    def ease_out_expo(self,x):
        if x == 1:
            return 1
        else:
            return 1 - pow(2, -10 * x)

