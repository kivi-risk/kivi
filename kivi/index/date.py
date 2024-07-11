import calendar
from datetime import datetime
from typing import List, Tuple, Union
import pandas as pd
from pandas.tseries.offsets import MonthEnd


__all__ = [
    "get_month_last_day",
    "get_start_and_end_date",
    "get_start_and_end_date_periods",
]


def get_month_last_day(date: datetime) -> datetime:
    """"""
    year = date.year
    month = date.month
    _, last_day = calendar.monthrange(year, month)
    month_last_day = datetime(year, month, last_day)
    return month_last_day


def get_start_and_end_date(
        biz_date: str,
        month: Union[int, str],
) -> str:
    """
    desc: 时间回溯函数
    :param biz_date:
    :param month: 时间周期
    :return: 两个 list 指标开始时间，指标结束时间

    >>> get_start_and_end_date(biz_date='20191010', month=month)
    """
    if isinstance(month, str):
        return '20010131'
    else:
        biz_date = pd.to_datetime(biz_date)
        start_date = biz_date - pd.DateOffset(months=month - 1) + MonthEnd(0)
        return start_date.strftime("%Y%m%d")


def get_start_and_end_date_periods(
        start_date: str,
        end_date: str,
        months: int = 3,
        is_hist: bool = False,
) -> Tuple[List[str], List[str]]:
    """
    desc: 时间回溯函数
    :param is_hist: 是否索引历史全量数据
    :param start_date: 开始时间
    :param end_date: 结束时间，回溯月份
    :param months: 时间周期
    :return: 两个 list 指标开始时间，指标结束时间

    >>> start_dates, end_dates = get_start_and_end_date(start_date='20191010', end_date='20201010', months=3)
    >>> print(start_dates, "\\n", end_dates)
    """
    start_dates = pd.date_range(start=start_date, end=end_date, freq='M')
    if is_hist:
        start_dates = start_dates.astype(str).str.replace('-', '').tolist()
        return ['20101231']*len(start_dates), start_dates
    else:
        end_dates = start_dates - pd.DateOffset(months=months - 1) + MonthEnd(0)
        start_dates = start_dates.astype(str).str.replace('-', '').tolist()
        end_dates = end_dates.astype(str).str.replace('-', '').tolist()
        return end_dates, start_dates
