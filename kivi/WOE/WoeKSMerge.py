import numpy as np
import pandas as pd
from .WOE import WOE, pd, np


__all__ = ['KSMerge']


class KSMerge(WOE):
    """
    描述：决策树分箱
    """
    def __init__(self, variables, target, bins=5, bin_limit=0.05, abnormal_vals=[], fill_bin=True):
        """
        描述：决策树分箱方法，使用决策树最优 entropy 进行分箱分析。

        :param variables: 待分箱变量
        :param target: 目标标签变量
        :param bins: 决策树分箱中最大的叶子结点数量，一般对应的是最终分箱数量，默认为 5 。
        :param abnormal_vals: 特殊值分箱，在变量存在特殊值时单独分一箱，如 -1111, -9999。
        :param fill_bin: 在各分箱中偶发性会出现 good 或 bad 为 0 的情况，默认 fill_pos 为 True ，为该分箱填充 0.5。

        示例：
        >>> woe = KSMerge(variables, target, bins=5, fill_bin=True)
        >>> woe.fit()
        """
        self.bins = bins
        self.data_init(variables, target, fill_bin=fill_bin, abnormal_vals=abnormal_vals)

        if bin_limit is not None:
            self.n_sample_limit = bin_limit * len(self.target)

    def GetMaxKSVal(self, data):
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
            if group_a >= self.n_sample_limit and group_b >= self.n_sample_limit:
                return i

    def GetCutoffpoint(self,):
        bins = [-np.inf, np.inf]

        data = pd.DataFrame({
            'variables': self.variables,
            'target': self.target,})

        data_upgrade = data.copy()
        for i in range(self.bins - 1):
            bins.append(self.GetMaxKSVal(data_upgrade))
            bins.sort()

            if len(bins) <= self.bins:
                # upgrade max sample bin
                df_buckets_stats = pd.cut(
                    data.variables, bins, include_lowest=True, duplicates='drop').value_counts(sort=True)
                max_bin = df_buckets_stats.idxmax()
                max_bin = [max_bin.left, max_bin.right]

                data_upgrade = data[data.variables.between(*max_bin, inclusive='right')].copy()
        self.cutoffpoint = bins

    def fit(self, score=True, origin_border=False, order=True):
        """

        :param score: 是否增加 WOE score。
        :param origin_border: 是否增加 分箱中的最大值与最小值。
        :param order: 是否增加单调性判断。
        :return: DataFrame WOE result.
        """
        self.GetCutoffpoint()

        value_cut, self.fix_cutoffpoint = pd.cut(
            self.variables, self.cutoffpoint, include_lowest=True, retbins=True)

        # 分箱与原值进行合并
        Bucket = pd.DataFrame({
            'variables': self.variables,
            'target': self.target,
            'Bucket': value_cut,
        }).groupby('Bucket', as_index=True)

        self.woe_iv_res(Bucket, score=score, origin_border=origin_border, order=order)
        return self.res

