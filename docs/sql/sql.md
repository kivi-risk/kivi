# Kivi 链接数据库

## 通用数据库接口

- 目前支持：
	- MySql
	- Oracle
	- 支持其他类型数据库请联系作者进行源码修改。

> GetSqlEngine: 获取链接引擎

```python
from kivi import GetSqlEngine, ShowDataBase

# 链接信息
connectInfo = {
    'dataBaseType': 'MySql' or 'Oracle',
    'name': 'root',
    'password': 'your password',
    'host': 'localhost',
    'prot': '3306',
}

# 创建连接引擎
engine = GetSqlEngine(dataBaseName='mydatabase', connectInfo=connectInfo)
```

> ShowDataBase: 展示表与列名的实例
```python
# 实例化展示引擎
SB = ShowDataBase(engine)
# 展示DataBase的全部表
SB.showTable()
# 展示任意表的列名
SB.showColumns('TableName')
```
