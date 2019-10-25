# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import MySQLdb.cursors
import codecs
import json

import pymysql
from scrapy.exporters import JsonItemExporter
from twisted.enterprise import adbapi
from scrapy.utils.project import get_project_settings
from job.utils.common import DateEncoder
import logging

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


# class MysqlPipeline(object):
#     # 采用同步的机制写入mysql
#     def __init__(self):
#         self.conn = MySQLdb.connect('127.0.0.1', 'root', '', 'scrapy', charset="utf8", use_unicode=True)
#         self.cursor = self.conn.cursor()
#
#     def process_item(self, item, spider):
#         insert_sql = """
#             insert into job(id, recruitment_position,company_name, education_background,work_experience,salary,job_requirements,company_info,company_address,company_welfare)
#             VALUES (%s, %s, %s, %s, %s,%s, %s, %s, %s, %s)
#         """
#         self.cursor.execute(insert_sql, (
#         item["id"], item["recruitment_position"], item["company_name"], item["education_background"],
#         item["work_experience"], item["salary"], item["job_requirements"], item["company_info"],
#         item["company_address"], item["company_welfare"]))
#         self.conn.commit()

# class MysqlTwistedPipline(object):
#     def __init__(self):
#         settings = get_project_settings()
#         # 建立数据库连接
#         self.connection = pymysql.connect(host=settings['MYSQL_HOST'], port=settings['MYSQL_PORT'], user=settings['MYSQL_USER'], password=settings['MYSQL_PASSWORD'], db=settings['MYSQL_DBNAME'],
#                                           charset=settings['MYSQL_CHARSET'])
#         # 创建操作游标
#         self.cursor = self.connection.cursor()
#
#     def process_item(self, item, spider):
#         select_sql = "select * from travel_comment where id = %s"
#         self.cursor.execute(select_sql,item['id'])
#         result = self.cursor.fetchone()
#         if result == None:
#             # 定义sql语句
#             # print(item)
#             logging.debug("====================================")
#             logging.debug(item)
#             logging.debug("====================================")
#             sql = "INSERT INTO travel_comment (`id`, `company`, `username`, `content`,`page_num`, `score`, `create_date`, `crawl_time`) VALUES ('" + item['id'] + "', '" + item['company'] + "', '" + item['username'] + "', '" + item['content'] + "', '"+ str(item['page_num']) + "', '" + str(item['score']) + "', '" + item['create_date'] + "', '" + item['crawl_time'].strftime(SQL_DATETIME_FORMAT) + "');"
#             # 执行sql语句
#             self.cursor.execute(sql)
#             # 保存修改
#             self.connection.commit()
#
#         return item
#
#     def __del__(self):
#         # 关闭操作游标
#         self.cursor.close()
#         # 关闭数据库连接
#         self.connection.close()

class MysqlTwistedPipline(object):
    # 异步连接池插入数据库，不会阻塞
    def __init__(self):
        settings = get_project_settings()
        dbparams = {
            'host': settings["MYSQL_HOST"],
            'port': settings["MYSQL_PORT"],
            'user': settings["MYSQL_USER"],
            'password': settings["MYSQL_PASSWORD"],
            'database': settings["MYSQL_DBNAME"],
            'charset': 'utf8',
            'cursorclass': MySQLdb.cursors.DictCursor
        }
        self.dbpool = adbapi.ConnectionPool('pymysql', **dbparams)

    # @classmethod
    # def from_settings(cls, settings):  # 初始化时即被调用静态方法
    #     dbparms = dict(
    #         host=settings["MYSQL_HOST"],  # setttings中定义
    #         db=settings["MYSQL_DBNAME"],
    #         user=settings["MYSQL_USER"],
    #         passwd=settings["MYSQL_PASSWORD"],
    #         charset='utf8',
    #         port=settings["MYSQL_PORT"],
    #         cursorclass=MySQLdb.cursors.DictCursor,
    #         use_unicode=True,
    #     )
    #     dbpool = adbapi.ConnectionPool("MySQLdb", **dbparms)
    #     dbpool.reconnect = True
    #     return cls(dbpool)

    def process_item(self, item, spider):
        # 使用twisted将mysql插入变成异步执行
        # query = self.dbpool.runInteraction(self.do_insert, item)
        # query.addErrback(self.handle_error, item, spider)  # 处理异常
        # 对sql语句进行处理
        defer = self.dbpool.runInteraction(self.insert_item, item)  # 执行函数insert_item 去插入数据
        defer.addErrback(self.handle_error, item, spider)  # 遇到错误信息调用 handle_error方法

    def handle_error(self, error, item, spider):
        # 处理异步插入的异常
        print('=' * 20 + 'error' + '=' * 20)
        print(error)
        print('=' * 20 + 'error' + '=' * 20)

    def insert_item(self, cursor, item):
        insert_sql, params = item.get_insert_sql()
        cursor.execute(insert_sql, params)
    # def do_insert(self, cursor, item):
    #     # 执行具体的插入，不具体的如MysqlPipeline.process_item()
    #     # 根据不同的item 构建不同的sql语句并插入到mysql中
    #     insert_sql, params = item.get_insert_sql()
    #     cursor.execute(insert_sql, params)

    # def __del__(self):
    #     # 关闭操作游标
    #     self.cursor.close()
    #     # 关闭数据库连接
    #     self.connection.close()
class MysqlPipeline:
    # 同步加载数据库
    def __init__(self, db_conn):
        self.db_conn = db_conn
        self.db_cur = db_conn.cursor()

    @classmethod
    def from_settings(cls, settings):
        db = settings["MYSQL_DBNAME"]
        host = settings["MYSQL_HOST"]
        port = settings["MYSQL_PORT"]
        user = settings["MYSQL_USER"]
        passwd = settings["MYSQL_PASSWORD"]
        db_conn = pymysql.connect(host=host, port=port, db=db, user=user, passwd=passwd, charset='utf8')
        return cls(db_conn)

    # 关闭数据库
    def close_spider(self, spider):
        self.db_conn.commit()
        self.db_cur.close()
        self.db_conn.close()

    # 对数据进行处理
    def process_item(self, item, spider):
        self.insert_db(item)
        return item

    # 插入数据
    def insert_db(self, item):
        insert_sql, params = item.get_insert_sql()
        try:
            self.db_conn.ping(reconnect=True)
            self.db_cur.execute(insert_sql, params)
            self.db_conn.commit()
            print("Insert finished")
        except Exception as e:
            print(e)
            self.db_conn.commit()
            self.db_conn.close()
