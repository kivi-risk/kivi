import pandas as pd
from scipy import stats
from itertools import combinations


def spearmanr(df, columns):
    """
    描述：spearman 相关系数。
    Spearman 秩相关系数是两个数据集之间关系单调性的非参数度量。
    与 Pearson 相关性不同，Spearman 相关性不假设两个数据集都是正态分布的。
    Spearman 系数在 -1 和 +1 之间变化，0 表示没有相关性。
    -1 或 +1 的相关性意味着精确的单调关系。正相关意味着随着 x 的增加，y 也会增加。
    负相关意味着随着 x 增加，y 减少。

    p 值粗略地表示不相关系统生成具有 Spearman 相关性的数据集的概率，
    p 值并不完全可靠，但对于大于 500 左右的数据集可能是合理的。

    :param df: DataFrame 需要统计相关系数的数据。
    :param columns: 需要统计相关系数的数据列名。
    :return: DataFrame
    """
    group = list(combinations(columns, 2))
    df_spearmanr = pd.DataFrame(group, columns=['col_a', 'col_b'])

    def one_group_spearmanr(cols):
        """"""
        return stats.spearmanr(*cols).correlation

    group_data = [[df[col_a].to_numpy(), df[col_b].to_numpy()] for col_a, col_b in group]
    df_spearmanr['corr'] = list(map(one_group_spearmanr, group_data))
    df_spearmanr = df_spearmanr.pivot(index='col_a', columns='col_b', values='corr')

    df_spearmanr = df_spearmanr.sort_index()
    df_spearmanr = df_spearmanr[sorted(df_spearmanr.columns.tolist())]
    return df_spearmanr
