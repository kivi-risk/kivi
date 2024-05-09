

import re
import os
import logging
from pyspark.sql import functions as F
from pyspark.sql.types import StructField, StringType
from pyspark.sql.window import Window


__all__ = [
    'get_spark',
    'long_to_wide',
    'EnableArrow',
    'mapLabel',
    'unpivot',
    'drop_table',
    'rename_table',
    'findTables',
    'checkTableExits',
    'getTableColumns',
    'SaveBigDFToHive',
    'toPdFrame',
    'toPySparkFrame',
    'InsertIntoHive',
    'FrameToHive',
    'ShowTablePartitions',
    'DropPartition',
    'CreateTableBySchema',
    'convert_col_to_list',
    'KillApp',
    'HiveTableToCSV',
    'get_db_table',
    'get_part_info',
]


def get_spark(app_name='zlx', master='yarn', executors=2):
    """

    :param app_name:
    :param master: 'yarn', 'local[*]'
    :param executors:
    :return:
    """
    import pyspark

    if hasattr(pyspark, "SparkService"):
        from pyspark import SparkService
        extra_param = {
            'spark.app.name': app_name,
            'spark.driver.cores': 2,
            'spark.sql.execution.arrow.pyspark.enabled': 'true',
        }
        spark = SparkService.get_yarn_spark(
            executor_instances=executors,
            per_executor_mem='2g',
            driver_mem='1g',
            extra_param=extra_param,
        )
    elif hasattr(pyspark.sql, 'SparkSession'):
        from pyspark.sql import SparkSession
        builder = SparkSession.builder \
            .appName(app_name) \
            .enableHiveSupport() \
            .master(master) \
            .config("spark.dynamicAllocation.maxExecutors", f"{executors}")
        spark = builder.getOrCreate()
    else:
        raise ValueError("Not support for Spark, please check your env.")
    return spark


def long_to_wide(df_long, index=['uuid', 'load_date'], columns='index_name', values='index_val'):
    """

    :param df_long:
    :param index:
    :param columns:
    :param values:
    :return:
    """
    df_wide = df_long.groupBy(index).pivot(columns).agg(
        F.first(values))
    return df_wide


def EnableArrow(spark, disp=False):
    """
    描述：开启Arrow加速模式。

    参数：
    :param spark: spark入口
    :param disp: 是否展示Arrow开启状态
    :return None:
    """
    spark.conf.set("spark.sql.execution.arrow.enabled", "true")
    if disp:
        print(f'Enable Arrow: {spark.conf.get("spark.sql.execution.arrow.enabled")}')


def mapLabel(mapping):
    """
    描述：[UDF] 用来匹配 pyspark DataFrame 中的键值对

    参数：
    :param mapping[Dict]: 需要匹配的字典

    示例：使用行业分类码值表，设置一列中文行业名称。
    >>> df.withColumn('industryCnName', mapLabel(industryDict)(df.industryCode))
    """
    def f(value):
        return mapping.get(value)
    return F.udf(f, returnType=StringType())


def unpivot(df, columns, val_type=None, index_name='uuid', feature_name='name', feature_value='value', orderby=None):
    """
    描述：对数据表进行反 pivot 操作

    参数：
    :param df:
    :param columns:
    :param index_name:
    :param feature_name:
    :param feature_value:
    :return:
    """
    if val_type is not None:
        columns_type = [F.col(col).cast(val_type()) for col in columns]
    else:
        columns_type = columns

    stack_query = []
    for col in columns:
        stack_query.append(f"'{col}', `{col}`")

    if isinstance(index_name, str):
        index_name = [index_name]

    df = df.select(*index_name, *columns_type)

    df = df.selectExpr(
        *index_name, f"stack({len(stack_query)}, {', '.join(stack_query)}) as (`{feature_name}`, `{feature_value}`)"
    )

    if orderby:
        df = df.orderBy(orderby)

    return df


def drop_table(db_name, table_name, spark=None):
    """
    描述： 给的库名、表名，删除相应的Table

    参数：
    :param db_name: 库名
    :param table_name: 表名，接受 str 或 list
    :param spark:
    :return None:
    """

    def drop(db_name, table_name, spark=None):
        if spark.catalog._jcatalog.tableExists(f'{db_name}.{table_name}'):
            print(f'drop old table {db_name}.{table_name}')
            spark.sql(f'drop table if exists {db_name}.{table_name}')
            print(f'Table {db_name}.{table_name} has been droped!')
        else:
            print(f'Table {db_name}.{table_name} not exit!')

    if isinstance(table_name, list):
        for name in table_name:
            drop(db_name, name, spark)
    elif isinstance(table_name, str):
        drop(db_name, table_name, spark)
    else:
        raise TypeError('table_name')


def rename_table(pre_db_name, pre_table_name, db_name=None, table_name=None, spark=None):
    print(f'Pre table {pre_db_name}.{pre_table_name}')
    if db_name is None:
        db_name = pre_db_name
    if table_name:
        spark.sql(f'ALTER TABLE {pre_db_name}.{pre_table_name} RENAME TO {db_name}.{table_name}')
    print(f'Rename to {db_name}.{table_name}')


