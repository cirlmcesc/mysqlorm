""" mysqldb connect package mysqlorm """
""" mysql connect operation library  """

import time
import pymysql as MySQLdb


class MySQLConnect(object):
    """
    MySQL connect, set db connect, example:
    db_config = {
        "host": "localhost",
        "user": "user",
        "passwd": "passwd",
        "db": "schema",
    }
    MySQLConnect.connect(db_config)
    """

    mysql_connect_count = 0
    mysql_connect_config = {}
    sql_statement_log = []
    last_executed = ""
    db_connect = {}
    db = {}

    @classmethod
    def getDB(cls):
        return cls.db

    @classmethod
    def getDBConnect(cls):
        return cls.db_connect

    @classmethod
    def connect(cls, db_config={}):
        """ connect """
        if len(db_config):
            db_config['cursorclass'] = MySQLdb.cursors.DictCursor
            cls.mysql_connect_config = db_config

        cls.db_connect = MySQLdb.connect(**cls.mysql_connect_config)
        cls.db = cls.db_connect.cursor()
        cls.mysql_connect_count += 1

    @classmethod
    def __dbexecute(cls, sql, parameter, many):
        """ db execute """
        if many:
            cls.db.executemany(sql, parameter)
        else:
            cls.db.execute(sql, parameter)

    @classmethod
    def __fetch(cls, sql, few):
        """ fetch all """
        if sql.upper().replace(" ", "").startswith("SELECT"):
            return cls.db.fetchall() if few else cls.db.fetchone()

        return cls.db_connect.commit()

    @classmethod
    def __check_connect(cls):
        """ check connect """
        try:
            cls.db_connect.ping()
        except:
            cls.connect()
            time.sleep(10)
            cls.__check_connect()

    @classmethod
    def execute(cls, sql, parameter=(), many=False, few=True):
        """ execute sql """
        cls.__check_connect()
        cls.__dbexecute(sql, parameter, many)
        cls.sql_statement_log.append({time.time(): sql})

        return cls.__fetch(sql, few)

    @classmethod
    def rollback(cls):
        """ mysql rollback """
        return cls.db_connect.rollback()