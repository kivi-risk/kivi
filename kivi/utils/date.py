from pyspark.sql import Column as TypeSparkColumn
import pandas as pd
import numpy as np
from pyspark.sql import functions as F
from pyspark.sql.types import StringType
from typing import List


__all__ = [
    "date_range",
    "month_shift",
    "to_date",
    "data_dates",
]


def date_range(start_date: str, end_date: str, freq: str = 'M') -> List[str]:
    """
    描述：时间周期

    :param start_date: 开始时间
    :param end_date: 结束时间
    :return:

    >>> dates = date_range('20191231', '20201231')
    """
    dates = pd.date_range(
        start=start_date, end=end_date, freq=freq
    ).astype(str).str.replace('-', '').tolist()
    return dates


def month_shift(col: str, n_month: int, fmt: str='yyyyMMdd') -> TypeSparkColumn:
    """
    描述：月份平移
    :param col:
    :param n_month:
    :param fmt:
    :return:
    """
    return F.date_format(F.add_months(F.to_date(col, fmt), n_month), fmt).cast(StringType())


def to_date(df, column, fmt: str='yyyyMMdd'):
    """"""
    df = df.withColumn(column, F.to_date(column, fmt))
    return df


def data_dates(obs_months=12, start_date='20191231', end_date='20210731', start_data_date='20190101'):
    """
    描述：计算样本批次，用于 UUID Info 长表与宽表的构建，用于样本的批量提取。

    参数：
    :param obs_months[Int]:          观察期（表现期）月份数
    :param start_date[String]:       建模样本开始时间，首批样本时间
    :param end_date[String]:         样本表现期最终批次时间点
    :param start_data_date[String]:  数据初始日期

    示例：
    >>> _data_dates, _sample_dates = data_dates(
    >>>     obs_months=2, start_date='20191031',
    >>>     end_date='20210731', start_data_date='20190101')
    """
    months = pd.date_range(start_data_date, end_date, freq='M').astype(str).str.replace('-', '').tolist()
    obs_date_index = months.index(start_date)
    credit_date_index = obs_date_index + obs_months

    data_dates = list(zip(months[: -(obs_months - 1)], months[(obs_months - 1):]))

    sample_dates = []
    while credit_date_index < len(months):
        sample_dates.append([months[obs_date_index], months[credit_date_index]])
        obs_date_index += 1
        credit_date_index += 1

    #### 剔除观察期不满足的记录
    data_start_date = np.array(sample_dates)[:, 0]
    mask = data_start_date >= months[obs_months - 1]
    sample_dates = np.array(sample_dates)[mask].tolist()
    return data_dates, sample_dates