def findTables(db_name=None, tables=None, pat=None, spark=None):
    """
    描述：选择相应模式的Table

    参数：
    :param db_name: 库名。db_name与tables二选一指定
    :param tables: 表名。db_name与tables二选一指定
    :param pat: 表名正则模式。
    :param spark: spark
    :return : table list for pat.
    """
    if db_name is None and tables is None:
        raise ValueError("db_name, tables")

    elif db_name is not None and tables is None:
        db_tables = spark.catalog.listTables(db_name)
        tables = [table_info.name for table_info in db_tables]

    pattern = re.compile(pat)
    find_res = list(map(pattern.findall, tables))
    find_tables = []
    for table, mask_info in zip(tables, find_res):
        if len(mask_info) != 0:
            find_tables.append(table)
    return find_tables


def checkTableExits(db, table_name, spark=None):
    """
    描述： 检查表是否已经存在

    :param db: 库名
    :param table_name: 表名
    :param spark: spark对象
    :return : True or False
    """
    if spark.catalog._jcatalog.tableExists(f'{db}.{table_name}'):
        return True
    else:
        return False


def getTableColumns(db_name: str, table_name: str, spark=None):
    """
    描述：获取表的列名称

    参数：
    :param db_name[str]: 库名
    :param table_name[str]: 表名
    :param spark:
    :return columns_name[list[str]]: 表列名

    示例：
    >>> getTableColumns('temp_work', 'test', spark)
    """
    columns_info = spark.catalog.listColumns(table_name, db_name)
    columns_name = [col.name for col in columns_info]
    return columns_name


