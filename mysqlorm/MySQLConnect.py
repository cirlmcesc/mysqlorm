import pymysql as MySQLdb
import time


class MySQLConnect(object):
    """ MySQL connect"""

    mysql_connect_config = {}
    sql_statement_log = []
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
        """ set db connect, example:
            db_config = {
                "host": "127.0.0.1",
                "user": "root",
                "passwd": "",
                "db": "schema",
                "charset": "utf-8"
            }
        """

        if len(db_config):
            cls.mysql_connect_config = db_config

        cls.db_connect = MySQLdb.connect(**cls.mysql_connect_config)
        cls.db = cls.db_connect.cursor()

    @classmethod
    def execute(cls, sql, parameter=(), many=False):
        """ execute sql """

        try:
            cls.db_connect.ping()
        except:
            cls.connect()

        cls.sql_statement_log.append({time.time(): sql})

        try:
            if many:
                cls.db.executemany(sql, parameter)
            else:
                cls.db.execute(sql, parameter)

            if sql.upper().replace(" ", "").startswith("SELECT"):
                return cls.db.fetchall()
        except:
            print(cls.db._last_executed)

        return cls.db_connect.commit()

    @classmethod
    def log(cls):
        """ sql execute log"""
        return cls.sql_statement_log
