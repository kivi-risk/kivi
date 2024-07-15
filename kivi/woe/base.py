import numpy as np
import pandas as pd
from pandas import Series, DataFrame
from pandas.core.groupby.generic import DataFrameGroupBy
from typing import Any, List, Union, Optional, Sequence
from ..utils.logger import LoggerMixin
from .utils import *


__all__ = [
    "WOEMixin",
]


class WOEMixin(LoggerMixin):
    """
    woe Mixin
    todo: 增加 bins plot
    """
    df_data: DataFrame
    df_missing_data: DataFrame
    df_abnormal_data: DataFrame
    woe: DataFrame
    woe_normal: DataFrame
    woe_missing: DataFrame
    woe_abnormal: DataFrame
    woe_columns: Optional[List[str]]
    decimal: Optional[int] = 6

    def _init__(
            self,
            variables: Series,
            target: Series,
            var_name: Optional[str] = None,
            fill_bin: Optional[bool] = True,
            abnormal_vals: Optional[List[Union[str, int, float]]] = Any,
            weight: Optional[Any] = None,
            woe_columns: Optional[List[str]] = None,
            *args: Any,
            **kwargs: Any,
    ):
        """
        初始化
        :param variables: 待分箱变量
        :param target: 标签
        :param bins: 分箱数量
        :param var_name: 变量名称
        :param fill_bin: 是否在分箱中未包含 1 标签的情况下，全部 1 标签数量自增 1 默认为 False
        :param abnormal_vals: 特殊值分箱，在变量存在特殊值时单独分一箱，如 -1111, -9999。
        :param weight: 样本权重。
        """
        self.variables = variables
        self.target = target
        self.fill_bin = fill_bin
        self.abnormal_vals = abnormal_vals
        self.woe_columns = woe_columns
        self.args = args
        self.kwargs = kwargs

        self._get_var_name(var_name)
        self._validate_data_length(variables, target)

        self._basic_count(target, weight)
        self._data_prepare(variables, target, weight)

    def __call__(self, *args, **kwargs) -> DataFrame:
        """"""
        return self.fit()

    def fit(self) -> DataFrame:
        """"""
        return DataFrame()

    def _get_var_name(self, var_name: Optional[str] = None) -> None:
        """"""
        if hasattr(self.variables, 'name'):
            self.var_name = self.variables.name
        else:
            self.var_name = var_name

    def _validate_data_length(self, *args) -> None:
        """
        检查数据长度是否一致
        :param args: 待检查数据
        """
        length = [len(item) for item in args]
        if len(set(length)) == 1:
            pass
        else:
            raise ValueError('Variable and target must be the same length!')

    def _data_prepare(
            self,
            variables: Series,
            target: Series,
            weight: Optional[Any] = None
    ) -> None:
        """
        prepare data: 1. missing data; 2. abnormal data; 3. normal data
        """
        if weight is None:
            df = pd.DataFrame({"variables": variables, "target": target})
        else:
            df = pd.DataFrame({"variables": variables, "target": target, 'weight': weight})

        # drop infinite values
        if pd.api.types.is_number(df.variables):
            df = df[~np.isinf(df.variables)]

        if self.abnormal_vals:
            condition_abnormal = df.variables.isin(self.abnormal_vals)
            self.df_abnormal_data = df[condition_abnormal]
            self.df_missing_data = df[df.variables.isna() & ~condition_abnormal]
            self.df_data = df[df.variables.notna() & ~condition_abnormal]
        else:
            self.df_abnormal_data = pd.DataFrame()
            self.df_missing_data = df[df.variables.isna()]
            self.df_data = df[df.variables.notna()]

        if weight is not None:
            self.weight = self.df_data.weight
        else:
            self.weight = None

    def data_prepare(
            self,
            variables: Optional[Series],
            target: Optional[Series],
            weight: Optional[Series] = None,
            var_name: Optional[str] = None,
    ):
        """"""
        self._get_var_name(var_name)
        self._validate_data_length(variables, target)
        self._basic_count(target, weight)
        self._data_prepare(variables, target, weight)
        self.woe_columns = [
            'var_name', 'missing_rate', 'min_bin', 'max_bin', 'total',
            'bad', 'bad_rate', 'woe', 'iv', 'iv_value',
        ]

    def _basic_count(self, target: Optional[Series], weight: Optional[Series] = None):
        """ basic count """
        self.sample_length = len(target)

        if weight is None:
            self.total, self.bad = target.count(), target.sum()
            self.good = self.total - self.bad
        else:
            self.total = weight.sum()
            self.bad = weight[target == 1].sum()
            self.good = weight[target == 0].sum()

    def _bucket_stats(self, bucket: Optional[Series] = None) -> None:
        """ 基本结果表 """
        if len(bucket) > 0:
            self.woe_normal = pd.DataFrame({
                'min_bin': bucket.variables.min(),
                'max_bin': bucket.variables.max(),
                'bad': bucket.target.sum(),
                'good': bucket.target.count() - bucket.target.sum(),
                'total': bucket.target.count(),
            })
        else:
            self.woe_normal = pd.DataFrame()

        if len(self.df_missing_data) != 0:
            self.woe_missing = pd.DataFrame({
                'min_bin': [np.nan],
                'max_bin': [np.nan],
                "bad": self.df_missing_data.target.sum(),
                'good': self.df_missing_data.target.count() - self.df_missing_data.target.sum(),
                'total': self.df_missing_data.target.count(),
            })
        else:
            self.woe_missing = pd.DataFrame()

        if len(self.df_abnormal_data) != 0:
            self.woe_abnormal = self.df_abnormal_data.groupby(
                'variables').agg({'target': ['sum', 'count']})
            self.woe_abnormal.columns = ['bad', 'total']
            self.woe_abnormal['min_bin'] = self.woe_abnormal.index
            self.woe_abnormal['max_bin'] = self.woe_abnormal.index
            self.woe_abnormal['good'] = self.woe_abnormal.total - self.woe_abnormal.bad
            self.woe_abnormal = self.woe_abnormal[[
                'min_bin', 'max_bin', "bad", 'good', 'total',]]
            self.woe_abnormal.reset_index(inplace=True, drop=True)
        else:
            self.woe_abnormal = pd.DataFrame()

    def get_weighted_buckets(
            self,
            value_cut: Optional[Sequence] = None,
            df: Optional[DataFrame] = None,
            variables: Optional[Series] = None,
            target: Optional[Series] = None,
            weight: Optional[Series] = None,
    ):
        """获取加权分组"""
        if df is not None:
            variables = df.variables
            target = df.target
            weight = df.weight
        else:
            pass

        weight_good, weight_bad = weight.copy(), weight.copy()
        weight_good[target == 1], weight_bad[target == 0] = 0, 0

        if value_cut is not None:
            bucket = pd.DataFrame({
                'variables': variables,
                'target': target,
                'weight': weight,
                'weight_good': weight_good,
                'weight_bad': weight_bad,
                'bucket': value_cut,
            }).groupby('bucket', as_index=True, observed=False)
        else:
            bucket = pd.DataFrame({
                'variables': variables,
                'target': target,
                'weight': weight,
                'weight_good': weight_good,
                'weight_bad': weight_bad,
            }).groupby('variables', as_index=True, observed=False)
        return bucket

    def _weighted_buckets_stats(self, bucket):
        """weighted good or bad"""
        if len(bucket) > 0:
            self.woe_normal = pd.DataFrame({
                'min_bin': bucket.variables.min(),
                'max_bin': bucket.variables.max(),
                'bad': bucket.weight_bad.sum(),
                'good': bucket.weight_good.sum(),
                'total': bucket.weight.sum(),
            })
        else:
            self.woe_normal = pd.DataFrame()

        if len(self.df_missing_data) != 0:
            self.woe_missing = pd.DataFrame({
                'min_bin': [np.nan],
                'max_bin': [np.nan],
                "bad": self.df_missing_data.weight[self.df_missing_data.target == 1].sum(),
                'good': self.df_missing_data.weight[self.df_missing_data.target == 0].sum(),
                'total': self.df_missing_data.weight.sum(),
            })
        else:
            self.woe_missing = pd.DataFrame()

        if len(self.df_abnormal_data) != 0:
            abnormal_bucket = self.get_weighted_buckets(df=self.df_abnormal_data)
            self.woe_abnormal = pd.DataFrame({
                'min_bin': abnormal_bucket.target.min().index,
                'max_bin': abnormal_bucket.target.max().index,
                'bad': abnormal_bucket.weight_bad.sum(),
                'good': abnormal_bucket.weight_good.sum(),
                'total': abnormal_bucket.weight.sum(),
            })
        else:
            self.woe_abnormal = pd.DataFrame()

    def calculate_woe(
            self,
            woe: DataFrame,
            bucket_type: Optional[int] = 0,
            reset_boundary: Optional[bool] = False
    ) -> DataFrame:
        """
        依据结果表，计算woe
            如果存在 fill_bin==True, 则需要对分箱中未包含 1 标签的情况下，全部 1 标签数量自增 0.5
        """
        if woe.empty:
            return woe
        else:
            if self.fill_bin and (0 in woe.bad.tolist()):
                woe.bad = woe.bad + 0.5
            elif self.fill_bin and (0 in woe.good.tolist()):
                woe.good = woe.good + 0.5
            woe['bad_rate'] = woe['bad'] / woe['total']
            woe['bad_attr'] = woe['bad'] / self.bad
            woe['good_attr'] = woe['good'] / self.good
            woe['woe'] = np.log(woe['bad_attr'] / woe['good_attr'])
            woe['iv'] = (woe['bad_attr'] - woe['good_attr']) * woe['woe']
            woe = woe.sort_values(by='min_bin').reset_index(drop=True)

            if isinstance(bucket_type, int):
                woe["bucket_type"] = bucket_type
            if reset_boundary:
                woe = self._reset_woe_boundary(woe)
        return woe

    def _add_order(self, order: Optional[bool] = True) -> None:
        """"""
        if order and "order" not in self.woe_columns:
            self.woe_columns.append('order')
            self.woe['order'] = monotony(self.woe_normal.woe)

    def _add_score(self, score: Optional[bool] = True) -> None:
        """"""
        if score and "score" not in self.woe_columns:
            self.woe_columns.append('score')
            neg_woe = - self.woe.woe
            woe_score = (neg_woe - neg_woe.min()) * 100 / (neg_woe.max() - neg_woe.min())
            self.woe['score'] = list(map(int_score, woe_score))

    def _add_origin_border(self, origin_border: Optional[bool] = False) -> None:
        """"""
        if origin_border and "min_bin_val" not in self.woe_columns:
            self.woe_columns.extend(['min_bin_val', 'max_bin_val'])

    def _reset_woe_boundary(self, woe: DataFrame) -> DataFrame:
        """"""
        woe['min_bin_val'] = woe['min_bin']
        woe['max_bin_val'] = woe['max_bin']

        right = woe.max_bin.tolist()
        if isinstance(right[0], str):
            return woe
        elif isinstance(right[0], (float, int)):
            right[-1] = np.inf
            left = [-np.inf] + right[: -1]
            woe['min_bin'] = left
            woe['max_bin'] = right
            return woe
        else:
            raise ValueError("min_bin or max_bin is not str or float")

    def _merge_woe(self, *args: DataFrame) -> DataFrame:
        """"""
        woes = [woe for woe in args if not woe.empty]
        return pd.concat(woes, axis=0)

    def _value_decimal(self, woe: DataFrame) -> DataFrame:
        """"""
        decimal_columns = ["bad_rate", "woe", "iv", "iv_value"]
        for col in decimal_columns:
             woe[col] = woe[col].round(self.decimal)
        return woe

    def cal_woe_iv(
            self,
            bucket: Optional[Union[Series, DataFrameGroupBy]],
            score: Optional[bool] = True,
            origin_border: Optional[bool] = False,
            order: Optional[bool] = True
    ) -> None:
        """
        描述：计算 woe 结果。

        :param bucket:
        :param score: 是否增加 woe score。
        :param origin_border: 是否增加 分箱中的最大值与最小值。
        :param order: 是否按照 min_bin 排序。
        :return: DataFrame
        """
        if not hasattr(self, 'weight') or self.weight is None:
            self._bucket_stats(bucket=bucket)
        else:
            self._weighted_buckets_stats(bucket=bucket)

        self.woe_normal = self.calculate_woe(self.woe_normal, bucket_type=0, reset_boundary=True)
        self.woe_missing = self.calculate_woe(self.woe_missing, bucket_type=1)
        self.woe_abnormal = self.calculate_woe(self.woe_abnormal, bucket_type=2)

        self.woe = self._merge_woe(self.woe_normal, self.woe_abnormal, self.woe_missing)
        self.woe['iv_value'] = self.woe.iv[~np.isinf(self.woe.iv)].sum()
        self.woe['missing_rate'] = 1 - (self.woe_normal.total.sum() / self.sample_length)
        self.woe['var_name'] = self.var_name
        self.woe.reset_index(drop=True, inplace=True)

        self._add_order(order)
        self._add_score(score)
        self._add_origin_border(origin_border)
        self.woe = self._value_decimal(self.woe)
        self.woe = self.woe[self.woe_columns]
