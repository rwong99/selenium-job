# encoding=utf-8

import MySQLdb

# 主类
from job.settings import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DBNAME, MYSQL_CHARSET


class MysqlConnection(object):
    def __init__(self, host, port, user, passwd, db, charset='utf8'):
        self.__host = host
        self.__port = port
        self.__user = user
        self.__passwd = passwd
        self.__db = db
        self.__charset = charset
        self.__conn = None
        self.__cur = None
        self.__connect()

    # 连接数据库
    def __connect(self):
        try:
            self.__conn = MySQLdb.connect(host=self.__host, port=self.__port, \
                                          user=self.__user, passwd=self.__passwd, \
                                          db=self.__db, charset=self.__charset)

            self.__cur = self.__conn.cursor()
        except:
            print("数据库连接异常")

    def close(self):
        # 在关闭连接之前将内存中的文件写入磁盘
        self.commit()
        if self.__cur:
            self.__cur.close()
            self.__cur = None

        if self.__conn:
            self.__conn.close()
            self.__conn = None

    # 设置提交
    def commit(self):
        if self.__conn:
            self.__conn.commit()

    def execute(self, sql, args=()):
        _cnt = 0
        if self.__cur:
            self.__cur.execute(sql, args)
        return _cnt

    def fetch(self, sql, args=()):
        _cnt = 0
        rt_list = []
        # _cnt = self.execute(sql, args)
        if self.__cur:
            _cnt = self.__cur.execute(sql, args)
            rt_list = self.__cur.fetchall()
        return _cnt, rt_list

    @classmethod
    def execute_sql(cls, sql, args=(), fetch=True):
        count = 0
        rt_list = []
        conn = MysqlConnection(host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER, passwd=MYSQL_PASSWORD,
                               db=MYSQL_DBNAME, 
                               charset=MYSQL_CHARSET)
        print(sql)
        if fetch:
            count, rt_list = conn.fetch(sql, args)
        else:
            count = conn.execute(sql, args)
        conn.close()
        print(rt_list)
        return count, rt_list


def execute_fetch_sql(sql, args=(), fetch=True):
    return execute_sql(sql, args, fetch)


def execute_commit_sql(sql, args=(), fetch=False):
    return execute_sql(sql, args, fetch)


# 区别在于是查询还是修改，增加，删除操作，用fetch来标识
def execute_sql(sql, args=(), fetch=True):
    cur = None
    conn = None
    count = 0
    rt = ()
    try:
        conn = MySQLdb.connect(host=MYSQL_HOST, port=MYSQL_PORT, \
                               user=MYSQL_USER, passwd=MYSQL_PASSWORD, db=MYSQL_DBNAME, \
                               charset=MYSQL_CHARSET)

        cur = conn.cursor()
        print('dbutils sql:%s, args = %s' % (sql, args))
        count = cur.execute(sql, args)
        # 如果是查询
        if fetch:
            rt = cur.fetchall()
            # if args:
            #     rt = cur.fetchone()
            # else:
            #     rt = cur.fetchall()
        else:
            conn.commit()

    except:
        print("执行sql失败")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
    print('dbutils:%s,%s' % (count, rt))
    return count, rt


# 批量插入数据库
def batch_execute_sql(sql, rt_list=[]):
    cur = None
    conn = None
    count = 0
    rt = ()

    try:
        conn = MySQLdb.connect(host=MYSQL_HOST, port=MYSQL_PORT, \
                               user=MYSQL_USER, passwd=MYSQL_PASSWORD, db=MYSQL_DBNAME, \
                               charset=MYSQL_CHARSET)

        cur = conn.cursor()
        print(sql)
        # 循环执行插入语句，一次性全部提交
        for line in rt_list:
            count += cur.execute(sql, line)
        conn.commit()

    except:
        print("批量插入失败")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

    return count


# 测试代码
if __name__ == '__main__':
    # conn = MysqlConnection(host = MYSQL_HOST, port = MYSQL_PORT,\
    #         user = MYSQL_USER, passwd = MYSQL_PASSWORD, db = MYSQL_DB,\
    #         charset = MYSQL_CHARSET)

    # # conn.execute('insert into user(username) values(%s)', ('jack123',))
    # cnt, rt_list = conn.fetch('select * from user')
    # print cnt,rt_list
    # conn.close()
    count, rt_list = MysqlConnection.execute_sql('insert into company(code) values(%s)', ('1',))
    print(rt_list)
