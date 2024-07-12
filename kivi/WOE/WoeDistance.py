from .WOE import WOEMixin, pd


__all__ = ["Distance"]


class Distance(WOEMixin):
    """

    """
    def __init__(self, variables, target, bins, abnormal_vals=[], fill_bin=False):
        """
        描述：等距分箱分析。

        :param variables: 待分箱变量
        :param target: 目标标签变量
        :param bins: 决策树分箱中最大的叶子结点数量，一般对应的是最终分箱数量，默认为 5 。
        :param abnormal_vals: 特殊值分箱，在变量存在特殊值时单独分一箱，如 -1111, -9999。
        :param fill_bin: 在各分箱中偶发性会出现 good 或 bad 为 0 的情况，默认 fill_pos 为 True ，为该分箱填充 0.5。

        示例：
        >>> woe = Distance(variables, target, bins=5, fill_bin=True)
        >>> woe.fit()
        """
        self.bins = bins
        self.data_init(variables, target, bins, fill_bin=fill_bin, abnormal_vals=abnormal_vals)

    def fit(self, score=True, origin_border=False, order=True):
        """
        :param score: 是否增加 WOEMixin score。
        :param origin_border: 是否增加 分箱中的最大值与最小值。
        :param order: 是否增加单调性判断。
        :return: DataFrame WOEMixin result.
        """
        Bucket = pd.DataFrame({
            'variables': self.variables,
            'target': self.target,
            'bucket': pd.cut(self.variables, self.bins, include_lowest=True, duplicates='drop')
        }).groupby('bucket', as_index=True)

        self.cal_woe_iv(Bucket, score=score, origin_border=origin_border, order=order)
        return self.res

