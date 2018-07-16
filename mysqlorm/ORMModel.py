""" mysqldb connect package MysqlORM """

import random
import time
from mysqlorm.MySQLConnect import MySQLConnect
from mysqlorm.QueryBuilder import QueryBuilder
from mysqlorm.ResaultBuilder import ResaultBuilder


class ORMModel(object):
    """ Model """

    no_attribute = (
        "fields", "table_name", "_ORMModel__id", "origin_attributes", "origin_id")

    def __init__(self, table_name="", attributes={}, origin_attributes={}):
        if not isinstance(attributes, dict) and not isinstance(origin_attributes, list):
            raise AttributeError("data type error.")

        self.fields = []

        if self.table_name == "" and table_name == "":
            self.table_name = self.__class__.__name__.lower()
        elif table_name != "":
            self.table_name = table_name

        def setModelInstanceAttribute(attributedata):
            for val in attributedata:
                self.__setattr__(val, attributedata.get(val, None))

        if isinstance(attributes, dict) and len(attributes):
            setModelInstanceAttribute(attributes)

        if isinstance(origin_attributes, dict) and len(origin_attributes):
            self.origin_attributes = origin_attributes
            self.origin_id = origin_attributes.get("id", "")
            setModelInstanceAttribute(origin_attributes)
        else:
            self.origin_attributes = origin_attributes
            self.origin_id = 0

    def __setattr__(self, attr, value):
        if not attr in self.no_attribute and not attr in self.fields:
            fields = self.fields
            fields.append(attr)
            self.__dict__["fields"] = fields

        self.__dict__[attr] = value

    def __getattribute__(self, attr):
        new_instance = super(ORMModel, self)

        if attr == "table_name" and new_instance.__getattribute__("table_name") == "":
            return new_instance.__class__.__name__.lower()

        try:
            return new_instance.__getattribute__(attr)
        except AttributeError:
            return ""

    @classmethod
    def get(cls):
        """ get all data """
        return cls.all()

    @classmethod
    def all(cls):
        """ get all data """
        return QueryBuilder(cls).get()

    @classmethod
    def first(cls):
        """ get first data """
        return ResaultBuilder.query(QueryBuilder(cls).limit(1), few=False)

    @classmethod
    def update(cls, data):
        """ update data """
        return QueryBuilder(cls).update(data)

    @classmethod
    def insert(cls, data):
        """ attribute insert to table"""
        if (not isinstance(data, list) and
            not isinstance(data, dict)) or not len(data):
            raise AttributeError("data type error.")

        def BuildInsertValueParam():
            """ build param """
            def builddata(value):
                return tuple([value.get(field, '') for field in value])

            return builddata(data) if isinstance(data, dict) else [
                builddata(instance) for instance in data
            ]

        def BuildFieldsString(fields):
            fields = tuple(fields)

            if len(fields) == 1:
                return "(%s)" % fields[0]
            else:
                tuple(fields).__str__().replace("'", '')

        fields = data.keys() if isinstance(data, dict) else random.choice(data).keys()
        sql = "INSERT INTO %s %s VALUES %s" % (
            cls.table_name,
            BuildFieldsString(fields),
            "(%s)" % ", ".join(["%s" for index in range(len(fields))]))

        return MySQLConnect.execute(
            sql, parameter=BuildInsertValueParam(), many=isinstance(data, list))

    @classmethod
    def find(cls, data_id):
        """ get the id data """
        return QueryBuilder(cls).where('id', data_id).first()

    @classmethod
    def select(cls, *fields):
        """ select """
        return QueryBuilder(cls).select(*fields)

    @classmethod
    def where(cls, field, *args, **kw):
        """ new QueryBuilder and .where """
        return QueryBuilder(cls).where(field, *args, **kw)

    @classmethod
    def has(cls, field, *args, **kw):
        """ check has """
        return QueryBuilder(cls).where(field, *args, **kw).has()

    @classmethod
    def query(cls, sql):
        """ execute sql string """
        return MySQLConnect.execute(sql)

    @staticmethod
    def DB():
        """ get MySQLConnect.db """
        return MySQLConnect.getDB()

    @staticmethod
    def log():
        """ get MySQLConnect.sql_statement_log """
        return MySQLConnect.sql_statement_log

    def arrangeAttributes(self):
        """ arrange self attribute """
        attributes = dict().fromkeys(self.fields)

        for attr in attributes:
            if attr != '_ORMModel__id':
                attributes[attr] = getattr(self, attr)

        return attributes

    def save(self):
        """ update model attribute change """
        attributes = self.arrangeAttributes()

        if len(self.origin_attributes):
            QueryBuilder(self).where("id", self.origin_id).update(attributes)

            return self.find(self.origin_id)

        return self.insert(attributes)

    def delete(self):
        """ delete this model data """
        if self.origin_id == 0:
            raise AttributeError("Instance have not attribute 'ID'")

        return QueryBuilder(self).where("id", self.origin_id).delete()

    def dict(self):
        """ self to dict """
        d = {}

        for field in self.fields:
            d[field] = getattr(self, field)

        return d