def SaveBigDFToHive(df, db_name, table_name, reset=True, spark=None, batch=5e4, disp=False):
    """
    描述：将模型结果保存至Hive表中，以5万为默认保存批次

    参数：
    :param df[pandas.DataFrame]:
    :param db_name[str]:
    :param table_name[str]:
    :param if_exists[str]: `fail`, `replace`, `append`
    :param spark[spark session]:
    :param batch[int]:

    示例：
    >>> SaveBigDFToHive(df_now_woe, 'tmp_work', 't_cch_sample_woe_20210531', spark)
    """
    table_exist = checkTableExits(db=db_name, table_name=table_name, spark=spark)

    if reset and table_exist:
        drop_table(db_name, table_name, spark)

    for i in tqdm_notebook(range(int(len(df) // batch) + 1)):
        low = int(i * batch)
        up = int((i + 1) * batch)
        df_part = spark.createDataFrame(df.iloc[low: up, :])

        if disp:
            print(f'[{low}, {up}]')

        if i == 0 and reset:
            mode = 'overwrite'
        else:
            mode = 'append'

        FrameToHive(
            df_part, db=db_name, table_name=table_name, spark=spark, repartition=4,
            mode=mode, disp=disp)
        df_part.unpersist()


def toPdFrame(df, interval=5e4, index_name='index', columns=None, drop_index=True):
    """
    转换PySpark到Pandas DataFrame
    interval: 转换间距
    index_name:
    columns: 排序依据列
    drop_index: 返回值是否删除索引index
    """
    if columns is None:
        window = Window().orderBy(df.columns)
    else:
        window = Window().orderBy(columns)
    df = df.withColumn('index', F.row_number().over(window))
    length = df.count()

    df_pd = pd.DataFrame(columns=df.columns)
    for i in tqdm_notebook(range(int(length / interval) + 1)):
        lower = i * interval
        upper = (i + 1) * interval
        df_pd = df_pd.append(df.where((df.index < upper) & (df.index >= lower)).toPandas())

    if drop_index:
        return df_pd.drop(index_name, axis=1)
    else:
        return df_pd


def toPySparkFrame(pd_df, spark):
    pd_df = pd_df.where(pd.notnull(pd_df), None)
    return spark.createDataFrame(pd_df)


def InsertIntoHive(
        df, db_name, table_name, partition, partition_val,
        spark=None, mode='overwrite', query_mode=True):
    """
    描述：向Hive表中插入数据

    参数：
    :param df:
    :param db_name:
    :param table_name:
    :param partition:
    :param partition_val:
    :param spark:
    :param mode:
    :param query_mode:

    示例：
    >>> InsertIntoHive(
    >>>     df_2, 'tmp_work', 't_cch_uuid_info',
    >>>     partition=['biz_code', 'load_date'],
    >>>     partition_val=['industry', '20190101'], spark=spark)
    """
    if query_mode:

        part_conditions = []
        for part, part_val in zip(partition, partition_val):
            part_conditions.append(f"{part}='{part_val}'")
        if len(part_conditions) == 1:
            part_condition = str(f'{part_conditions[0]}')
        else:
            part_condition = str(', '.join(part_conditions))

        columns = getTableColumns(db_name, table_name, spark)
        for column in partition:
            if column in columns:
                columns.remove(column)

        df.createOrReplaceTempView("temp")
        df_empty = spark.sql(f"""
        INSERT OVERWRITE TABLE {db_name}.{table_name}
        PARTITION ({part_condition}) 
        SELECT {', '.join(columns)}
        FROM temp
        """)
    else:
        df.write.insertInto(f'{db_name}.{table_name}', True)


def FrameToHive(df, db, table_name, spark=None, comment=None,
                partitionBy=None, mode='overwrite', repartition=None, disp=True):
    '''
    保存表格到数据库
    '''
    if disp: logging.warning(f'Save DataFrame To {db}.{table_name}!')

    if partitionBy:
        df.write.mode(mode).partitionBy(partitionBy).saveAsTable(f'{db}.{table_name}')
    elif repartition:
        df.repartition(repartition).write.mode(mode).saveAsTable(f'{db}.{table_name}')
    elif spark:
        drop_table(db, table_name, spark)
        df.createOrReplaceTempView(f'{table_name}')
        spark.sql(f'create table {db}.{table_name} as select * from {table_name}')
        if comment is not None:
            spark.sql(f"ALTER TABLE {db}.{table_name} SET TBLPROPERTIES('comment'='{comment}')")
    else:
        raise Exception(f'table {db}.{table_name} save failed!')

    if disp: logging.warning(f'Save End!')

def ShowTablePartitions(table_name, spark=None):
    """
    描述：展示表的分区信息
    示例：
    >>> df_part = ShowTablePartitions('tmp_work.t_cch_sample_long', spark=spark)
    >>>
    """
    def parse_partition_value(row_value):
        row = dict()
        for item in row_value:
            key, value = item.split('=')
            row.update({key: value})
        return row
    df_part = spark.sql(f"SHOW PARTITIONS {table_name}").toPandas()
    part = df_part.partition.str.split('/').tolist()
    return pd.DataFrame(list(map(parse_partition_value, part)))


def DropPartition(db_name, table_name, partition, spark=None):
    """
    描述：删除分区

    参数：

    示例：
    >>>
    """
    query = f"""
    alter table {db_name}.{table_name} drop if exists partition (partition)
    """
    spark.sql(query)
    print(f'Table {db_name}.{table_name} partion: {partition} droped!')


def CreateTableBySchema(schema, table_name, partitionBy, db_name='tmp_work', spark=None, mode='overwrite'):
    """
    描述：依据schema创建表

    参数：
    :param schema:
    :param table_name:
    :param partitionBy[list]: ['biz_code', 'load_date']
    :param db_name:
    :param spark:
    :param mode:

    示例：
    >>> schema = StructType([
    >>>     StructField('uuid', StringType(), False),
    >>>     StructField('biz_code', StringType(), False),
    >>>     StructField('index_val', StringType(), True),
    >>>     StructField('load_date', StringType(), False),
    >>> ])
    """
    df = spark.createDataFrame(spark.sparkContext.emptyRDD(), schema=schema)
    df.write.mode(mode).partitionBy(partitionBy).saveAsTable(f'{db_name}.{table_name}')

def convert_col_to_list(df, col):
    """
    desc: convert pyspark DataFrame to list.

    :param df: spark dataframe.
    :param col: column name.
    :return: column value list.
    """
    return df.select(col).rdd.map(lambda x: x[0]).collect()


def KillApp(app_id):
    """
    描述：kill spark application

    :param app_id: spark app id
    :return:
    """
    info = os.popen(f'yarn application --kill {app_id}').readlines()
    print('\n'.join(info))


def HiveTableToCSV(csv_path, db_name=None, table_name=None, query=None):
    """
    描述：提取Hive Table至CSV文件

    参数：
    :param db_name: 数据库名
    :param table_name: 表名
    :param csv_path: CSV路径
    :param query: 需要导出的 SQL Query

    示例：
    >>> query = 'SELECT * FROM tmp_work.t_cch_sample_for_yto'
    >>> csv_path = './dataset/samples.csv'
    >>> HiveTableToCSV(csv_path=csv_path, query=None)
    >>> HiveTableToCSV(db_name='tmp_work', table_name='t_cch_sample_for_yto', csv_path=csv_path)
    """
    mkdir(csv_path)
    if query:
        shell = f"hive -e 'set hive.cli.print.header=true; {query}' > '{csv_path}'"
    else:
        shell = f"hive -e 'set hive.cli.print.header=true; SELECT * FROM {db_name}.{table_name}' > '{csv_path}'"
    info = os.popen(shell).readlines()
    print('\n'.join(info))


def get_db_table(db_name, spark=None):
    """
    desc: get database table info.
    :param db_name: database name
    :param spark: spark session
    :return: pd.DataFrame, table info.
    """
    tables = spark.catalog.listTables(db_name)
    list_table = []
    for table in tables:
        table_info = {
            'name': table.name,
            'database': table.database,
            'description': table.description,
            'tableType': table.tableType,
            'isTemporary': table.isTemporary,
        }
        list_table.append(table_info)
    df_tables = pd.DataFrame(list_table)
    return df_tables


def get_part_info(db_name, table_name, spark):
    """

    :param db_name:
    :param table_name:
    :param spark:
    :return:
    """
    df_part = ShowTablePartitions(f'{db_name}.{table_name}',spark=spark)
    if len(df_part) == 0:
        return []
    else:
        return list(zip(df_part.load_date, df_part.index_name))

