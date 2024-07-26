try:
    from pyspark.sql.window import Window
    from pyspark.sql import functions as F
    from pyspark.sql.types import StringType, DoubleType
    from pyspark.sql import DataFrame as TypeSparkDataFrame
except ImportError:
    print("pyspark not installed, please install it first. < pip install pyspark >")
from typing import List, Optional
from pandas import DataFrame as TypePandasDataFrame


__all__ = [
    "pct_rank",
]


def pct_rank(
        df: TypePandasDataFrame,
        column_name,
        index_name: str = None,
        partition_by: Optional[List[str]] = None,
) -> TypePandasDataFrame:
    """
    描述：返回依据行业作为窗口的行业排名 DataFrame
    :param df: 原始数据
    :param column_name: 新指标名称
    :param index_name: 原指标名称
    :param partition_by: 窗口字段
    :return: spark DataFrame
    """
    if partition_by is None:
        partition_by = ['load_date', 'industry']

    if index_name is None:
        index_name = column_name
    # window of industry rank
    wind_indu = Window.partitionBy(*partition_by).orderBy(F.desc(column_name))
    df = df.withColumn(f'rank_indu_{index_name}', F.percent_rank().over(wind_indu))
    return df
