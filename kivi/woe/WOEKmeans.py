from .WOE import WOEMixin, pd, np
from sklearn.cluster import KMeans


__all__ = ['KmeansBins']


class KmeansBins(WOEMixin):
    """
    描述：决策树分箱
    """
    def __init__(self, variables, target, bins=5, abnormal_vals=[], fill_bin=True):
        """
        描述：[无监督分箱] Kmeans 分箱方法，使用 Kmeans 进行分箱分析。

        :param variables: 待分箱变量
        :param target: 目标标签变量
        :param bins: 决策树分箱中最大的叶子结点数量，一般对应的是最终分箱数量，默认为 5 。
        :param abnormal_vals: 特殊值分箱，在变量存在特殊值时单独分一箱，如 -1111, -9999。
        :param fill_bin: 在各分箱中偶发性会出现 good 或 bad 为 0 的情况，默认 fill_pos 为 True ，为该分箱填充 0.5。

        示例：
        >>> woe = KmeansBins(variables, target, bins=5, fill_bin=True)
        >>> woe.fit()
        """
        self.bins = bins
        self.data_init(variables, target, fill_bin=fill_bin, abnormal_vals=abnormal_vals)

    def GetCutoffpoint(self,):
        """"""
        vars = self.variables.to_numpy().reshape(-1, 1)
        kmeans = KMeans(n_clusters=self.bins, random_state=0).fit(vars)
        df_var_label = pd.DataFrame({
            'label': kmeans.fit_predict(vars).flatten(),
            'vars': self.variables
        })
        bins = sorted(df_var_label.groupby('label').max().vars.tolist())[:-1]
        bins += [np.inf, -np.inf]
        bins.sort()
        self.cutoffpoint = bins

    def fit(self, score=True, origin_border=False, order=True):
        """

        :param score: 是否增加 WOEMixin score。
        :param origin_border: 是否增加 分箱中的最大值与最小值。
        :param order: 是否增加单调性判断。
        :return: DataFrame WOEMixin result.
        """
        self.GetCutoffpoint()

        value_cut, self.fix_cutoffpoint = pd.cut(
            self.variables, self.cutoffpoint, include_lowest=True, retbins=True)

        # 分箱与原值进行合并
        Bucket = pd.DataFrame({
            'variables': self.variables,
            'target': self.target,
            'bucket': value_cut,
        }).groupby('bucket', as_index=True)

        self.cal_woe_iv(Bucket, score=score, origin_border=origin_border, order=order)
        return self.res

