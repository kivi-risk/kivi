try:
    from pyspark.sql import SparkSession
    from pyspark.sql import functions as F
    from pyspark.sql.types import StructField, StringType
    from pyspark.sql.window import Window
    from pyspark.sql import DataFrame as TypeSparkDataFrame
except ImportError:
    print("pyspark not installed, please install it first. < pip install pyspark >")
from typing import Any, List, Optional
from tqdm import tqdm
import pandas as pd
from pandas import DataFrame as TypePandasDataFrame


__all__ = [
    "long_to_wide",
    "unpivot",
    "pandas_to_spark_frame",
    "spark_to_pandas_frame",
    "tqdm"
]


def long_to_wide(
        df_long: TypeSparkDataFrame,
        index: Optional[List[str]] = None,
        columns: Optional[str] = 'index_name',
        values: Optional[str] = 'index_val'
) -> TypeSparkDataFrame:
    """ 描述：对数据表进行 pivot 操作 """
    if index is None:
        index = ['uuid', 'load_date']
    df_wide = df_long.groupBy(index).pivot(columns).agg(
        F.first(values))
    return df_wide


def unpivot(
        df: TypeSparkDataFrame,
        columns: List[str],
        val_type: Optional[Any] = None,
        index_name='uuid',
        feature_name='name',
        feature_value='value',
        orderby=None
) -> TypeSparkDataFrame:
    """描述：对数据表进行反 pivot 操作"""
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


def pandas_to_spark_frame(df: TypePandasDataFrame, spark: SparkSession) -> TypeSparkDataFrame:
    """"""
    df = df.where(pd.notnull(df), None)
    return spark.createDataFrame(df)


def spark_to_pandas_frame(
        df: TypeSparkDataFrame,
        interval: Optional[int] = 5e4,
        index_name: Optional[str] = 'index',
        columns: Optional[List[str]] = None,
        drop_index: Optional[bool] = True,
) -> TypeSparkDataFrame:
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
    for i in tqdm(range(int(length / interval) + 1)):
        lower = i * interval
        upper = (i + 1) * interval
        df_pd = df_pd.append(df.where((df.index < upper) & (df.index >= lower)).toPandas())

    if drop_index:
        return df_pd.drop(index_name, axis=1)
    else:
        return df_pd

