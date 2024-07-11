from .WOE import WOE, pd


__all__ = ['CutOffPoint']


class CutOffPoint(WOE):
    """
    自定义分箱截断点 woe iv 计算方式
    """
    def __init__(self, variables, target, cutoffpoint, abnormal_vals=[], fill_bin=True):
        """
        描述：自定义截断点进行分箱

        :param variables: 待分箱变量
        :param target: 目标标签变量
        :param cutoffpoint: 分箱截断点
        :param abnormal_vals: 特殊值分箱，在变量存在特殊值时单独分一箱，如 -1111, -9999。
        :param fill_bin: 在各分箱中偶发性会出现 good 或 bad 为 0 的情况，默认 fill_bin 为 True ，为该分箱填充 0.5。

        示例：
        >>> woe = CutOffPoint(variables, target, bins=5, fill_bin=True)
        >>> woe.fit()
        """
        self.cutoffpoint = cutoffpoint
        self.data_init(variables, target, fill_bin=fill_bin, abnormal_vals=abnormal_vals)


    def fit(self, score=True, origin_border=False, order=True):
        """
        :param score: 是否增加 WOE score。
        :param origin_border: 是否增加 分箱中的最大值与最小值。
        :param order: 是否增加单调性判断。
        :return: DataFrame WOE result.
        """
        # 依据自定义的分箱截断点进行分箱，并返回修正分箱截断点
        value_cut, self.fix_cutoffpoint = pd.cut(
            self.variables, self.cutoffpoint, include_lowest=True, retbins=True, duplicates='drop')

        Bucket = pd.DataFrame({
            'variables': self.variables,
            'target': self.target,
            'Bucket': value_cut,
        }).groupby('Bucket', as_index=True)

        self.woe_iv_res(Bucket, score=score, origin_border=origin_border, order=order)
        return self.res
