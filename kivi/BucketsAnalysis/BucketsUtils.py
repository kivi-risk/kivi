import numpy as np
import pandas as pd
from pyspark.sql import functions as F

__all__ = [
    "quantile",
    "getQuantiles",
    "psi",
    "csi",
]



def quantile(col: str, percent=0.5):
    """
    描述：分位数计算

    参数：
    :param col: 字段名称
    :param percent: 分位点
    :return : pyspark.sql.functions
    """
    return F.expr(f'percentile_approx({col}, {percent})')

def getQuantiles(df, column_name, ranges=np.linspace(0, 1, 11))->list:
    """
    描述：获取字段的分位数点。

    参数：
    :param df:
    :param column_name:
    :param ranges:
    :return : 分位数值 List

    示例：获取多个字段的多个分位点
    >>> quant_val_list = [getQuantiles(df, col) for col in cols]
    >>> pd.DataFrame(dict(zip(cols, quant_val_list)), index=np.linspace(0, 1, 11)).T
    """
    quantiles = [quantile(column_name, i).alias(f'i') for i in ranges]
    return df.agg(*quantiles).toPandas().values.flatten().tolist()


def psi(df_buckets, ex_name='Expected', ac_name='Actual', fill_bin=True):
    """

    :param df_buckets:
    :param ex_name:
    :param ac_name:
    :return:
    """
    if fill_bin:
        if 0 in df_buckets[ex_name].tolist():
            df_buckets[ex_name] += 0.5
        if 0 in df_buckets[ac_name].tolist():
            df_buckets[ac_name] += 0.5

    df_buckets['Expected_percentage'] = df_buckets[ex_name] / df_buckets[ex_name].sum()
    df_buckets['Actual_percentage'] = df_buckets[ac_name] / df_buckets[ac_name].sum()
    df_buckets['A-E'] = df_buckets.Actual_percentage - df_buckets.Expected_percentage
    df_buckets['A/E'] = df_buckets.Actual_percentage / df_buckets.Expected_percentage
    df_buckets['ln(A/E)'] = np.log(df_buckets['A/E'])
    df_buckets['psi_val'] = df_buckets['A-E'] * df_buckets['ln(A/E)']
    df_buckets['psi'] = df_buckets['psi_val'].sum()
    return df_buckets


def csi(df_buckets, ex_name='Expected', ac_name='Actual', fill_bin=True):
    """
    Des: 计算CSI的核心函数
    :param df_buckets: 明细表
    :return: 明细表以及CSI值 df_buckets, csi
    """

    df_buckets['Expected_percentage'] = df_buckets.Expected / df_buckets.Expected.sum()
    df_buckets['Actual_percentage'] = df_buckets.Actual / df_buckets.Actual.sum()
    df_buckets['A-E'] = df_buckets.Actual_percentage - df_buckets.Expected_percentage
    if len(df_buckets) != len(self.score):
        raise Exception(TypeError, 'Score len error!')
    df_buckets['score'] = self.score
    df_buckets['index'] = df_buckets['A-E'] * self.score
    df_buckets['csi'] = df_buckets['index'].sum()
    return df_buckets

