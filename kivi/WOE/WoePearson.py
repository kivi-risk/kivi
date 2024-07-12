import numpy as np
import pandas as pd
from .WOE import WOEMixin
from tqdm import tqdm_notebook
import pandas.core.algorithms as algos
import scipy.stats.stats as stats


__all__ = [
    "Pearson"
]


class Pearson(WOEMixin):

    def __init__(self, df, targetName='target', R=1, ForceBin=3, MaxBin=20):
        """
        描述：使用 Pearson 相关系数方法进行分箱分析。

        :param df: 需要计算的DataFrame。不需要进行字段数据类型区分，以及缺失处理。
        :param targetName: 标签名称，默认为'target'
        :param R: 相关系数阈值
        :param ForceBin: 最小分箱数
        :param MaxBin: 最大分箱数

        示例：
        >>> woe = Pearson(df, targetName='target', R=1, ForceBin=3, MaxBin=20)
        >>> woe.fit()
        """
        self.data_init(variables=None, target=None, all_feature=True, weight=None)
        self.R = R
        self.df = df
        self.MaxBin = MaxBin
        self.ForceBin = ForceBin
        self.targetName = targetName

    def __createRes(self, res, justMiss):
        """

        :param res:
        :param justMiss:
        :return:
        """
        res = res.reset_index(drop=True)

        if len(justMiss.index) > 0:
            _df_temp = pd.DataFrame({
                'min_value': [np.nan],
                'max_value': [np.nan],
                'Count': justMiss.count().target,
                "event": justMiss.sum().target,
                'non_event': justMiss.count().target - justMiss.sum().target
            })
            res = res.append(_df_temp, ignore_index=True)

        res["event_rate"] = res.event / res.Count
        res["non_event_rate"] = res.non_event / res.Count
        res["dist_event"] = res.event / res.sum().event
        res["dist_non_event"] = res.non_event / res.sum().non_event
        res["woe"] = np.log(res.dist_event / res.dist_non_event)
        res["iv"] = (res.dist_event - res.dist_non_event) * np.log(
            res.dist_event / res.dist_non_event)
        res["var_name"] = "var"
        res = res[[
            'var_name', 'min_value', 'max_value', 'Count', 'event',
            'event_rate', 'non_event', 'non_event_rate',
            'dist_event', 'dist_non_event', 'woe', 'iv'
        ]]

        res = res.replace([np.inf, -np.inf], 0)
        res.iv = res.iv.sum()
        res = res.reset_index(drop=True)
        return res

    def continuousBin(self, variables, target, score=True, origin_border=False, order=True):
        """

        :param variables:
        :param target:
        :return:
        """
        n = self.MaxBin
        ForceBin = self.ForceBin

        self.justMiss, self.notMiss, self.abnormal = self._data_prepare(variables=variables, target=target)

        r = 0

        while np.abs(r) < self.R:
            try:
                BucketGroup = pd.DataFrame({
                    "variables": self.notMiss.variables,
                    "target": self.notMiss.target,
                    "bucket": pd.qcut(self.notMiss.variables, n)
                }).groupby('bucket', as_index=True)

                r, p = stats.spearmanr(BucketGroup.mean().variables, BucketGroup.mean().target)
                n -= 1
            except Exception as e:
                n -= 1

        if len(BucketGroup.mean()) == 1:
            bins = algos.quantile(self.notMiss.variables, np.linspace(0, 1, ForceBin))
            if len(np.unique(bins)) == 2:
                bins = np.insert(bins, 0, 1)
                bins[1] = int(bins[1] / 2)

            BucketGroup = pd.DataFrame({
                "variables": self.notMiss.variables,
                "target": self.notMiss.target,
                "bucket": pd.cut(self.notMiss.variables, np.unique(bins), include_lowest=True)
            }).groupby('bucket', as_index=True)

        self.cal_woe_iv(BucketGroup, score=score, origin_border=origin_border, order=order)
        return self.res

    def charBin(self, variables, target, score=True, origin_border=False, order=True):
        """

        :param variables:
        :param target:
        :return:
        """
        self.justMiss, self.notMiss, self.abnormal = self._data_prepare(variables, target)
        BucketGroup = self.notMiss.groupby('variables', as_index=True)

        self.cal_woe_iv(BucketGroup, score=score, origin_border=origin_border, order=order)
        return self.res

    def fit(self, score=True, origin_border=False, order=True):
        """
        :param score: 是否增加 WOEMixin score。
        :param origin_border: 是否增加 分箱中的最大值与最小值。
        :param order: 是否增加单调性判断。
        :return: DataFrame WOEMixin result.
        """
        df = self.df.copy()
        target = df.pop(self.targetName)
        cols = df.columns
        woe = pd.DataFrame()
        self._basic_count(target)

        for col in tqdm_notebook(cols):

            self.variables = df[col]
            self.target = target

            if np.issubdtype(df[col], np.number) and len(pd.Series.unique(df[col])) > 2:
                conv = self.continuousBin(df[col], target, score=score, origin_border=origin_border, order=order)
            else:
                conv = self.charBin(df[col], target, score=score, origin_border=origin_border, order=order)
            conv["var_name"] = col
            if len(woe) == 0:
                woe = conv
            else:
                woe = woe.append(conv, ignore_index=True)

        return woe

