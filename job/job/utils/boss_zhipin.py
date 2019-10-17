# -*- coding: utf-8 -*-
import json
import os
import re
from urllib.parse import urlencode
import fake_useragent
from scrapy.selector import Selector
import requests
import time
from lxml import etree
from selenium import webdriver
import pandas as pd

# 方法二，从本地文件夹获取
# location = os.path.dirname(os.path.abspath(__file__)) + 'fake_useragent.json'
ka = fake_useragent.UserAgent(path='fake_useragent.json', verify_ssl=False, use_cache_server=False)

# 构造请求头User-Agent
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache - control': 'max - age = 0',
    'referer': 'https://www.zhipin.com/',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': ka.random,
    'X-Requested-With': 'XMLHttpRequest'
}
# 用于存放所有数据
data_my = []
# 这是请求岗位职责的地址相同部分
get_url = 'https://www.zhipin.com/wapi/zpgeek/view/job/card.json?'


def main():
    area_list = {'西湖区', '余杭区', '滨江区', '江干区', '萧山区', '拱墅区', '下城区', '上城区'}

    chromedriver_path = 'chromedriver.exe'
    # 此步骤很重要，设置为开发者模式，防止被各大网站识别出来使用了Selenium
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    driver = webdriver.Chrome(executable_path=chromedriver_path, options=options)
    driver.maximize_window()

    for area in area_list:
        loginurl = 'https://www.zhipin.com/c101210100/b_' + area + '/?query=数据分析杭州'
        driver.get(loginurl)
        time.sleep(3.5)
        # Selenium为我们提供了get_cookies来获取登录cookies
        cookies = driver.get_cookies()
        jsonCookies = json.dumps(cookies)
        # 把cookies保存在本地
        with open('bossCookies.json', 'w') as f:
            f.write(jsonCookies)

        # 获取信息
        get_detail(driver, area)
    # 写入本地CSV文件
    df = pd.DataFrame(data_my)
    df.to_csv('./shuju.csv', index=None, encoding='utf-8-sig', mode='a')
    time.sleep(0.5)
    print('已保存该数据到本地shuju.csv文件夹')
    driver.close()


def get_detail(driver, area):
    source = etree.HTML(driver.page_source)
    node_list = source.xpath("//div[@class='job-primary']")
    # 用来存储所有的item字段

    for node in node_list:
        item = {}
        item['链接'] = node.xpath("./div[@class='info-primary']//a/@href")[0]
        item['职位'] = node.xpath("./div[@class='info-primary']//a/div[@class='job-title']")[0].text
        item['薪资'] = node.xpath("./div[@class='info-primary']//a/span")[0].text
        item['工作地点'] = area
        item['工作经验'] = node.xpath("./div[@class='info-primary']//p/text()[2]")[0]
        item['公司名称'] = node.xpath("./div[@class='info-company']//a")[0].text
        item['所处行业'] = node.xpath("./div[@class='info-company']/div[@class='company-text']/p")[0].text
        item['融资轮'] = node.xpath("./div[@class='info-company']/div[@class='company-text']/p//text()[2]")[0]

        item['jid'] = node.xpath(".//div[@class='info-primary']/h3/a/@data-jid")[0]
        item['lid'] = node.xpath(".//div[@class='info-primary']/h3/a/@data-lid")[0]
        ajson = get_info(item['jid'], item['lid'])
        item['岗位职责'] = get_json(ajson)
        print(item)
        data_my.append(item)

    # 翻页
    if source.xpath('//*[@id="main"]/div/div[3]/div[3]//a[@class="next"]'):
        next_page = driver.find_element_by_xpath('//*[@id="main"]/div/div[3]/div[3]//a[@class="next"]')
        driver.execute_script("arguments[0].click();", next_page)
        time.sleep(3.5)
        # Selenium为我们提供了get_cookies来获取登录cookies
        cookies = driver.get_cookies()
        jsonCookies = json.dumps(cookies)
        # 把cookies保存在本地
        with open('bossCookies.json', 'w') as f:
            f.write(jsonCookies)
        get_detail(driver, area)


def get_info(jid, lid):
    params = {
        'jid': jid,
        'lid': lid
    }

    # 获取cookies
    with open('bossCookies.json', 'r', encoding='utf-8') as f:
        listcookies = json.loads(f.read())

    # 把获取的cookies处理成dict类型
    cookies_dict = dict()
    for cookie in listcookies:
        # 在保存成dict时，只要cookies中的name和value
        cookies_dict[cookie['name']] = cookie['value']

    requests.adapters.DEFAULT_RETRIES = 5
    s = requests.session()
    # 关闭多余进程
    s.keep_alive = False
    # 请求ajax获取岗位职责
    re = requests.get(get_url + urlencode(params), headers=headers, cookies=cookies_dict)
    time.sleep(0.2)
    if re.status_code == 200:
        vjson = re.json()
        return vjson
    else:
        print("获取失败")


def get_json(js):
    # 处理字符串，由于返回的岗位职责是一个包含html的json数据，需要处理一下
    if js:
        json_content = js.get('zpData').get('html')
        content = Selector(text=json_content)
        content_text = content.css(".detail-bottom-text::text").re("[\u4e00-\u9fa5_a-zA-Z0-9]+")
        return content_text
    else:
        print("未获取数据")


if __name__ == '__main__':
    main()

    print("结束---------------------------------")
