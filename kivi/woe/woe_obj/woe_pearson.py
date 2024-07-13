import numpy as np
import pandas as pd
from pandas import DataFrame, Series
from scipy.stats import spearmanr
from typing import Any, List, Union, Optional
from kivi.woe.base import WOEMixin


__all__ = [
    "PearsonBins"
]


class PearsonBins(WOEMixin):
    bins: Optional[List[Union[float, int]]]

    def __init__(
            self,
            variables: Series,
            target: Series,
            r: Optional[float] = 0.8,
            min_bin: Optional[int] = 3,
            max_bin: Optional[int] = 20,
            abnormal_vals: Optional[List[Union[str, int, float]]] = None,
            fill_bin: Optional[bool] = True,
            decimal: Optional[int] = 6,
            weight: Optional[Any] = None,
            *args: Any,
            **kwargs: Any,
    ):
        """
        描述：使用 Pearson 相关系数方法进行分箱分析。

        :param r: 相关系数阈值
        :param min_bin: 最小分箱数
        :param max_bin: 最大分箱数

        Example:
            woe = PearsonBins(r=1, min_bin=3, max_bin=20)
            woe.fit()
        """
        self.variables = variables
        self.target = target
        self.r = r
        self.min_bin = min_bin
        self.max_bin = max_bin
        self.fill_bin = fill_bin
        self.abnormal_vals = abnormal_vals
        self.decimal = decimal
        self.args = args
        self.kwargs = kwargs
        self.data_prepare(
            variables=variables, target=target, weight=weight)

    def pearson_bins(self):
        """"""
        n = self.max_bin
        r = 0
        while np.abs(r) < self.r and n >= self.min_bin:
            try:
                _bucket, self.bins = pd.qcut(self.df_data.variables, n, retbins=True, duplicates='drop')
                bucket_group = pd.DataFrame({
                    "variables": self.df_data.variables,
                    "target": self.df_data.target,
                    "bucket": _bucket,
                }).groupby('bucket', as_index=True, observed=False)
                r, p = spearmanr(bucket_group.mean().variables, bucket_group.mean().target)
            except Exception as e:
                self._logger(msg=f"[{__class__.__name__}] Error: {e}.", color="red")
            n -= 1
        self.bins[0] = -np.inf
        self.bins[-1] = np.inf

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
        self.pearson_bins()
        _bucket, _bins = pd.cut(
            self.df_data.variables, self.bins, include_lowest=True, retbins=True, duplicates='drop')
        bucket = pd.DataFrame({
            'variables': self.df_data.variables,
            'target': self.df_data.target,
            'bucket': _bucket,
        }).groupby('bucket', as_index=True, observed=False)
        self.cal_woe_iv(bucket, score=score, origin_border=origin_border, order=order)
        return self.woe
