import numpy as np
import pandas as pd
from typing import List, Union, Tuple, Optional
from pandas import DataFrame


__all__ = [
    "BinsMixin",
    "lift",
]


def lift(
        score: DataFrame,
        score_name: Optional[str] = "score",
        target_name: Optional[str] = "target",
        bins: Optional[Union[int, List[Union[int, float]]]] = 10,
) -> DataFrame:
    """ 计算模型结果的lift """
    score["buckets"] = pd.cut(score[score_name], bins=bins, include_lowest=True)
    df_buckets = score.groupby('buckets', observed=False).agg({target_name: ['count', 'sum']})

    df_buckets.columns = ['total', 'bad']
    df_buckets['good'] = df_buckets.total - df_buckets.bad
    df_buckets['bad_rate'] = df_buckets.bad / df_buckets.total

    df_buckets['cum_total'] = df_buckets.total.cumsum() / df_buckets.total.sum()
    df_buckets['cum_bad'] = df_buckets.bad.cumsum() / df_buckets.bad.sum()
    df_buckets['cum_good'] = df_buckets.good.cumsum() / df_buckets.good.sum()
    df_buckets['ks'] = df_buckets.cum_bad - df_buckets.cum_good
    df_buckets['lift'] = df_buckets.cum_bad / df_buckets.cum_total
    return df_buckets


class BinsMixin:

    def Getcutoffpoint(self, bins, data, cut_type='qcut'):
        """
        Des: 计算cutoff point，包括等距分箱，等频分箱
        :param bins: 分箱数
        :param percent: 是否使用等频分箱，默认为不使用False
        :param kwargs: 其他参数
        :return: cutoff point
        """

        if cut_type == 'qcut':
            cut = pd.qcut
        elif cut_type == 'cut':
            cut = pd.cut

        _, self.cutoffpoint = cut(
            data, bins, retbins=True, include_lowest=True, duplicates='drop',
        )

        self.cutoffpoint[0] = -np.inf
        self.cutoffpoint[-1] = np.inf

