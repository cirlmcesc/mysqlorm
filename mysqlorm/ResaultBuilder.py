""" mysqldb connect package mysqlorm """
""" mysql resault builder            """

from mysqlorm.MySQLConnect import MySQLConnect


class ResaultBuilder(object):
    """ Resault Builder """

    @classmethod
    def execute(cls, sql, parameter=(), many=False):
        """ execute """
        return MySQLConnect.execute(sql, parameter=parameter, many=False)

    @classmethod
    def query(cls, builder, few=True):
        """ query """
        resault = MySQLConnect.execute(builder.BuildQuerySQLString(), few=few)

        if not resault:
            return () if few else None

        return tuple(map(lambda attributes: cls.buildORMModelInstance(builder._ormmodel, attributes), resault)) \
            if few else cls.buildORMModelInstance(builder._ormmodel, resault)

    @classmethod
    def buildORMModelInstance(cls, model, attributes):
        """ build model instance """
        return model(origin_attributes=attributes)
