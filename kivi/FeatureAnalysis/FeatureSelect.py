import numpy as np
import pandas as pd


def TopNFeatures(df_woe, var_name='var_name', sort_by='ks', top_n=3, dim='dim'):
    """
    描述：依据指标的效果排序筛选指标。
    :param df_woe:
    :param var_name:
    :param sort_by:
    :param top_n:
    :param dim:
    :return:
    """
    columns = [var_name, 'des', 'ks', 'auc', 'dim']
    df_features = pd.DataFrame(columns=columns)
    df_woe = df_woe[columns].drop_duplicates()

    for group_name, group in df_woe.groupby(dim):
        df_group = group.copy()
        df_group.sort_values(sort_by, ascending=False, inplace=True)
        df_features = df_features.append(df_group.head(top_n))

    return df_features



