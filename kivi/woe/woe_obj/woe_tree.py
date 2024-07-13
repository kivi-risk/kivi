try:
    from sklearn.tree import DecisionTreeClassifier
except ImportError:
    raise ImportError("Please install scikit-learn to use this module. pip install scikit-learn")
import pandas as pd
from pandas import Series, DataFrame
from typing import Any, List, Union, Optional
from kivi.woe.base import WOEMixin


__all__ = ['TreeBins']


class TreeBins(WOEMixin):
    """决策树分箱"""
    cutoff_point: List[float]

    def __init__(
            self,
            variables: Series,
            target: Series,
            bins: Optional[int] = 5,
            fill_bin: Optional[bool] = True,
            var_name: Optional[str] = None,
            abnormal_vals: Optional[List[Union[str, int, float]]] = None,
            weight: Optional[Any] = None,
            dtc_weight: Optional[Any] = None,
            decimal: Optional[int] = 6,
            *args: Any,
            **kwargs: Any,
    ):
        """
        描述：决策树分箱方法，使用决策树最优 entropy 进行分箱分析。

        :param variables: 待分箱变量
        :param target: 目标标签变量
        :param bins: 决策树分箱中最大的叶子结点数量，一般对应的是最终分箱数量，默认为 5 。
        :param abnormal_values: 特殊值分箱，在变量存在特殊值时单独分一箱，如 -1111, -9999。
        :param fill_bin: 在各分箱中偶发性会出现 good 或 bad 为 0 的情况，默认 fill_pos 为 True ，为该分箱填充 0.5。

        Example:
            woe = TreeBins(variables, target, bins=5, fill_bin=True)
            woe.fit()
        """
        self.variables = variables
        self.target = target
        self.bins = bins
        self.max_leaf_nodes = bins
        self.fill_bin = fill_bin
        self.abnormal_vals = abnormal_vals
        self.dtc_weight = dtc_weight
        self.decimal = decimal
        self.args = args
        self.kwargs = kwargs
        self.data_prepare(
            variables=variables, target=target,
            weight=weight, var_name=var_name)

    def tree_cutoff_point(self, ):
        """ """
        clf = DecisionTreeClassifier(
            criterion='entropy', max_leaf_nodes=self.max_leaf_nodes, min_samples_leaf=0.05)
        clf.fit(self.variables.to_numpy().reshape(-1, 1), self.target.to_numpy().reshape(-1, 1), sample_weight=self.dtc_weight)
        n_nodes = clf.tree_.node_count
        left, right = clf.tree_.children_left, clf.tree_.children_right
        threshold = clf.tree_.threshold
        self.cutoff_point = sorted([-float('inf')] + [threshold[i] for i in range(n_nodes) if left[i] != right[i]] + [float('inf')])

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
        self.tree_cutoff_point()
        _bucket, _bins = pd.cut(self.df_data.variables, self.cutoff_point, include_lowest=True, retbins=True)
        if self.weight is None:
            bucket = pd.DataFrame({
                'variables': self.df_data.variables,
                'target': self.df_data.target,
                'bucket': _bucket,
            }).groupby('bucket', as_index=True, observed=False)
        else:
            bucket = self.get_weighted_buckets(
                value_cut=_bucket, variables=self.df_data.variables, target=self.df_data.target, weight=self.df_data.weight)
        self.cal_woe_iv(bucket, score=score, origin_border=origin_border, order=order)
        return self.woe
