try:
    from pyspark.sql.window import Window
    from pyspark.sql import functions as F
    from pyspark.sql.types import StringType, DoubleType
    from pyspark.sql import DataFrame as TypeSparkDataFrame
except ImportError:
    print("pyspark not installed, please install it first. < pip install pyspark >")
from typing import List, Optional
from pandas import DataFrame as TypePandasDataFrame
from hashlib import md5


__all__ = [
    "operator_mapping",
    "pct_rank",
]


operator_mapping = {
    'cnt': F.count,
    'avg': F.avg,
    'sum': F.sum,
    'cnt_dist': F.countDistinct,
    'sum_dist': F.sumDistinct,
    "min": F.min,
    "max": F.max,
    "mean": F.mean,
    "first": F.first,
    "last": F.last,
    "skewness": F.skewness,
    "kurtosis": F.kurtosis,
    "collect_set": F.collect_set,
    "collect_list": F.collect_list,
    "approx_count_distinct": F.approx_count_distinct,
    'stddev': F.stddev,
    'stddev_samp': F.stddev_samp,
    'stddev_pop': F.stddev_pop,
    'variance': F.variance,
    'var_pop': F.var_pop,
    'var_samp': F.var_samp,
}


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


@F.udf(returnType=DoubleType())
def udf_operator_div(num, den):
    """
    描述：用于 spark 中做除法，并区分分子分母状态，计算逻辑如下：

    分母\分子	   null	    0	   正值或负值
    null	  -4404	   -4404	-9999
    0	      -4404	   -4404	-9999
    正值或负值  -1111	    0	    正常计算

    参数：
    :param num: 分子名
    :param den: 分母名称

    Example:
    >>> data = [(None, 1), (1, 1), (None, None), (0, 0), (0, 1), (0, None), (1, None), (1, 0)]
    >>> df = spark.createDataFrame(data, schema=['num', 'den'])
    >>> df = df.withColumn('div', udf_operator_div(F.col('num'), F.col('den')))
    >>> df.show()
    +----+----+-------+
    | num| den|    div|
    +----+----+-------+
    |null|   1|-1111.0|
    |   1|   1|    1.0|
    |null|null|-4404.0|
    |   0|   0|-4404.0|
    |   0|   1|    0.0|
    |   0|null|-4404.0|
    |   1|null|-9999.0|
    |   1|   0|-9999.0|
    +----+----+-------+
    """
    if ((num is None) or (num == 0)) and ((den is None) or (den == 0)):
        return -4404.
    elif ((den is None) or (den == 0)):
        return -9999.
    elif num is None:
        return -1111.
    else:
        return num / den


def operator_div(num, den):
    """
    描述：用于 spark 中做除法，并区分分子分母状态，计算逻辑如下：

    分母\分子	   null	    0	   正值或负值
    null	  -4404	   -4404	-9999
    0	      -4404	   -4404	-9999
    正值或负值  -1111	    0	    正常计算

    参数：
    :param num: 分子名
    :param den: 分母名称

    示例：
    >>> data = [(None, 1), (1, 1), (None, None), (0, 0), (0, 1), (0, None), (1, None), (1, 0)]
    >>> df = spark.createDataFrame(data, schema=['num', 'den'])
    >>> df = df.withColumn('div', operator_div('num', 'den'))
    >>> df.show()
    +----+----+-------+
    | num| den|    div|
    +----+----+-------+
    |null|   1|-1111.0|
    |   1|   1|    1.0|
    |null|null|-4404.0|
    |   0|   0|-4404.0|
    |   0|   1|    0.0|
    |   0|null|-4404.0|
    |   1|null|-9999.0|
    |   1|   0|-9999.0|
    +----+----+-------+
    """
    cond_a = (((F.col(num).isNull()) | (F.col(num) == 0)) & ((F.col(den).isNull()) | (F.col(den) == 0)))
    cond_b = ((F.col(den).isNull()) | (F.col(den) == 0))
    cond_c = F.col(num).isNull()
    return F.when(cond_a, -4404).when(cond_b, -9999).when(cond_c, -1111).otherwise(F.col(num) / F.col(den))



@F.udf(returnType=StringType())
def MD5(x):
    """MD5生成器"""
    return md5(str(x).encode("utf8")).hexdigest()


# @F.udf(returnType=StringType())
def get_boundary(base_value, e=1):
    """
    描述：数值的区间脱敏，将数据转化为区间。

    参数：
    :param base_value: 区间脱敏
    :param e: 脱敏幂次

    示例：
    >>> df_sample = df_sample.withColumn('income', get_boundary(1000)(df_sample.income))
    1000为最低区分区间。
    """

    def f(value):
        try:
            value = float(value)
        except:
            return None

        if 'inf' in str(value):
            return str(value)

        # 正负值掩码
        mask = 1 if value >= 0 else -1

        # base_value 以内不进行分段区分
        value = value * mask
        if value < base_value and mask > 0:
            return f'[0, {base_value})'
        if value < base_value and mask < 0:
            return f'[-{base_value}, 0)'

        p = len(str(int(value))) - e

        low = int(value / float(f'1e{p}'))
        if mask >= 0:
            res = '[{}, {})'.format(str(int(mask * float(f'{low}e{p}'))), str(int(mask * float(f'{low + 1}e{p}'))))
        else:
            if value == float(f'{low}e{p}'):
                res = '[{1}, {0})'.format(str(int(mask * float(f'{low - 1}e{p}'))),
                                          str(int(mask * float(f'{low}e{p}'))))
            else:
                res = '[{1}, {0})'.format(str(int(mask * float(f'{low}e{p}'))),
                                          str(int(mask * float(f'{low + 1}e{p}'))))
        return res

    udf_fun = F.udf(f, returnType=StringType())
    return udf_fun
