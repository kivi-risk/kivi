import statsmodels.api as sm
from pyspark.sql.types import *
from pyspark.sql import functions as F


__all__ = [
    'StatsLogit',
    'NumRange',
    'mode',
    'Div',
]


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
