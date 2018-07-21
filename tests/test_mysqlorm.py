import os, random
import sys; sys.path.append('/Users/cirlmcescma/www/python/mysqlorm')
from mysqlorm import ORMModel, MySQLConnect


mysql_connect_config = {
    "host": "127.0.0.1",
    "user": "root",
    "passwd": "qwe123",
    "db": "ormmodel_test",
}

class TestModel(ORMModel):
    table_name = "ormmodel_test"

def test_connect():
    MySQLConnect.connect(mysql_connect_config)
    MySQLConnect.db_connect.ping()

def test_insert():
    TestModel.insert({"test": "test ormmodel single insert"})
    TestModel.insert([{"test": "test ormmodel batch insert"}, {"test": "test ormmodel batch insert"}])
    model = TestModel(attributes={"test": "test ormmodel instance save insert"})
    model.save()

def test_query():
    TestModel.get()
    TestModel.first()
    TestModel.find(random.choice(range(1, len(TestModel.get()))))
    TestModel.where('id', ">", 1).where('test', 'like', 'test').orderBy('id').limit(11).get()

def test_update():
    TestModel.update({"test": "batch update"})

    for instance in TestModel.all():
        instance.test = "instance update"
        instance.save()

def test_delete():
    for instance in TestModel.all():
        instance.delete()


if __name__ == "__main__":
    test_connect()
    test_insert()
    test_query()
    test_update()
    test_delete()
    print(MySQLConnect.sql_statement_log)

