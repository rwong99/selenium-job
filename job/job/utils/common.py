# -*- coding: utf-8 -*-
__author__ = 'onejane'
import hashlib
import re
import json
from datetime import date, datetime
import urllib
import urllib3
import os
from bs4 import BeautifulSoup


def get_md5(url):
    if isinstance(url, str):  # 若是unicode则转为utf-8
        url = url.encode("utf-8")
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()


def extract_num(text):
    # 从字符串中提取出数字
    match_re = re.match(".*?(\d+.*\d+).*", text)
    if match_re:
        nums = int(re.sub(",", "", match_re.group(1)))
    else:
        nums = 0

    return nums


class DateEncoder(json.JSONEncoder):
    # json.dumps无法序列化datetime，新写函数实现
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime("%Y-%m-%d")
        else:
            return json.JSONEncoder.default(self, obj)




def remove_html(html):
    dr = re.compile(r'<[^>]+>', re.S)
    result = dr.sub('', html)
    return result


def parse_html():
    with open('a', 'rb') as f:
        data = f.read()

    result = re.findall(r'href="(ssr.*?)"', data.decode('utf-8'))
    with open('b', 'a') as file_object:
        for each in result:
            file_object.write(each + "\n")

def parse_json():
    data = "{'primary_info': ['', '统一社会信用代码：91110000802100433B', '企业名称：北京百度网讯科技有限公司', '类型：', '法定代表人：梁志祥', '注册资本：1342128.000000万人民币', '成立日期：2001年06月05日', '营业期限自：2001年06月05日', '营业期限至：2021年06月04日', '登记机关：北京市工商行政管理局海淀分局', '核准日期：2019年08月20日', '登记状态：开业', '住所：北京市海淀区上地十街10号百度大厦2层', '经营范围：技术服务、技术培训、技术推广；设计、开发、销售计算机软件；经济信息咨询；利用www；baidu；com、www；hao123；com(www；hao222；net、www；hao222；com)网站发布广告；设计、制作、代理、发布广告；货物进出口、技术进出口、代理进出口；医疗软件技术开发；委托生产电子产品、玩具、照相器材；销售家用电器、机械设备、五金交电、电子产品、文化用品、照相器材、计算机、软件及辅助设备、化妆品、卫生用品、体育用品、纺织品、服装、鞋帽、日用品、家具、首饰、避孕器具、工艺品、钟表、眼镜、玩具、汽车及摩托车配件、仪器仪表、塑料制品、花、草及观赏植物、建筑材料、通讯设备；预防保健咨询；公园门票、文艺演出、体育赛事、展览会票务代理；翻译服务；通讯设备和电子产品的技术开发；计算机系统服务；因特网信息服务业务（除出版、教育、医疗保健以外的内容）；图书、电子出版物、音像制品批发、零售、网上销售；利用信息网络经营音乐娱乐产品、演出剧（节）目、动漫产品、游戏产品（含网络游戏虚拟货币发行）、表演、网络游戏技法展示或解说（网络文化经营许可证有效期至2020年04月17日）；演出经纪；人才中介服；经营电信业务。（企业依法自主选择经营项目，开展经营活动；演出经纪、人才中介服务、利用信息网络经营音乐娱乐产品、演出剧（节）目、动漫产品、游戏产品（含网络游戏虚拟货币发行）、表演、网络游戏技法展示或解说、经营电信业务以及依法须经批准的项目，经相关部门批准后依批准的内容开展经营活动；不得从事本市产业政策禁止和限制类项目的经营活动。）', '']}"
    result = re.findall(r'\[(.*?)\]', data)
    info_list = result[0].replace('\'','').split(', ')
    info = [info for info in info_list if "类型：" in info]
    a="无" if not len(info) else info[0].replace("类型：","")
    print(a)
    print(info_list[2].split("：")[1])


def company_info(info_list,name):
    info = [info for info in info_list if name in info]
    return "无" if not len(info) else info[0].replace(name, "")

def null_if(list):
    if not len(list):
        list.append("无")
        return list[0]
    return list[0].text if None==list[0].tail else list[0].tail


from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
import selenium.webdriver.support.expected_conditions as EC
import selenium.webdriver.support.ui as ui


# 一直等待某元素可见，默认超时10秒
def is_visible(locator, driver, timeout=10):
    try:
        ui.WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.XPATH, locator)))
        return True
    except TimeoutException:
        return False


# 一直等待某个元素消失，默认超时10秒
def is_not_visible(locator, driver, timeout=10):
    try:
        ui.WebDriverWait(driver, timeout).until_not(EC.visibility_of_element_located((By.XPATH, locator)))
        return True
    except TimeoutException:
        return False


def down_image():
    html = urllib.request.urlopen(
        'https://www.duitang.com/album/?id=69001447').read()
    # parse url data 1 html 2 'html.parser' 3 'utf-8'
    soup = BeautifulSoup(html, 'html.parser', from_encoding='utf-8')
    # img
    images = soup.findAll('img')
    print(images)
    imageName = 0
    for image in images:
        link = image.get('src')
        print('link=', link)
        fileFormat = link[-3:]
        if fileFormat == 'png' or fileFormat == 'jpg':
            fileSavePath = 'C:/Users/codewj/AnacondaProjects/5刷脸识别/images/' + str(imageName) + '.jpg'
            imageName = imageName + 1
            urllib.request.urlretrieve(link, fileSavePath)


if __name__ == "__main__":
    parse_json()
