import statsmodels.api as sm
from pyspark.sql.types import *
from pyspark.sql import functions as F

__all__ = [
    'operator_mapping',
    'StatsLogit',
    'NumRange',
    'mode',
    'Div',
    'operator_div',
    'udf_operator_div',
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

def StatsLogit(X, y, intercept=True):
    """
    描述： statsmodels 逻辑回归
    :param X:
    :param y:
    :param intercept:
    :return:
    """
    if intercept:
        X = sm.add_constant(X, has_constant='add')
    model = sm.Logit(y, X).fit(disp=False)
    return model

def NumRange(a, b, X_min, X_max, X):
    """
    描述：将数值转换为任意值域
    :param a: 期望最小值
    :param b: 期望最大值
    :param X_min: 数据最小值
    :param X_max: 数据最大值
    :param X: 数据
    :return:
    """
    return a + ((b - a) / (X_max - X_min)) * (X - X_min)

def mode(series):
    """
    描述：
    :param series:
    :return:
    """
    try:
        return float(series.mode())
    except:
        return -9999.

class Div:
    @staticmethod
    def divSpark(df, div_name, a, b, else_value=-9999.):
        """
        描述：Spark 计算 Div 指标
        :param df:
        :param div_name:
        :param a:
        :param b:
        :param else_value:
        :return:
        """
        df = df.withColumn(div_name, F.when(F.col(b) != 0., F.col(a) / F.col(b)).otherwise(else_value))
        return df

    @staticmethod
    def divPandas(df, div_name, a, b, else_value=-9999.):
        """
        描述：Pandas 计算 Div 指标
        :param df:
        :param div_name:
        :param a:
        :param b:
        :param else_value:
        :return:
        """
        df[div_name] = df[a] / df[b].replace(0, 1e-6)
        return df

    @staticmethod
    def div(a, b, else_value=-9999.):
        if b != 0:
            return a / b
        else:
            return else_value

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

    示例：
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

