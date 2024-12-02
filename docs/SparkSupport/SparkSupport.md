# SparkSupport

> 这里封装了一些支持`Spark`集群操作表的方法，大概有以下意图：

1. 简化了对于`Hive`表的操作，减少了读写`Hive`表的`Sql`代码量，使得前端分析代码的结构精简，提高前端分析代码的可读性。
2. 使得批量操作表更加的简单规范，提高代码的效率，减少误操作与Bug。

---

```python
from kivi.SparkSupport import *
# OR
from ywcxUtils.SparkSupport import *
```

## 1. 性能

### 1.1 `EnableArrow`

> 说明：打开 `Arrow` 加速。

> 参数

- `:param spark`: `spark session`
- `:param disp`: 是否展示Arrow开启状态

> 示例

```python
EnableArrow(spark, disp=False)
```

### 1.2 `broadcast` 广播

> 说明：应用于数据量不对称时，对小数据进行广播运算，以减少通讯成本，提高运行效率。

> 示例

```python
# 1. 过滤
broadcast_info = F.broadcast(['a', 'b'])
df_filter= df.where((df['state'].isin(broadcast_info.value)))

# 2. 关联
df_big = df_big.join(F.broadcast(df_small), on='uid')
```

## 2. Hive 表的操作

### 2.1 `FrameToHive`将Spark DataFrame存储至Hive表

> 说明：将`Spark DataFrame`存储至Hive表

> 参数

- `:param df`: pyspark dataframe.
- `:param db`: database name.
- `:param table_name`: table name.
- `:param spark`: spark session.
- `:param comment`: hive table comment.
- `:param partitionBy`: partition columns name.
- `:param mode`: table write mode.
- `:param repartition`: When not specified partition, specify the number of data blocks.
- `:param disp`: display saving message.

> 示例

```python
FrameToHive(df, db, table_name, spark=None, comment=None, 
    partitionBy=None, mode='overwrite', repartition=None, disp=True)
```

### 2.2 `CreateTableBySchema`依据表结构创建空表

> 说明：创建一个空表，以备写入数据。

> 参数

- `:param schema:` table schema.
- `:param table_name:` table name.
- `:param partitionBy[list]:` partition columns. eg. ['biz_code', 'load_date'].
- `:param db_name:` database name.
- `:param spark:` spark session.
- `:param mode:` default `overwrite`.

> 示例

```python
schema = StructType([
    StructField('uuid', StringType(), False), 
    StructField('biz_code', StringType(), False), 
    StructField('index_val', StringType(), True), 
    StructField('load_date', StringType(), False), 
])

CreateTableBySchema(
    schema, table_name, partitionBy='load_date', db_name='tmp_work', 
    spark=spark,)
```

### 2.3 `InsertIntoHive`将数据插入分区表中

> 说明：向Hive表中插入数据，默认覆盖分区下的内容。

> 参数

- `:param df`: pyspark dataframe.
- `:param db_name`: database name.
- `:param table_name`: table name.
- `:param partition`: partition columns.
- `:param partition_val`: partition values.
- `:param spark`: spark session.
- `:param mode`: write mode, default `overwrite`.
- `:param query_mode`: *this parameter not work now*.

> 示例

```python
InsertIntoHive(
    df, 'tmp_work', 't_cch_uuid_info', partition=['biz_code', 'load_date'],
    partition_val=['industry', '20190101'], spark=spark)
```

### 2.4 `SaveBigDFToHive`将Pandas.DataFrame存储至Hive

> 说明：将模型结果保存至Hive表中，以5万为默认保存批次

> 参数

- `:param df[pandas.DataFrame]`: pandas dataframe.
- `:param db_name[str]`: database name.
- `:param table_name[str]`: table name.
- `:param spark[spark session]`: spark session.
- `:param batch[int]`: one batch data size of save pyspark dataframe.

> 示例

```python
SaveBigDFToHive(df_now_woe, 'tmp_work', 't_cch_sample_woe_20210531', spark)
```

### 2.5 `ShowTablePartitions` 提取表的分区信息

> 说明：

1. 快速查询`Hive`表的元数据，提取表的分区信息。
2. 一般用于查看数据分区是否正常，或通过该方法查询还有哪些分区没有数据，用于数据的断点重跑。

> 参数：

- `:param table_name`: Hive Table.
- `:param spark`: spark session.
- `:return `: `pandas.DataFrame`.

> 示例：

```python
df_part = ShowTablePartitions('tmp_work.t_cch_sample_long', spark=spark)
```

### 2.6 `DropPartition` 删除分区

> 说明：删除某表的某分区。

> 参数

- `:param db_name`: database name.
- `:param table_name`: hive table name.
- `:param partition`: partition name.
- `:param spark`: spark session.

> 示例

```python
DropPartition(db_name, table_name, partition, spark=spark)
```

### 2.7 `drop_table` 删除表

> 说明: drop Hive table.

> 参数

- `:param db_name`: database name.
- `:param table_name`: table name.
- `:param spark`: spark session.

> 示例

```python
drop_table(db_name, table_name, spark=spark)
```

### 2.8 `rename_table` 重命名表

> 说明: `Hive` 表的重命名。

> 参数

- `:param pre_db_name`: 原表库名。
- `:param pre_table_name`: 原表名。
- `:param db_name`: 新库名。
- `:param table_name`: 新表名。
- `:param spark`: spark session。

> 示例

```python
rename_table(
    pre_db_name, pre_table_name, 
    db_name=None, table_name=None, spark=None)
```

### 2.9 `findTables` 查找某一类表

> 说明：查找某一类表。

> 参数

- `:param db_name:` 库名。db_name与tables二选一指定
- `:param tables:` 表名。db_name与tables二选一指定
- `:param pat:` 表名正则模式。
- `:param spark:` spark
- `:return :` table list.

> 示例

```python
findTables(db_name=None, tables=None, pat=None, spark=None)
```

### 2.10 `checkTableExits` 检查某表是否存在

> 说明: 检查某表是否存在

> 参数

- `:param: db`: database name.
- `:param: table_name`: table name.
- `:param: spark`: spark session.
- `:return: `: `True` OR `False`
> 示例

```python
checkTableExits(db, table_name, spark=None)
```

### 2.11 `getTableColumns` 获取表的全部列名

> 说明：获取表的全部列名

> 参数

- `:param: db`: database name.
- `:param: table_name`: table name.
- `:param: spark`: spark session.

> 示例

```python
getTableColumns(db, table_name, spark)
```

### 2.12 `HiveTableToCSV` 提取`Hive Table`至`CSV`文件

> 说明:  提取`Hive Table`至`CSV`文件；应用于`100万`数据量以下，从`Hive`库中提取至本地`CSV`。
> 参数

- `:param csv_path`: `csv`文件路径。
- `:param db_name`: 库名。
- `:param table_name`: 表名；与query二选一指定。
- `:param query`: SQL query；与table_name二选一指定。

> 示例

```python
# 表名模式
HiveTableToCSV('./sample.csv', db_name='temp', table_name='t_test_sample')

# query 模式
query = """
SELECT * FROM temp.t_test_sample
"""
HiveTableToCSV('./sample.csv', query=query)
```

## 3. 其他`Spark`支持

### 3.1 `getSpark` 获取 `spark session`

> 说明: 获取 `spark session`

> 参数

- `:param app_name`: spark session 名称。
- `:param master`: `yarn` 集群模式，`local[*]` 本地模式。
- `:param executors`: 执行核心数。

> 示例

```python
spark = getSpark(app_name='sample', master='yarn', executors=800)
```

### End

----
