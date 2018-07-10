import pymysql as MySQLdb


MYSQL_CONFIG = {
    "host": "localhost",
    "user": "root",
    "passwd": "qwe123",
    "db": "bilibili",
    "charset": "utf8"
}

def CheckConnect(func):
    def execute(*args, **kw):
        if isinstance(MySQLConnect.db_connect, dict) or MySQLConnect.execute_count > 100:
            MySQLConnect.connect(MYSQL_CONFIG)
            MySQLConnect.execute_count = 0
        return func(*args, **kw)
    return execute


class MySQLConnect(object):
    """ MySQL connect"""

    execute_count = 0
    sql_statement_log = []
    db_connect = {}
    db = {}

    @classmethod
    @CheckConnect
    def getDB(cls):
        return cls.db

    @classmethod
    @CheckConnect
    def getDBConnect(cls):
        return cls.db_connect

    @classmethod
    def connect(cls, db_config):
        """ set db connect, example:
            db_config = {
                "host": "127.0.0.1",
                "user": "root",
                "passwd": "",
                "db": "schema",
                "charset": "utf-8"
            }
        """
        cls.db_connect = MySQLdb.connect(**db_config)
        cls.db = cls.db_connect.cursor()

    @classmethod
    @CheckConnect
    def execute(cls, sql, parameter=(), many=False):
        """ execute sql """
        cls.sql_statement_log.append({time.time(): sql})
        cls.execute_count += 1

        try:
            if many:
                cls.db.executemany(sql, parameter)
            else:
                cls.db.execute(sql, parameter)

            if sql.upper().replace(" ", "").startswith("SELECT"):
                return cls.db.fetchall()
        except:
            print cls.db._last_executed

        return cls.db_connect.commit()

    @classmethod
    def log(cls):
        """ sql execute log"""
        return cls.sql_statement_log
