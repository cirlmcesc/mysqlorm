import MySQLConnect


class ResaultBuilder(object):
    """ Resault Builder """

    @classmethod
    def execute(cls, sql, parameter=(), many=False):
        """ execute """
        return MySQLConnect.execute(sql, parameter=parameter, many=False)

    @classmethod
    def query(cls, builder, few=True):
        """ query """
        resault = MySQLConnect.execute(builder.BuildQuerySQLString())

        if not len(resault):
            return [] if few else None

        if few:
            return list(map(
                lambda attributes:cls.buildORMModelInstance(builder._ormmodel, attributes), resault))
        else:
            return cls.buildORMModelInstance(builder._ormmodel, resault[0])

    @classmethod
    def buildORMModelInstance(cls, model, attributes):
        """ build model instance """
        return model(origin_attributes=attributes)
