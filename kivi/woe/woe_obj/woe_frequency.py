import pandas as pd
from pandas import DataFrame, Series
from typing import Any, List, Union, Optional
from kivi.woe.base import WOEMixin


__all__ = ["FrequencyBins"]


class FrequencyBins(WOEMixin):
    """"""
    def __init__(
            self,
            variables: Series,
            target: Series,
            bins: Optional[int] = 5,
            abnormal_vals: Optional[List[Union[str, int, float]]] = None,
            fill_bin: Optional[bool] = True,
            decimal: Optional[int] = 6,
            weight: Optional[Any] = None,
            *args: Any,
            **kwargs: Any,
    ):
        """等频分箱分析

        Args:
            variables: 待分箱变量。
            target: 目标标签变量。
            bins: 决策树分箱中最大的叶子结点数量，一般对应的是最终分箱数量，默认为 5 。
            abnormal_vals: 特殊值分箱，在变量存在特殊值时单独分一箱，如 -1111, -9999。
            fill_bin: 在各分箱中偶发性会出现 good 或 bad 为 0 的情况，默认 fill_pos 为 True ，为该分箱填充 0.5。
            decimal: 小数点后保留位数，默认为 6 位。
            weight: 样本权重。
            *args:
            **kwargs:

        Example:
            ```python
            bins = FrequencyBins(df_bank.age, df_bank.target, bins=5)
            df_woe = bins.fit()
            print(df_woe.to_markdown())
            ```
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

    def fit(
            self,
            score: Optional[bool] = True,
            origin_border: Optional[bool] = False,
            order: Optional[bool] = True,
            **kwargs: Any,
    ) -> DataFrame:
        """
        计算WOE值和IV值。

        Args:
            score: 是否增加 WOEMixin score。
            origin_border: 是否增加 分箱中的最大值与最小值。
            order: 是否增加单调性判断。
            **kwargs:

        Returns:
            DataFrame: 包含WOE值和IV值的DataFrame。
        """
        _bucket = pd.qcut(self.df_data.variables, self.bins, duplicates='drop')
        bucket = pd.DataFrame({
            'variables': self.df_data.variables,
            'target': self.df_data.target,
            'bucket': _bucket,
        }).groupby('bucket', as_index=True, observed=False)
        self.cal_woe_iv(bucket, score=score, origin_border=origin_border, order=order)
        return self.woe
