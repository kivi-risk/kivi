import os, re
import logging
try:
    from pyspark.sql import SparkSession
    from pyspark.sql import functions as F
    from pyspark.sql.types import StructType, StructField, StringType
    from pyspark.sql.window import Window
    from pyspark.sql import DataFrame as TypeSparkDataFrame
except ImportError:
    print("pyspark not installed, please install it first. < pip install pyspark >")
from typing import List, Optional
from tqdm import tqdm
import pandas as pd
from pandas import DataFrame as TypePandasDataFrame
from ..utils.utils import mkdir
from .column import get_table_columns

__all__ = [
    "drop_table",
    "rename_table",
    "find_tables",
    "table_exit",
    "create_table_by_schema",
    "spark_frame_to_hive",
    "insert_into_hive",
    "get_db_table",
    "hive_table_to_csv",
    "save_pandas_frame_to_hive",
]


def drop_table(db_name: str, table_name: str, spark: SparkSession) -> None:
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


def rename_table(
        pre_db_name: str,
        pre_table_name: str,
        db_name: str,
        table_name: str,
        spark: SparkSession
) -> None:
    print(f'Pre table {pre_db_name}.{pre_table_name}')
    if db_name is None:
        db_name = pre_db_name
    if table_name:
        spark.sql(f'ALTER TABLE {pre_db_name}.{pre_table_name} RENAME TO {db_name}.{table_name}')
    print(f'Rename to {db_name}.{table_name}')


def find_tables(
        db_name: str,
        tables: str,
        pat: str,
        spark: SparkSession
) -> List[str]:
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


def table_exit(db_name: str, table_name: str, spark: SparkSession) -> bool:
    """"""
    if spark.catalog._jcatalog.tableExists(f'{db_name}.{table_name}'):
        return True
    else:
        return False


def create_table_by_schema(
        schema: StructType,
        db_name: str,
        table_name: str,
        partition_by: str,
        spark: SparkSession,
        mode='overwrite'
) -> None:
    """
    描述：依据schema创建表

    Example:
        schema = StructType([
            StructField('uuid', StringType(), False),
            StructField('biz_code', StringType(), False),
            StructField('index_val', StringType(), True),
            StructField('load_date', StringType(), False),
        ])
    """
    df = spark.createDataFrame(spark.sparkContext.emptyRDD(), schema=schema)
    df.write.mode(mode).partitionBy(partition_by).saveAsTable(f'{db_name}.{table_name}')


def spark_frame_to_hive(
        df: TypeSparkDataFrame,
        db_name: str,
        table_name: str,
        spark: SparkSession,
        comment: Optional[str] = None,
        partition_by: Optional[str] = None,
        mode: str = 'overwrite',
        repartition: Optional[int] = None,
        verbose: Optional[bool] = True,
) -> None:
    """
    原来的 FrameToHive
    保存表格到数据库
    """
    if verbose: logging.warning(f'Save DataFrame To {db_name}.{table_name}!')

    if partition_by:
        df.write.mode(mode).partitionBy(partition_by).saveAsTable(f'{db_name}.{table_name}')
    elif repartition:
        df.repartition(repartition).write.mode(mode).saveAsTable(f'{db_name}.{table_name}')
    elif spark:
        drop_table(db_name, table_name, spark)
        df.createOrReplaceTempView(f'{table_name}')
        spark.sql(f'create table {db_name}.{table_name} as select * from {table_name}')
        if comment is not None:
            spark.sql(f"ALTER TABLE {db_name}.{table_name} SET TBLPROPERTIES('comment'='{comment}')")
    else:
        raise Exception(f'table {db_name}.{table_name} save failed!')

    if verbose: logging.warning(f'Save End!')


def insert_into_hive(
        df: TypeSparkDataFrame,
        db_name: str,
        table_name: str,
        partition: List[str],
        partition_val: List[str],
        spark: SparkSession ,
        query_mode: Optional[bool] = True
) -> None:
    """
    描述：向Hive表中插入数据

    Example:
        InsertIntoHive(
            df_2, 'tmp_work', 't_cch_uuid_info',
            partition=['biz_code', 'load_date'],
            partition_val=['industry', '20190101'], spark=spark)
    """
    if query_mode:

        part_conditions = []
        for part, part_val in zip(partition, partition_val):
            part_conditions.append(f"{part}='{part_val}'")
        if len(part_conditions) == 1:
            part_condition = str(f'{part_conditions[0]}')
        else:
            part_condition = str(', '.join(part_conditions))

        columns = get_table_columns(db_name=db_name, table_name=table_name, spark=spark)
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


def get_db_table(db_name: str, spark: SparkSession) -> TypePandasDataFrame:
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


def hive_table_to_csv(csv_path: str, db_name: str = None, table_name: str = None, query: str = None):
    """
    描述：提取Hive Table至CSV文件

    参数：
    :param db_name: 数据库名
    :param table_name: 表名
    :param csv_path: CSV路径
    :param query: 需要导出的 SQL Query

    Example:
        query = 'SELECT * FROM tmp_work.t_cch_sample_for_yto'
        csv_path = './dataset/samples.csv'
        HiveTableToCSV(csv_path=csv_path, query=None)
        HiveTableToCSV(db_name='tmp_work', table_name='t_cch_sample_for_yto', csv_path=csv_path)
    """
    mkdir(csv_path)
    if query:
        shell = f"hive -e 'set hive.cli.print.header=true; {query}' > '{csv_path}'"
    else:
        shell = f"hive -e 'set hive.cli.print.header=true; SELECT * FROM {db_name}.{table_name}' > '{csv_path}'"
    info = os.popen(shell).readlines()
    print('\n'.join(info))


def save_pandas_frame_to_hive(
        df: TypePandasDataFrame,
        db_name: str,
        table_name: str,
        reset: Optional[bool] = True,
        spark: Optional[SparkSession] = None,
        batch: Optional[int] = 5e4,
        verbose: Optional[bool] = False
) -> None:
    """
    描述：将模型结果保存至Hive表中，以5万为默认保存批次
    Example:
        SaveBigDFToHive(df_now_woe, 'tmp_work', 't_cch_sample_woe_20210531', spark)
    """
    table_exist = table_exit(db_name=db_name, table_name=table_name, spark=spark)

    if reset and table_exist:
        drop_table(db_name, table_name, spark)

    for i in tqdm(range(int(len(df) // batch) + 1)):
        low = int(i * batch)
        up = int((i + 1) * batch)
        df_part = spark.createDataFrame(df.iloc[low: up, :])

        if verbose:
            print(f'[{low}, {up}]')

        if i == 0 and reset:
            mode = 'overwrite'
        else:
            mode = 'append'

        spark_frame_to_hive(
            df_part, db_name=db_name, table_name=table_name, spark=spark, repartition=4,
            mode=mode, verbose=verbose)
        df_part.unpersist()


