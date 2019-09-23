# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import MySQLdb.cursors
import codecs
import json

from scrapy.exporters import JsonItemExporter
from twisted.enterprise import adbapi

from job.utils.common import DateEncoder


class JobPipeline(object):
    def process_item(self, item, spider):
        return item


class JsonWithEncodingPipeline(object):

    # 自定义json文件的导出
    def __init__(self):
        self.file = codecs.open('job.json', 'w', encoding="utf-8")

    def process_item(self, item, spider):
        # 序列化，ensure_ascii利于中文,json没法序列化date格式，需要新写函数
        lines = json.dumps(dict(item), ensure_ascii=False, cls=DateEncoder) + "\n"
        self.file.write(lines)
        return item

    def spider_closed(self, spider):
        self.file.close()


class JsonExporterPipleline(object):
    # 调用scrapy提供的json export导出json文件
    def __init__(self):
        self.file = open('job.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


class MysqlPipeline(object):
    # 采用同步的机制写入mysql
    def __init__(self):
        self.conn = MySQLdb.connect('127.0.0.1', 'root', '', 'scrapy', charset="utf8", use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = """
            insert into job(id, recruitment_position,company_name, education_background,work_experience,salary,job_requirements,company_info,company_address,company_welfare)
            VALUES (%s, %s, %s, %s, %s,%s, %s, %s, %s, %s)
        """
        self.cursor.execute(insert_sql, (
        item["id"], item["recruitment_position"], item["company_name"], item["education_background"],
        item["work_experience"], item["salary"], item["job_requirements"], item["company_info"],
        item["company_address"], item["company_welfare"]))
        self.conn.commit()


class MysqlTwistedPipline(object):
    # 异步连接池插入数据库，不会阻塞
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):  # 初始化时即被调用静态方法
        dbparms = dict(
            host=settings["MYSQL_HOST"],  # setttings中定义
            db=settings["MYSQL_DBNAME"],
            user=settings["MYSQL_USER"],
            passwd=settings["MYSQL_PASSWORD"],
            charset='utf8',
            port=settings["MYSQL_PORT"],
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparms)

        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider)  # 处理异常

    def handle_error(self, failure, item, spider):
        # 处理异步插入的异常
        print(failure)

    def do_insert(self, cursor, item):
        # 执行具体的插入，不具体的如MysqlPipeline.process_item()
        # 根据不同的item 构建不同的sql语句并插入到mysql中
        insert_sql, params = item.get_insert_sql()
        cursor.execute(insert_sql, params)
