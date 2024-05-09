

import numpy as np
import pandas as pd

class BinomialTest:

    def __init__(self, df_res=None, ranking=None,
                 target=None, proba=None, alpha=0.05,):
        """
        主标尺下的二项检验，支持两种调用方式
        方式一（推荐）：给定样本的评级等级 ranking、预测PD proba、真实违约 target
        方式二（不推荐）：给定依据评级等级分组后 df_res (DataFrame)
        :param df_res:
        :param ranking:
        :param target:
        :param proba:
        :param alpha:
        """
        import scipy.stats as st
        self.st = st

        self.ranking = ranking
        self.target = target
        self.proba = proba
        self.alpha = alpha

        if self.target is not None:
            groups = pd.DataFrame({
                'ranking': self.ranking,
                'target': self.target,
                'proba': self.proba,
            }).groupby('ranking')

            self.res = pd.DataFrame({
                'ranking': groups.target.sum().index,
                'counts': groups.target.count(),
                'default_nums': groups.target.sum(),
                'default': groups.target.mean(),
                'proba': groups.proba.mean(),
            })
        else:
            self.res = df_res

    def binomial_pvalue(
            self, count_col='counts', proba_col='proba', default_nums_col='default_nums'
    ):
        """
        若给定等级分组后的 df_res 则需指定以下列
            样本计数列 count_col
            分级内的平均预测概率 proba_col
            违约样本数 default_num_col
        :param count_col:
        :param proba_col:
        :param default_nums_col:
        :return:
        """
        group_proba = self.res[proba_col].copy()
        group_proba[group_proba != 1] = group_proba[group_proba != 1] + 1e-6
        group_proba[group_proba == 1] = group_proba[group_proba == 1] - 1e-6

        self.res['Z'] = (self.res[default_nums_col] - self.res[count_col] * group_proba) /\
                   np.sqrt(self.res[count_col] * group_proba * (1 - group_proba))
        self.res['distr'] = self.st.norm.cdf(-np.abs(self.res.Z))
        self.res['p_value'] = self.res.distr * 2
        self.res['binomial_test'] = [True if p > self.alpha else False for p in self.res.p_value]
        return self.res

    def binomial_boundary(
            self, count_col='counts', proba_col='proba', default_nums_col='default_nums',
            unilateral=None,
    ):
        """
        若给定等级分组后的 df_res 则需指定以下列
            样本计数列 count_col
            分级内的平均预测概率 proba_col
            违约样本数 default_num_col
        :param count_col:
        :param proba_col:
        :param default_nums_col:
        :param unilateral: left right
        :return:
        """
        group_proba = self.res[proba_col].copy()
        group_proba[group_proba != 1] = group_proba[group_proba != 1] + 1e-6


        if unilateral == 'left':
            self.res['d_min'] = self.st.binom.ppf(self.alpha, self.res[count_col], group_proba)
            self.res['binomial_test'] = self.res[default_nums_col] >= self.res.d_min
        elif unilateral == 'right':
            self.res['d_max'] = self.st.binom.ppf(1 - self.alpha, self.res[count_col], group_proba)
            self.res['binomial_test'] = self.res[default_nums_col] <= self.res.d_max
        else:
            self.res['d_min'] = self.st.binom.ppf(self.alpha / 2, self.res[count_col], group_proba)
            self.res['d_max'] = self.st.binom.ppf(1 - (self.alpha / 2), self.res[count_col], group_proba)
            self.res['binomial_test'] = np.logical_and(
                self.res[default_nums_col] <= self.res.d_max, self.res[default_nums_col] >= self.res.d_min)
        return self.res

def herfindahl(ranking: pd.Series):
    """
    Herfindahl index 赫芬达尔指数
    计量样本中不同评级的集中度, 一般值域为[1/k, 1]最大为20%。
    :param ranking: 评级等级
    :return: Herfindahl index
    """
    value_counts = ranking.value_counts()
    return sum((value_counts / value_counts.sum())**2)

