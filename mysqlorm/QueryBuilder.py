""" mysqldb connect package mysqlorm  """
""" mysql query statement builder     """

import random
from inspect import isfunction
from mysqlorm.ResaultBuilder import ResaultBuilder
from mysqlorm.MySQLConnect import MySQLConnect


class QueryBuilder(object):
    """ Query Builder """

    _selectstr = "SElECT %s FROM `%s`"
    _updatestr = "UPDATE `%s` SET "
    _deletestr = "DELETE FROM `%s`"
    _insertstr = "INSERT INTO `%s` %s VALUES %s"

    def __init__(self, ormmodel):
        self._ormmodel = ormmodel
        self._table_name = ormmodel.table_name
        self._fields = "`*`"
        self._join = []
        self._where = []
        self._order = []
        self._group = []
        self._limit = ""
        self._like_value = []

    def select(self, *fields):
        """ set select fields """
        if len(fields) > 0:
            self._fields = "`id`, " + (", ".join(list(map(
                lambda f: self._TableFieldAddGrave(f) if "." in f else "`%s`" % f, fields))))

        return self

    def BuildQuerySQLString(self):
        """ build sql string """
        if isinstance(self._fields, list):
            field = tuple(self._fields).__str__().replace('(', '')
            field = field.replace(')', '')
        else:
            field = self._fields

        sql = self._selectstr % (field.replace("'", ''), self._table_name)

        return sql + "".join(map(lambda condition: self._buildConditionString(condition), [
            "_join", "_where", "_group", "_order", "_limit"
        ]))

    def _transConditionString(self, condition):
        """ transformation condition string """
        if condition == "_order":
            return " ORDER BY "
        elif condition == "_group":
            return " GROUP BY "

        return "%s " % condition.replace("_", " ").upper()

    def _buildConditionString(self, condition):
        """ build condition string """
        content = getattr(self, condition)
        joinstring = ", " if condition == "_order" or condition == "_group" else " "
        startstring =  " " if condition == "join" else self._transConditionString(condition)

        if isinstance(content, str) and len(content):
            return startstring + content

        return (startstring + joinstring.join(content)) if len(content) else ""

    def join(self, table, current_table_field, target_table_field, **kw):
        """ join """
        self._join.append("%s %s ON %s = %s" % (
            "INNER JOIN" if not len(kw) else kw["_cmp"],
            table, current_table_field, target_table_field))

        return self

    def leftJoin(self, table, current_table_field, target_table_field):
        """ left join """
        return self.join(table, current_table_field, target_table_field, _cmp="LEFT JOIN")

    def rightJogin(self, table, current_table_field, target_table_field):
        """ right join """
        return self.join(table, current_table_field, target_table_field, _cmp="RIGHT JOin")

    def _ConnectWhereString(self, whereCmp):
        if len(self._where) > 0 and self._where[-1] != "AND" and self._where[-1] != "OR":
            self._where.append(whereCmp)

    def _appendBuildWhereString(self, field, *args, **kw):
        _cmp = "=" if len(args) == 1 else args[0]
        value = args[0] if len(args) == 1 else args[1]
        restring = value.replace(" ", "") if isinstance(value, str) else str(value)
        field = self._TableFieldAddGrave(field) if "." in field else "`%s`" % field

        if (not restring.startswith("(") or
            not restring.startswith("'") or
            not restring.startswith("NULL")):
            valuestr = "%s" if isinstance(value, int) and isinstance(value, float) else "'%s'"
            value = valuestr % value

        self._where.append(" ".join((field, _cmp, value)))

        return self

    def where(self, field, *args, **kw):
        """ where """
        self._ConnectWhereString("AND" if not len(kw) else kw['_cmp'])

        if isfunction(field):
            builder = field(QueryBuilder(self._ormmodel))
            self._where.append("(%s)" % builder._buildConditionString("_where").replace(" WHERE ", ""))
        elif isinstance(field, list) or isinstance(field, tuple):
            for condition in field:
                self.where(*condition)
        else:
            if len(args) > 1 and "LIKE" in args[0].upper():
                self._whereLike(field, args[1],
                    _cmp="NOT LIKE" if "NOT" in args[0].upper() else "LIKE")
            else:
                self._appendBuildWhereString(field, *args, **kw)

        return self

    def when(self, booleanvalue, condition):
        """ execute when the Boolean value is true """
        if booleanvalue:
            return condition(self)

        return self

    def _TableFieldAddGrave(self, field):
        """ field add grave """
        field = field.split(".")
        field[len(field) - 1] = "`%s`" % field[len(field) - 1]

        return ".".join(field)

    def _whereLike(self, field, value, _cmp):
        """ like """
        field = self._TableFieldAddGrave(field) if "." in field else "`%s`" % field
        self._where.append("LOCATE('%s', %s) > 0" % (value, field))

        return self

    def orWhere(self, field, *args):
        """ or where """
        return self.where(field, *args, _cmp="OR")

    def whereIn(self, field, _tuple, **kw):
        """ where in """
        _cmp = "IN" if not len(kw) else kw["_cmp"]
        return self.where(field, _cmp, "('%s')" % ("' ,'".join(_tuple)))

    def whereNotIn(self, field, _tuple):
        """ where not in """
        return self.whereIn(field, _tuple, _cmp="NOT IN")

    def whereBetween(self, field, from_condition, to_condition, **kw):
        """ where between """
        between = "BETWEEN" if not len(kw) else kw["_cmp"]

        return self.where(field, between, "'%s' AND '%s'" % (from_condition, to_condition))

    def whereNotBetween(self, field, from_condition, to_condition):
        """ where not between """
        return self.whereBetween(field, from_condition, to_condition, _cmp="NOT BETWEEN")

    def whereNull(self, field, **kw):
        """ where field null """
        _cmp = "IS" if not len(kw) else kw["_cmp"]

        return self.where(field, _cmp, "NUll")

    def whereNotNull(self, field):
        """ where field is not null"""
        return self.whereNull(field, _cmp="IS NOT")

    def limit(self, offset, *args):
        """ limit """
        number = offset if not len(args) else args[0]
        offset = 0 if not len(args) else offset
        self._limit = "%d, %d" % (offset, number)

        return self

    def orderBy(self, field, *args):
        """ order by """
        _cmp = "ASC" if not len(args) else "DESC"
        self._order.append(" ".join((field, _cmp)))

        return self

    def groupBy(self, field):
        """ group by """
        if isinstance(field, str):
            self._group.append(field)
        elif isinstance(field, list):
            self._group = field

        return self

    def get(self):
        """ query data """
        return ResaultBuilder.query(self)

    def first(self):
        """ query first one col data """
        return ResaultBuilder.query(self, few=False)

    def has(self):
        """ check has """
        return len(ResaultBuilder.query(self)) > 0

    def update(self, attributes):
        """ execute update """
        source_fields = ["%s = %s" % (attr, "%s") for attr in attributes]
        srouce_value = [attributes.get(attr, '') for attr in attributes]
        sql = (self._updatestr % self._table_name) + ", ".join(source_fields)
        sql = sql + self._buildConditionString("_where")

        return MySQLConnect.execute(sql, parameter=srouce_value)

    def delete(self):
        """ execute delete """
        sql = self._deletestr % self._table_name
        sql = sql + self._buildConditionString("_where")

        return MySQLConnect.execute(sql)

    def insert(self, data):
        """ attribute insert to table"""
        if (not isinstance(data, list) and
            not isinstance(data, dict)) or not len(data):
            raise AttributeError("data type error.")

        fields = data.keys() if isinstance(data, dict) else random.choice(data).keys()
        sql = self._insertstr % (self._table_name, self._buildInserFieldsString(fields),
            "(%s)" % ", ".join(["%s" for index in range(len(fields))]))

        return MySQLConnect.execute(sql,
            parameter=self.__buildInsertValueParam(data),
            many=isinstance(data, list))

    def __buildInsertValueParam(self, data):
        """ build param """
        return self._builddata(data) if isinstance(data, dict) else [
            self._builddata(instance) for instance in data
        ]

    def _builddata(self, value):
        """ build param data """
        return tuple([value.get(field, '') for field in value])

    def _buildInserFieldsString(self, fields):
        """ build field string """
        fields = tuple(fields)

        if len(fields) == 1:
            return "(%s)" % fields[0]
        else:
            tuple(fields).__str__().replace("'", '')

            return fields