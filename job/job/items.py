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
            ON DUPLICATE KEY UPDATE company_address=VALUES(company_address),crawl_date=VALUES(crawl_date),update_date=VALUES(update_date),
            company_name=VALUES(company_name),education_background=VALUES(education_background),work_experience=VALUES(work_experience),job_requirements=VALUES(job_requirements)
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


class StandardCompanyItem(scrapy.Item):
    legal_representative = scrapy.Field()
    registered_capital = scrapy.Field()
    reality_capital = scrapy.Field()
    establishment_date = scrapy.Field()
    business_status = scrapy.Field()
    social_credit_code = scrapy.Field()
    business_registration_num = scrapy.Field()
    taxpayer_num = scrapy.Field()
    organization_code = scrapy.Field()
    company_type = scrapy.Field()
    industry = scrapy.Field()
    approval_date = scrapy.Field()
    registration_authority = scrapy.Field()
    operating_period = scrapy.Field()
    taxpayer_qualification = scrapy.Field()
    staff_size = scrapy.Field()
    participants_num = scrapy.Field()
    used_name = scrapy.Field()
    english_name = scrapy.Field()
    registered_address = scrapy.Field()
    business_scope = scrapy.Field()
    company_name = scrapy.Field()
    telephone = scrapy.Field()
    url = scrapy.Field()
    address = scrapy.Field()
    introduction = scrapy.Field()
    job_company_name = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            insert into standard_business(legal_representative,registered_capital,reality_capital,establishment_date,business_status,social_credit_code,business_registration_num,taxpayer_num,organization_code,company_type,industry,approval_date,registration_authority,operating_period,taxpayer_qualification,staff_size,participants_num,used_name,english_name,registered_address,business_scope,company_name,telephone,url,address,introduction,job_company_name)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) 
            ON DUPLICATE KEY UPDATE 
            legal_representative=VALUES(legal_representative),
            business_status=VALUES(business_status),
            staff_size=VALUES(staff_size),
            participants_num=VALUES(participants_num),
            business_scope=VALUES(business_scope),
            registered_capital=VALUES(registered_capital),
            reality_capital=VALUES(reality_capital)
        """
        params = (self["legal_representative"],self["registered_capital"],self["reality_capital"],self["establishment_date"],self["business_status"],self["social_credit_code"],self["business_registration_num"],self["taxpayer_num"],self["organization_code"],self["company_type"],self["industry"],self["approval_date"],self["registration_authority"],self["operating_period"],self["taxpayer_qualification"],self["staff_size"],self["participants_num"],self["used_name"],self["english_name"],self["registered_address"],self["business_scope"],self["company_name"],self["telephone"],self["url"],self["address"],self["introduction"],self["job_company_name"])

        return insert_sql, params

