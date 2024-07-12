import pandas as pd
from .WOE import WOEMixin


__all__ = ["Category"]


class Category(WOEMixin):
    """
    类别型变量的分箱
    """
    def __init__(self, variables, target, fill_bin=True):
        """
        描述：类别型变量分箱分析。

        :param variables: 待分箱变量
        :param target: 目标标签变量
        :param fill_bin: 在各分箱中偶发性会出现 good 或 bad 为 0 的情况，默认 fill_pos 为 True ，为该分箱填充 0.5。

        示例：
        >>> woe = Category(variables, target)
        >>> woe.fit()
        """
        self.data_init(variables, target, fill_bin=fill_bin)

    def fit(self, score=True, origin_border=False, order=True):
        """
        :param score: 是否增加 WOEMixin score。
        :param origin_border: 是否增加 分箱中的最大值与最小值。
        :param order: 是否增加单调性判断。
        :return: DataFrame WOEMixin result.
        """
        # bins groupby bucket
        Bucket = pd.DataFrame({
            'variables': self.variables,
            'target': self.target,
            'bucket': self.variables,
        }).groupby('bucket', as_index=True)

        self.cal_woe_iv(Bucket, score=score, origin_border=origin_border, order=order)
        return self.res
