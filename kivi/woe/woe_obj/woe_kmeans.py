import numpy as np
import pandas as pd
try:
    from sklearn.cluster import KMeans
except ImportError:
    raise ImportError("Please install scikit-learn to use this module. pip install scikit-learn")
from pandas import DataFrame, Series
from typing import Any, List, Union, Optional
from kivi.woe.base import WOEMixin


__all__ = ['KmeansBins']


class KmeansBins(WOEMixin):
    """ 描述：Kmeans 分箱方法，使用 Kmeans 进行分箱分析。 """
    cutoff_points: List[float]

    def __init__(
            self,
            variables: Series,
            target: Series,
            bins: Optional[int] = 5,
            n_init: Optional[int] = 10,
            random_state: Optional[int] = 0,
            abnormal_vals: Optional[List[Union[str, int, float]]] = None,
            fill_bin: Optional[bool] = True,
            decimal: Optional[int] = 6,
            weight: Optional[Any] = None,
            *args: Any,
            **kwargs: Any,
    ):
        """
        描述：[无监督分箱] Kmeans 分箱方法，使用 Kmeans 进行分箱分析。

        :param variables: 待分箱变量
        :param target: 目标标签变量
        :param bins: 决策树分箱中最大的叶子结点数量，一般对应的是最终分箱数量，默认为 5 。
        :param abnormal_vals: 特殊值分箱，在变量存在特殊值时单独分一箱，如 -1111, -9999。
        :param fill_bin: 在各分箱中偶发性会出现 good 或 bad 为 0 的情况，默认 fill_pos 为 True ，为该分箱填充 0.5。

        Example:
            woe = KmeansBins(variables, target, bins=5, fill_bin=True)
            woe.fit()
        """
        self.variables = variables
        self.target = target
        self.bins = bins
        self.n_init = n_init
        self.random_state = random_state
        self.fill_bin = fill_bin
        self.abnormal_vals = abnormal_vals
        self.decimal = decimal
        self.args = args
        self.kwargs = kwargs
        self.data_prepare(
            variables=variables, target=target, weight=weight)

    def kmeans_cutoff_point(self,):
        """"""
        vars = self.variables.to_numpy().reshape(-1, 1)
        kmeans = KMeans(n_init=self.n_init, n_clusters=self.bins, random_state=self.random_state).fit(vars)
        df_var_label = pd.DataFrame({
            'label': kmeans.fit_predict(vars).flatten(),
            'vars': self.variables
        })
        bins = sorted(df_var_label.groupby('label').max().vars.tolist())[:-1]
        bins += [np.inf, -np.inf]
        bins.sort()
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
        self.kmeans_cutoff_point()
        _bucket, _bins = pd.cut(
            self.df_data.variables, self.cutoff_point, include_lowest=True, retbins=True)
        bucket = pd.DataFrame({
            'variables': self.df_data.variables,
            'target': self.df_data.target,
            'bucket': _bucket,
        }).groupby('bucket', as_index=True, observed=False)
        self.cal_woe_iv(bucket, score=score, origin_border=origin_border, order=order)
        return self.woe

