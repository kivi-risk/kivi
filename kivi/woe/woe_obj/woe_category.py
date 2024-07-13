import pandas as pd
from pandas import DataFrame, Series
from typing import Any, List, Union, Optional
from kivi.woe.base import WOEMixin


__all__ = ["CategoryBins"]


class CategoryBins(WOEMixin):
    """
    类别型变量的分箱
    """
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
        """
        描述：类别型变量分箱分析。

        :param variables: 待分箱变量
        :param target: 目标标签变量
        :param fill_bin: 在各分箱中偶发性会出现 good 或 bad 为 0 的情况，默认 fill_pos 为 True ，为该分箱填充 0.5。

        Example:
            woe = CategoryBins(variables, target)
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
        bucket = pd.DataFrame({
            'variables': self.df_data.variables,
            'target': self.df_data.target,
            'bucket': self.df_data.variables,
        }).groupby('bucket', as_index=True)

        self.cal_woe_iv(bucket, score=score, origin_border=origin_border, order=order)
        return self.woe
