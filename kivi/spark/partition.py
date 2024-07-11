import pandas as pd
from typing import List, Tuple, Optional
from pyspark.sql import SparkSession
from pandas import DataFrame as TypePandasDataFrame

__all__ = [
    "show_table_partition",
    "get_index_partition",
    "drop_partition_data",
]


def show_table_partition(
        db_name: Optional[str] = None,
        table_name: Optional[str] = None,
        spark: Optional[SparkSession] = None,
) -> TypePandasDataFrame:
    """
    描述：展示表的分区信息
    Example:
        df_part = ShowTablePartitions(table_name='tmp_work.t_cch_sample_long', spark=spark)
    """
    if db_name and table_name:
        table_name = f'{db_name}.{table_name}'

    def parse_partition_value(row_value):
        row = dict()
        for item in row_value:
            key, value = item.split('=')
            row.update({key: value})
        return row
    df_part = spark.sql(f"SHOW PARTITIONS {table_name}").toPandas()
    part = df_part.partition.str.split('/').tolist()
    return pd.DataFrame(list(map(parse_partition_value, part)))


def get_index_partition(
        db_name: str,
        table_name: str,
        spark: SparkSession
) -> List[Tuple[str, str]]:
    """

    :param db_name:
    :param table_name:
    :param spark:
    :return:
    """
    df_part = show_table_partition(db_name, table_name, spark=spark)
    if len(df_part) == 0:
        return []
    else:
        return list(zip(df_part.load_date, df_part.index_name))


def drop_partition_data(db_name: str, table_name: str, partition: str, spark: SparkSession) -> None:
    """
    描述：删除分区 示例：
    """
    query = f"""
        alter table {db_name}.{table_name} drop if exists partition (partition)
        """
    spark.sql(query)
    print(f'Table {db_name}.{table_name} partition: {partition} has been dropped.')
