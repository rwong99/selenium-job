# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose


def return_value(value):
    return value


class JobItemLoader(ItemLoader):
    # 自定义itemloader
    default_output_processor = TakeFirst()


class JobItem(scrapy.Item):
    source = scrapy.Field()
    update_date = scrapy.Field()
    id = scrapy.Field()
    recruitment_position = scrapy.Field()
    company_name = scrapy.Field()
    education_background = scrapy.Field()
    work_experience = scrapy.Field()
    salary = scrapy.Field()
    job_requirements = scrapy.Field()
    company_info = scrapy.Field(
        input_processor=MapCompose(return_value),  # 传递进来可以预处理
    )
    company_address = scrapy.Field()
    company_welfare = scrapy.Field()
    crawl_date = scrapy.Field()
    keyword = scrapy.Field()
    url = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            insert into job(update_date,source,id, recruitment_position,company_name, education_background,work_experience,salary,job_requirements,company_info,company_address,company_welfare,crawl_date,url,keyword)
            VALUES (%s,%s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s,%s,%s) 
        """
        params = (self["update_date"],self["source"],self["id"], self["recruitment_position"], self["company_name"], self["education_background"],
                  self["work_experience"], self["salary"], self["job_requirements"], self["company_info"],
                  self["company_address"], self["company_welfare"], self["crawl_date"], self["url"], self["keyword"])

        return insert_sql, params


class CompanyItem(scrapy.Item):
    code = scrapy.Field()
    name = scrapy.Field()
    type = scrapy.Field()
    start = scrapy.Field()
    end = scrapy.Field()
    capital = scrapy.Field()
    owner = scrapy.Field()
    establish = scrapy.Field()
    registration = scrapy.Field()
    check = scrapy.Field()
    status = scrapy.Field()
    address = scrapy.Field()
    scope = scrapy.Field()
    partner = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            insert into company(code, name,type, start_date,end_date,capital,owner,establish,registration,check_date,status,address,scope,partner)
            VALUES (%s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s,%s,%s,%s) 
            ON DUPLICATE KEY UPDATE address=VALUES(address)
        """
        params = (self["code"], self["name"], self["type"], self["start"], self["end"], self["capital"], self["owner"],
                  self["establish"], self["registration"], self["check"], self["status"], self["address"],
                  self["scope"],self['partner'])

        return insert_sql, params
