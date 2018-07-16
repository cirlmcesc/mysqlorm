from mysqlorm.ResaultBuilder import ResaultBuilder
from mysqlorm.MySQLConnect import MySQLConnect


class QueryBuilder(object):
    """ Query Builder """

    def __init__(self, ormmodel):
        self._ormmodel = ormmodel
        self._table_name = ormmodel.table_name
        self._fields = "*"
        self._join = []
        self._where = []
        self._order = []
        self._group = []
        self._limit = ""
        self._final_sql = ""

    def select(self, *fields):
        """ set select fields """
        if not len(fields):
            self._fields = "*"
        elif len(fields) > 0:
            self._fields = "id, " + (", ".join(fields))

        return self

    def BuildQuerySQLString(self):
        """ build sql string """
        if isinstance(self._fields, list):
            field = tuple(self._fields).__str__().replace('(', '')
            field = field.replace(')', '')
        else:
            field = self._fields

        sql = "SElECT %s FROM %s" % (field.replace("'", ''), self._table_name)

        return sql + "".join(
            map(lambda condition: self._buildConditionString(condition), [
                "_join", "_where", "_group", "_order", "_limit"
            ]))

    def _buildConditionString(self, condition):
        """ build condition string """
        def transConditionString():
            """ transformation condition string """
            if condition == "_order":
                return " ORDER BY "
            elif condition == "_group":
                return " GROUP BY "

            return "%s " % condition.replace("_", " ").upper()

        content = getattr(self, condition)
        joinstring = ", " if condition == "_order" or condition == "_group" else " "
        startstring =  " " if condition == "join" else transConditionString()

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
        return self.join(table, current_table_field,
                         target_table_field, _cmp="LEFT JOIN")

    def rightJogin(self, table, current_table_field, target_table_field):
        """ right join """
        return self.join(table, current_table_field,
                         target_table_field, _cmp="RIGHT JOin")

    def where(self, field, *args, **kw):
        """ where """

        if len(self._where) > 0 and self._where[-1] != "AND" and self._where[-1] != "OR":
            self._where.append("AND" if not len(kw) else kw['_cmp'])

        if hasattr(field, "__call__"):
            builder = field(QueryBuilder(self._ormmodel))
            self._where.append("(%s)" % builder._buildConditionString("_where").replace(" WHERE ", ""))
        elif isinstance(field, list):
            for condition in field:
                self.where(*condition)
        else:
            _cmp = "=" if len(args) == 1 else args[0]
            value = args[0] if len(args) == 1 else args[1]
            restring = value.replace(" ", "") if isinstance(value, str) else str(value)

            if (not isinstance(value, int) or
                not restring.startswith("(") or
                not restring.startswith("'") or
                not restring.startswith("NULL")):
                value = "'%s'" % value

            self._where.append(" ".join((field, _cmp, value)))

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

    def update(self, attributes):
        """ execute update """
        source_fields = ["%s = %s" % (attr, "%s") for attr in attributes]
        srouce_value = [attributes.get(attr, '') for attr in attributes]
        sql = ("UPDATE %s SET " % self._table_name) + ", ".join(source_fields)
        sql = sql + self._buildConditionString("_where")

        return MySQLConnect.execute(sql, parameter=srouce_value)

    def delete(self):
        """ execute delete """
        sql = "DELETE FROM %s" % self._table_name
        sql = sql + self._buildConditionString("_where")

        return MySQLConnect.execute(sql)

    def get(self):
        """ query data """
        return ResaultBuilder.query(self)

    def first(self):
        """ query first one col data """
        return ResaultBuilder.query(self, few=False)

    def has(self):
        """ check has """
        return len(ResaultBuilder.query(self)) > 0
