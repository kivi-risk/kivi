try:
    from pyspark.sql import functions as F
    from pyspark.sql.types import StringType
    from pyspark.sql import DataFrame as TypeSparkDataFrame
except ImportError:
    print("pyspark not installed, please install it first. < pip install pyspark >")
from typing import Any, List, Dict


__all__ = [
    "convert_col_to_list",
    "map_label",
    "get_table_columns"
]


def convert_col_to_list(df: TypeSparkDataFrame, column: str) -> List[Any]:
    """
    desc: convert pyspark DataFrame to list.

    :param df: spark dataframe.
    :param col: column name.
    :return: column value list.
    """
    return df.select(column).rdd.map(lambda x: x[0]).collect()


def map_label(mapping: Dict):
    """
    描述：[UDF] 用来匹配 pyspark DataFrame 中的键值对

    示例：使用行业分类码值表，设置一列中文行业名称。
    >>> df.withColumn('industryCnName', mapLabel(industryDict)(df.industryCode))
    """
    def f(value):
        return mapping.get(value)
    return F.udf(f, returnType=StringType())


def get_table_columns(db_name: str, table_name: str, spark: TypeSparkDataFrame) -> List[str]:
    """
    描述：获取表的列名称
    示例：
    >>> getTableColumns('temp_work', 'test', spark)
    """
    columns_info = spark.catalog.listColumns(table_name, db_name)
    columns_name = [col.name for col in columns_info]
    return columns_name
