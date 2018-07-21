# mysqlorm


TL:DR
-----
A simple ORM MySQL operation Library, running on Python3.
Automatic long connection，support chain call, more secure statement generation and the MySQL query can be constructed more elegantly.


Installation
------------
Install via pip
```
(sudo) pip(3) install mysqlorm
```


Usage
-----
Begin by importing the mysqlorm module:
```python
from mysqlorm import ORMModel, MySQLConnect
```

You need to link the database before use：
```python
mysql_connect_config = {
    "host": "host",
    "user": "user",
    "passwd": "passwd",
    "db": "db",
}
MySQLConnect.connect(mysql_connect_config)
```

Create a class to inherit ormmodel and set `table_name` attribute:
(If no `table_name` attribute is set, use the lowercase class name by default.)
```python
class ExampleModel(ORMModel):
    table_name = "exampletable"
```

Insert:
```python
ExampleModel.insert({"field1": "value1", "field2", "value2"}) # single insert
ExampleModel.insert(( # batch insert, can use tuple or list
    {"field1": "value1", "field2", "value2"}, 
    {"field1": "value1", "field2", "value2"}))
```

Where:
```python
# Support call chaining.
# The `where` method can pass 2 or 3 parameters.
# If two parameters are passed, the comparison symbol uses the equal sign by default.
# Call chaining use `and` connection condition, you must use `orWhere` method to `or` condition
ExampleModel.where("field", "value").where("field", ">", "value")
ExampleModel.where("field", "value").orWhere("field", ">", "value")
# Support batch afferent condition, can use tuple or list.
# Use `and` connection condition
ExampleModel.where((("filed1", "value1"), ("filed2", "value2")))
# Support aggregation condition query.
# Or you can use lambda method.
def condition(query):
    return query.where("field", "value").where("field1", ">", "value")

ExampleModel.where(condition).orWhere(
    lambda query: return query.where("field", "value").where("field1", "<", "value")
)
# The `like` condition uses the "LOCATE()" implementation.
# because the `%` symbol is a special symbol in Python will cause some problems. 
# So do not pass in the `where` method the parameter with the `%` symbol.
ExampleModel.where("file", 'like', "value")
# You can use `whereIn` and `whereNotIn` method.
# Can use tuple or list.
ExampleModel.whereIn("field", TupleOrList).whereNotIn("field", TupleOrList)
# You can use `whereBetween` and `whereNotBetween`.
ExampleModel.whereBetween("field", "from_condition", "to_condition"
    ).whereNotBetween("field", "from_condition", "to_condition")
# You can use `whereNull` and `whereNotNull`.
ExampleModel.whereNull("field1").whereNotNull("field2")
```

Query:
```python
# You can use `select` method to defining query fields.
# If a parameter is not passed, use by default `*`.
# The default is to query `id`.
# Or can not use `select` method.
query = ExampleModel.select("field1", "field2", "field3")# n field parameters can be passed in.
# All queries support the `where` method conditional queries.
query.where("field", "value")
# You can use `when` method.
# Execute the query when the value is true or skip.
# The second parameter can be a function, like the use of the `where` method.
import random
a = random.choice(range(1, 10))
b = random.choice(range(1, 10))
query.when(a != b, condition).when(a == b, lambda query: return query.where("field", "value"))
# You can use `orderBy` method to sort resault.
# The `orderBy` method can pass 1 or 2 parameters.
# If one parameter passed, use 'ASC' by default.
query.orderBy("field")
# You can use `groupBy` method
# But you must pay attention to the problems caused by `sql_mode=only_full_group_by`
query.groupBy("field")
# You can use `limit` method
# The `where` method can pass 1 or 2 parameters.
# If one parameter is passed, offer use 0 by default.
query.limit(0, 10)
# The query returns are all model instances.
# Can easy to operate on a single instance.
query.all() # to get all data
query.find(1) # to find data from id
query.get() # to get data what query according to conditions
query.first() # to get first raw data what query according to conditions
```

Update:
```python
# The `update` method supports the `where` conditions.
ExampleModel.update({"field1": "value1", "field2", "value2"}) # batch update
ExampleModel.where("field", "value").update({"field1": "value1"})
```

Delete:
```python
# The `delete` method supports the `where` conditions.
ExampleModel.where("field", "value").delete()
```

ORMModel:
```python
# ORMModel instances can be operated on a variety of operations.
# You can get a ormmodel instance in this way:
example = ExampleModel(attributes=attr) # attr must be a dict that matches the database field
# You can use the `save` method to insert data.
example.save()
# You can use the `save` method to update data or use the `delete` method to delete data.
# But the instances must from query resault.
example = ExampleModel.find(1)
example.field = "new value"
example.save() # update data
example.delete() # delete data
# Converting ormmodel instances to dict with `dict` method
example.dict()
```

TODO
----
* Perfect the join table query.
* Add more functions for ormmodel.
* Increase the association between ormmodel.