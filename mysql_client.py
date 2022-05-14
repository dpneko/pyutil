import pymysql
from dbutils.pooled_db import PooledDB
 
class MysqlPool:
    config = {
        'creator': pymysql,
        'host': "127.0.0.1",
        'port': 3306,
        'user': "tron",
        'password': "123456",
        'db': "vecrv_sun_airdrop_claimed",
        'charset': 'utf8',
        'maxconnections': 70,
        'cursorclass': pymysql.cursors.DictCursor
    }
    pool = PooledDB(**config)
 
    def __enter__(self):
        self.conn = MysqlPool.pool.connection()
        self.cursor = self.conn.cursor()
        return self
 
    def __exit__(self, type, value, trace):
        if type == None or type == 0:
            self.conn.commit()
        else:
            print(f"mysql exec failed: \"{self.cursor._last_executed}\"\n"
                f"{type.__name__}{value}\n"
                f"{trace}")
            self.conn.rollback()
        self.cursor.close()
        self.conn.close()
 
def db_conn(func):
    def wrapper(*args, **kw):
        with MysqlPool() as db:
            result = func(db, *args, **kw)
        return result
    return wrapper


class Mysql:
 
    @staticmethod
    @db_conn
    def getAll(db, sql, param=None):
        """
        @summary: 执行查询，并取出所有结果集
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list(字典对象)/boolean 查询到的结果集
        """
        if param is None:
            count = db.cursor.execute(sql)
        else:
            count = db.cursor.execute(sql, param)
        if count>0:
            result = db.cursor.fetchall()
        else:
            result = False
        return result

    @staticmethod
    @db_conn
    def getOne(db, sql, param=None):
        """
        @summary: 执行查询，并取出第一条
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list/boolean 查询到的结果集
        """
        if param is None:
            count = db.cursor.execute(sql)
        else:
            count = db.cursor.execute(sql, param)
        if count>0:
            result = db.cursor.fetchone()
        else:
            result = False
        return result

    @staticmethod
    @db_conn
    def getMany(db, sql, num, param=None):
        """
        @summary: 执行查询，并取出num条结果
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param num:取得的结果条数
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list/boolean 查询到的结果集
        """
        if param is None:
            count = db.cursor.execute(sql)
        else:
            count = db.cursor.execute(sql, param)
        if count>0:
            result = db.cursor.fetchmany(num)
        else:
            result = False
        return result

    @staticmethod
    @db_conn
    def insertOne(db, sql, value):
        """
        @summary: 向数据表插入一条记录
        @param sql:要插入的ＳＱＬ格式
        @param value:要插入的记录数据tuple/list
        @return: insertId 受影响的行数
        """
        db.cursor.execute(sql, value)
        return Mysql.__getInsertId(db)

    @staticmethod
    @db_conn
    def insertMany(db, sql, values):
        """
        @summary: 向数据表插入多条记录
        @param sql:要插入的ＳＱＬ格式
        @param values:要插入的记录数据tuple(tuple)/list[list]
        @return: count 受影响的行数
        """
        count = db.cursor.executemany(sql,values)
        return count

    @staticmethod
    def __getInsertId(db):
        """
        获取当前连接最后一次插入操作生成的id,如果没有则为０
        """
        db.cursor.execute("SELECT @@IDENTITY AS id")
        result = db.cursor.fetchall()
        return result[0]['id']

    @staticmethod
    def __query(db, sql, param=None):
        if param is None:
            count = db.cursor.execute(sql)
        else:
            count = db.cursor.execute(sql, param)
        return count

    @staticmethod
    @db_conn
    def update(db, sql, param=None):
        """
        @summary: 更新数据表记录
        @param sql: ＳＱＬ格式及条件，使用(%s,%s)
        @param param: 要更新的  值 tuple/list
        @return: count 受影响的行数
        """
        return Mysql.__query(db, sql, param)

    @staticmethod
    @db_conn
    def delete(db, sql, param=None):
        """
        @summary: 删除数据表记录
        @param sql: ＳＱＬ格式及条件，使用(%s,%s)
        @param param: 要删除的条件 值 tuple/list
        @return: count 受影响的行数
        """
        return Mysql.__query(db, sql, param)


