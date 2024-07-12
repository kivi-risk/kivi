import logging
import pandas as pd
from tqdm import tqdm_notebook
from ..utils import WarnInfo


__all__ = [
    "WideToLong",
    "MatchWoe",
    "TransRealValToWOE",
    "SaveWOEVal",
    "TransToWOEVal",
]


def WideToLong(df, features: list, id_name='uuid', dtype='float'):
    """
    描述：宽表转为长表，用于WOE分数转换

    参数：
    :param df:
    :param features:
    :param id_name:
    :return:

    示例：
    """
    if id_name in features:
        features.remove(id_name)

    df_translated = df[features].add_prefix('values_').join(df[[id_name]])
    df_translated = pd.wide_to_long(
        df_translated, stubnames='values',
        i=id_name, j='var_name', sep='_', suffix='\w+'
    )
    df_translated.reset_index(inplace=True)
    df_translated.sort_values(by=id_name, inplace=True)
    df_translated.reset_index(inplace=True, drop=True)
    df_translated['values'] = df_translated['values'].astype(dtype)
    return df_translated


def MatchWoe(df_trans, df_woe, id_name='uuid', match_error='error', error_thresh=None):
    """
    描述：
    :param df_trans:
    :param df_woe:
    :param id_name:
    :param match_error:
    :param error_thresh:
    :return:
    """
    merge_score = df_trans.merge(df_woe, on='var_name', how='left')
    na_series = merge_score[['values', 'min_bin', 'max_bin']].isna().all(axis=1)
    notna_series = merge_score[['values', 'min_bin', 'max_bin']].isna().any(axis=1)
    df_sample_score_na = merge_score[na_series].copy()
    df_sample_score_notna = merge_score[~notna_series].copy()

    cond_eq = (df_sample_score_notna['values'] == df_sample_score_notna.min_bin) &\
              (df_sample_score_notna['values'] == df_sample_score_notna.max_bin)

    if error_thresh:
        cond_mid = (df_sample_score_notna['values'] > (df_sample_score_notna.min_bin - error_thresh)) &\
                   (df_sample_score_notna['values'] <= (df_sample_score_notna.max_bin + error_thresh))
    else:
        cond_mid = (df_sample_score_notna['values'] > df_sample_score_notna.min_bin) &\
                   (df_sample_score_notna['values'] <= df_sample_score_notna.max_bin)
    cond_mid = cond_mid | cond_eq

    df_sample_score_notna = df_sample_score_notna[cond_mid]

    df_sample_score = pd.concat(
        [df_sample_score_notna, df_sample_score_na], axis=0)
    df_sample_score.sort_values(by=id_name, inplace=True)

    if match_error == 'error':
        if df_sample_score.shape[0] != df_trans.shape[0]:
            raise Exception(
                ValueError,
                f'sample shape {df_sample_score.shape[0]} not match origin dataset shape {df_trans.shape[0]}.')
    elif match_error == 'skip':
        if df_sample_score.shape[0] > df_trans.shape[0]:
            logging.warning(f'Mutil Bins! {df_sample_score.shape}, {df_trans.shape}')
        elif df_sample_score.shape[0] < df_trans.shape[0]:
            logging.warning(f'Bins Margin Warn! {df_sample_score.shape}, {df_trans.shape}')

    return df_sample_score


def TransRealValToWOE(df, df_woe, features, values='woe', index='uuid'):
    """

    :param df:
    :param df_woe:
    :param features:
    :return:
    """
    df_long = WideToLong(df, features=features)
    df_long_woe = MatchWoe(df_trans=df_long, df_woe=df_woe)
    df_woe_features = df_long_woe.pivot(index=index, columns='var_name', values=values)
    return df_woe_features


def SaveWOEVal(df, df_woe, columns, id_name='uuid', join_origin=['uuid', 'target'], values='woe', disp=True):
    """
    描述：两种种WOE映射值

    :param df: DataFrame 原始数据集。
    :param df_woe: DataFrame WOEMixin 分箱表。
    :param columns: 需要转换的指标名称。
    :param join_origin: 保留原始数据中的字段信息，默认为样本 `uid` 以及标签 `target`。
    :param values: ['woe', 'score'] 转换的值，默认为 `woe` ;也可以是分数 `score`。
    :param disp: 是否展示转换进度信息，默认为 `True`。
    :return:

    示例：
    >>> df = SaveWOEVal(df, df_woe, columns,)
    """
    df_select = df[join_origin + columns].copy()
    df_woe_select = df_woe[df_woe.var_name.isin(columns)].copy()
    WarnInfo('【开始】宽表转长表...', disp)
    df_long = WideToLong(df_select, features=columns)
    WarnInfo('【开始】匹配WOE...', disp)
    df_woeval = MatchWoe(df_long, df_woe_select, match_error='skip')
    WarnInfo('【完成】匹配WOE。', disp)
    if isinstance(values, str):
        df_woeval_wide = df_woeval.pivot(index=id_name, columns='var_name', values=values)
        df_woeval_wide = df_woeval_wide.join(df_select[join_origin].set_index(id_name), on=id_name)
        return df_woeval_wide
    elif isinstance(values, list):
        df_woeval_wides = []
        for value in values:
            df_woeval_wide = df_woeval.pivot(index=id_name, columns='var_name', values=value)
            df_woeval_wide = df_woeval_wide.join(df_select[join_origin].set_index(id_name), on=id_name)
            df_woeval_wides.append(df_woeval_wide)
        return df_woeval_wides


def TransToWOEVal(df, df_woe, values='woe', batch=50):
    """
    描述：依据指标进行批量WOE分数转换。

    参数：
    :param df: DataFrame 原始数据集。
    :param df_woe: DataFrame WOEMixin 分箱表。
    :param values: 转换的值，默认为 `woe` ;也可以是分数 `score`。
    :param batch: 每个批次进行指标WOE分数转换的数量，默认为50。
    :return:

    示例：
    >>>
    """
    columns = df_woe.var_name.unique().tolist()

    df_woeval = pd.DataFrame()
    for i in tqdm_notebook(range(int(len(columns) // batch) + 1), desc='woe batch'):
        low, up = int(i * batch), int((i + 1) * batch)

        batch_columns = columns[low: up]
        if len(batch_columns) > 0:
            df_woeval_batch = SaveWOEVal(df, df_woe, batch_columns, disp=False, values=values)
            if i == 0:
                df_woeval = df_woeval_batch
            else:
                df_woeval = df_woeval.join(df_woeval_batch.drop('target', axis=1))

    df_woeval = df_woeval.astype(float)
    return df_woeval





