import numpy as np
import pandas as pd
from pandas import DataFrame, Series
from typing import Any, List, Union, Optional
from kivi.woe.base import WOEMixin


__all__ = ['KSBins']


class KSBins(WOEMixin):
    """
    描述：决策树分箱
    """
    cutoff_point: List[Union[float, int]]

    def __init__(
            self,
            variables: Series,
            target: Series,
            bins: Optional[int] = 5,
            abnormal_vals: Optional[List[Union[str, int, float]]] = None,
            fill_bin: Optional[bool] = True,
            decimal: Optional[int] = 6,
            weight: Optional[Any] = None,
            min_sample_rate: Optional[float] = 0.05,
            *args: Any,
            **kwargs: Any,
    ):
        """
        描述：最优KS分箱方法，使用决策树最优 entropy 进行分箱分析。

        :param variables: 待分箱变量
        :param target: 目标标签变量
        :param bins: 决策树分箱中最大的叶子结点数量，一般对应的是最终分箱数量，默认为 5 。
        :param abnormal_vals: 特殊值分箱，在变量存在特殊值时单独分一箱，如 -1111, -9999。
        :param fill_bin: 在各分箱中偶发性会出现 good 或 bad 为 0 的情况，默认 fill_pos 为 True ，为该分箱填充 0.5。

        Example:
            woe = KSBins(variables, target, bins=5, fill_bin=True)
            woe.fit()
        """
        self.variables = variables
        self.target = target
        self.bins = bins
        self.fill_bin = fill_bin
        self.abnormal_vals = abnormal_vals
        self.decimal = decimal
        self.args = args
        self.kwargs = kwargs
        self.data_prepare(
            variables=variables, target=target, weight=weight)
        if min_sample_rate is not None:
            self.min_sample = min_sample_rate * len(self.target)

    def max_ks_value(self, data):
        """
        """
        bad = data.target.sum()
        good = data.target.count() - bad

        data_cum = pd.crosstab(data.variables, data.target)\
            .div([good, bad]).cumsum()
        ks_list = (data_cum[1] - data_cum[0]).abs()
        ks_list_index = ks_list.nlargest(len(ks_list)).index.tolist()

        for i in ks_list_index:
            group_a = data.target[data.variables <= i].count()
            group_b = data.target[data.variables > i].count()
            if group_a >= self.min_sample and group_b >= self.min_sample:
                return i

    def get_cutoff_point(self, ):
        """"""
        bins = [-np.inf, np.inf]
        data_upgrade = self.df_data.copy()
        for i in range(self.bins - 1):
            bins.append(self.max_ks_value(data_upgrade))
            bins.sort()

            if len(bins) <= self.bins:
                # upgrade max sample bin
                df_buckets_stats = pd.cut(
                    self.df_data.variables, bins, include_lowest=True, duplicates='drop').value_counts(sort=True)
                max_bin = df_buckets_stats.idxmax()
                max_bin = [max_bin.left, max_bin.right]

                data_upgrade = self.df_data[self.df_data.variables.between(*max_bin, inclusive='right')].copy()
        self.cutoff_point = bins

    def fit(
            self,
            score: Optional[bool] = True,
            origin_border: Optional[bool] = False,
            order: Optional[bool] = True,
            **kwargs: Any,
    ) -> DataFrame:
        """

        :param score: 是否增加 WOEMixin score。
        :param origin_border: 是否增加 分箱中的最大值与最小值。
        :param order: 是否增加单调性判断。
        :return: DataFrame WOEMixin result.
        """
        self.get_cutoff_point()
        _bucket, _bins = pd.cut(self.df_data.variables, self.cutoff_point, include_lowest=True, retbins=True)
        bucket = pd.DataFrame({
            'variables': self.df_data.variables,
            'target': self.df_data.target,
            'bucket': _bucket,
        }).groupby('bucket', as_index=True, observed=False)
        self.cal_woe_iv(bucket, score=score, origin_border=origin_border, order=order)
        return self.woe
