import pandas as pd
from pandas import DataFrame, Series
from typing import Any, List, Union, Optional
from kivi.woe.base import WOEMixin


__all__ = ["DistanceBins"]


class DistanceBins(WOEMixin):
    """等距分箱分析"""
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
        """等距分箱分析。
        Notes:
            ```python
            from kivi.woe import *
            from kivi.datasets import *
            df_bank = Dataset.bank_data()

            bins = DistanceBins(df_bank.age, df_bank.target, bins=5)
            df_woe = bins.fit(score=True, origin_border=False)
            print(df_woe.to_markdown())
            ```

        Args:
            variables: 待分箱变量
            target: 目标标签变量
            bins: 决策树分箱中最大的叶子结点数量，一般对应的是最终分箱数量，默认为 5 。
            abnormal_vals: 特殊值分箱，在变量存在特殊值时单独分一箱，如 -1111, -9999。
            fill_bin: 在各分箱中偶发性会出现 good 或 bad 为 0 的情况，默认 fill_pos 为 True ，为该分箱填充 0.5。
            decimal: 分箱后，WOE 和 IV 的保留小数位数，默认为 6 位。
            weight: 样本权重变量，用于计算 WOE，默认为 None。
            *args:
            **kwargs:

        Example:
            woe = Distance(variables, target, bins=5, fill_bin=True)
            woe.fit()
        """
        self.variables = variables
        self.target = target
        self.bins = bins
        self.max_leaf_nodes = bins
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
        :param score: 是否增加 WOEMixin score。
        :param origin_border: 是否增加 分箱中的最大值与最小值。
        :param order: 是否增加单调性判断。
        :return: DataFrame WOEMixin result.
        """
        _bucket = pd.cut(self.df_data.variables, self.bins, include_lowest=True, duplicates='drop')
        bucket = pd.DataFrame({
            'variables': self.df_data.variables,
            'target': self.df_data.target,
            'bucket': _bucket,
        }).groupby('bucket', as_index=True, observed=False)
        self.cal_woe_iv(bucket, score=score, origin_border=origin_border, order=order)
        return self.woe

