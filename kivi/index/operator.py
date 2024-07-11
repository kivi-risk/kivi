from typing import Callable, Union, Optional
import pandas as pd
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType


__all__ = [
    "merge_index_name",
    "operator_mapping",
    "operator_growth_months",
    "operator_consecutive_growth_months",
    "operator_pandas_udf_group_sum_ratio",
]


def merge_index_name(
        id_level: str,
        index_name: str,
        operate_name: str,
        month: Union[str, int],
        alias_operator: Optional[str] = None,
) -> str:
    """
    desc: 合并指标名称

    :param id_level: 聚合主键
    :param index_name: 指标名称
    :param operate_name: 聚合算子
    :param month: 月份
    :param alias_operator: 别名算子
    :return: 指标名称
    """
    if alias_operator:
        return '_'.join([id_level, index_name, alias_operator, f'{month}m'])
    else:
        return '_'.join([id_level, index_name, operate_name, f'{month}m'])


def operator_ratio(num, den):
    """"""
    if num is None and den is None:
        return -4404.
    elif num is None:
        return -1111.
    elif den is None or den == 0.:
        return -9999.
    else:
        return num / den


def operator_growth_months(data):
    """"""
    consecutive_months = 0
    for i in range(1, len(data)):
        if data[i] > data[i - 1]:
            consecutive_months += 1
    return consecutive_months


def operator_consecutive_growth_months(data):
    """"""
    max_growth = 0
    current_growth = 0
    for pre, aft, in zip(data[:-1], data[1:]):
        if aft > pre:
            current_growth += 1
        else:
            current_growth = 0
        max_growth = max(max_growth, current_growth)
    return max_growth


def operator_pandas_udf_group_sum_ratio(num: pd.Series, den: pd.Series) -> float:
    """"""
    _num = num.sum()
    _den = den.sum()
    if _den == 0.:
        return -9999.
    else:
        return _num / _den


operator_mapping = {
    "sum": F.sum,
    "avg": F.avg,
    "mean": F.mean,
    "ratio": F.udf(f=operator_ratio, returnType=DoubleType()),
    "group_sum_ratio": F.pandas_udf(f=operator_pandas_udf_group_sum_ratio, returnType=DoubleType()),
}
index_schema_list = ['uuid', 'index_name', 'index_val', 'load_date']
