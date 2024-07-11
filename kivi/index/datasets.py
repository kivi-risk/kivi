from pyspark.sql import SparkSession
from pyspark.sql.dataframe import DataFrame
from pyspark.sql import functions as F


__all__ = [
    "get_dwd_data",
    "get_operator_data",
]


def get_dwd_data(
        db_name: str,
        table_name: str,
        column: str,
        start_date: str,
        end_date: str,
        spark: SparkSession,
) -> DataFrame:
    """
    清洗层取数函数

    :param db_name: 数据库名称
    :param table_name: 表名
    :param column: 取数字段名称
    :param start_date: 开始时间 yyyyMMdd
    :param end_date: 结束时间 yyyyMMdd
    :param spark: 数据库连接
    :return: 取数结果
    """
    query = f"""
        SELECT uuid, {column}, load_date
        FROM {db_name}.{table_name}
        WHERE load_date BETWEEN '{start_date}' AND '{end_date}'
        """
    df = spark.sql(query)
    return df


def get_operator_data(
        df: DataFrame,
        column: str,
        start_date: str,
        end_date: str,
) -> DataFrame:
    """
    清洗层取数函数
    :param df: 原始数据
    :param column: 取数字段名称
    :param start_date: 开始时间 yyyyMMdd
    :param end_date: 结束时间 yyyyMMdd
    :return: 取数结果
    """
    df = df.where(F.col(start_date).between(start_date, end_date))
    return df.select("uuid", column, "load_date")
