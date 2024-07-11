import logging
import numpy as np
import pandas as pd
from pyspark.sql import functions as F
from ..utils import WarnInfo
from ..utils.operator import NumRange


def SaveWOEVal(df, df_woe, columns, join_origin=['uuid', 'target'], values='woe', disp=True):
    """
    描述：保存三种WOE映射值
    :param df:
    :param df_woe:
    :param columns:
    :params values: ['woe', 'woe_score', 'woe_score_int']

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
        df_woeval_wide = df_woeval.pivot(index='uuid', columns='var_name', values=values)
        df_woeval_wide = df_woeval_wide.join(df_select[join_origin].set_index('uuid'), on='uuid')
        return df_woeval_wide
    elif isinstance(values, list):
        df_woeval_wides = []
        for value in values:
            df_woeval_wide = df_woeval.pivot(index='uuid', columns='var_name', values=value)
            df_woeval_wide = df_woeval_wide.join(df_select[join_origin].set_index('uuid'), on='uuid')
            df_woeval_wides.append(df_woeval_wide)
        return df_woeval_wides

def WideToLong(df, features, id_name='uuid'):
    """
    描述：宽表转为长表，用于WOE分数转换

    参数：
    :param df:
    :param features:
    :param id_name:
    :return:

    示例：

    """
    df_translated = df[features].add_prefix('value_').join(df[[id_name]])
    df_translated = pd.wide_to_long(
        df_translated, stubnames='value',
        i=id_name, j='var_name', sep='_', suffix='\w+'
    )
    df_translated.reset_index(inplace=True)
    df_translated.sort_values(by='uuid', inplace=True)
    df_translated.reset_index(inplace=True, drop=True)
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
    na_series = merge_score[['value', 'min_bin', 'max_bin']].isna().all(axis=1)
    notna_series = merge_score[['value', 'min_bin', 'max_bin']].isna().any(axis=1)
    df_sample_score_na = merge_score[na_series].copy()
    df_sample_score_notna = merge_score[~notna_series].copy()

    cond_eq = (df_sample_score_notna['value'] == df_sample_score_notna.min_bin) &\
              (df_sample_score_notna['value'] == df_sample_score_notna.max_bin)

    if error_thresh:
        cond_mid = (df_sample_score_notna['value'] >= (df_sample_score_notna.min_bin - error_thresh)) &\
                   (df_sample_score_notna['value'] < (df_sample_score_notna.max_bin + error_thresh))
    else:
        cond_mid = (df_sample_score_notna['value'] >= df_sample_score_notna.min_bin) &\
                   (df_sample_score_notna['value'] < df_sample_score_notna.max_bin)
    cond_mid = cond_mid | cond_eq

    df_sample_score_notna = df_sample_score_notna[cond_mid]

    df_sample_score = df_sample_score_notna.append(df_sample_score_na)
    df_sample_score.sort_values(by=id_name, inplace=True)

    if match_error == 'error':
        if df_sample_score.shape[0] != df_trans.shape[0]:
            raise Exception(
                ValueError,
                f'sample shape {df_sample_score.shape[0]} not match origin dataset shape {df_trans.shape[0]}.'
            )
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

def FixWoeBins(df_woe, drop_woe_val=False, groupby='var_name'):
    """
    描述：修正 WOE 分箱中的大小边界。
    :param df_woe:
    :param drop_woe_var:
    :return:
    """
    if drop_woe_val:
        columns = df_woe.columns
    else:
        columns = df_woe.columns.tolist() + ['min_bin_val', 'max_bin_val']

    df_woe_fix = pd.DataFrame(columns=columns)
    for group_name, group in df_woe.groupby(groupby):
        group = group.copy()
        if not drop_woe_val:
            group.loc[:, 'min_bin_val'] = group['min_bin']
            group.loc[:, 'max_bin_val'] = group['max_bin']
        group.loc[group.min_bin.idxmin(), 'min_bin'] = -np.inf
        group.loc[group.max_bin.idxmax(), 'max_bin'] = np.inf
        group.loc[1: , 'min_bin'] = group.max_bin[: -1].values
        if group.max_bin.isna().sum() > 0:
            group.loc[group.max_bin.isna(), 'min_bin'] = np.nan
        df_woe_fix = df_woe_fix.append(group)
    return df_woe_fix

def FixWoeVal(df_woe, groupby='var_name'):
    """
    描述：依据WOE值，确定WOE分箱值域范围
    :param df_woe:
    :param groupby:
    :return:
    """
    df_fixed_val = pd.DataFrame(columns=df_woe.columns.tolist() + ['min_woe_val', 'max_woe_val'])
    for group_name, group in df_woe.groupby(groupby):
        group = group.copy()
        if group['corr'].values[0] == -1:
            diff_val, method = -1, 'ffill'
        elif group['corr'].values[0] == 1:
            diff_val, method = 1, 'bfill'
        group['min_woe_val'] = group.woe - (group.woe.diff(diff_val) / 2).fillna(method=method)
        group['max_woe_val'] = group.woe + (group.woe.diff(diff_val) / 2).fillna(method=method)
        df_fixed_val = df_fixed_val.append(group)
    return df_fixed_val

def WoeDeviation(row):
    """
    描述：
    :param row:
    :return:
    """
    if pd.np.isnan(row.value):
        val = row.woe

    elif row['corr'] == 1.:
        if row.value < row.min_bin_val:
            val = row.min_woe_val
        elif row.value > row.max_bin_val:
            val = row.max_woe_val
        else:
            val = NumRange(row.min_woe_val, row.max_woe_val, row.min_bin_val, row.max_bin_val, row.value)

    elif row['corr'] == -1.:
        if row.value < row.min_bin_val:
            val = row.max_woe_val
        elif row.value > row.max_bin_val:
            val = row.min_woe_val
        else:
            val = NumRange(row.min_woe_val, row.max_woe_val, -row.min_bin_val, -row.max_bin_val, -row.value)
    else:
        val = -99999.
    return val

def ModelResultSpark(df_match, score_shceme='sigmod'):
    """
    描述：使用spark计算模块结果，计算模型结果

    参数：
    :param df_match: 匹配分数表
    :param score_shceme: 分数计算方案 `simode`, `linear`
    :return pyspark DataFrame 模型结果表

    示例：
    >>>
    """
    if score_shceme == 'simode':
        weight_type = 'coef'
    elif score_shceme == 'linear':
        weight_type = 'wight'

    df_module = df_match.groupBy('load_date', 'uuid', 'module_name').agg(
        (-(F.sum(F.col('woe') * F.col(f'var_{weight_type}')) + F.first('var_intercept'))).alias('module_ln_odds'),
        (1 / (1 + F.exp(-(F.sum(F.col('woe') * F.col(f'var_{weight_type}')) + F.first('var_intercept'))))).alias(
            'module_pd'),
        F.first('k').alias('k'),
        F.first(f'module_{weight_type}').alias(f'module_{weight_type}'),
        F.first('module_intercept').alias('module_intercept'),
        F.first('module_min_pd').alias('module_min_pd'),
        F.first('module_max_pd').alias('module_max_pd'), )

    df_module = df_module.withColumn('sig', F.when(F.col('module_coef') > 0, 1).otherwise(-1)) \
        .withColumn('module_score', ((F.col('sig') * F.lit(100) / (F.col('module_max_pd') - F.col('module_min_pd'))) * (
                F.col('module_pd') - F.col('module_min_pd'))))

    df_model = df_module.groupBy('load_date', 'uuid').agg(
        (-(F.sum(F.col('module_score') * F.col(f'module_{weight_type}')) + F.first('module_intercept'))).alias(
            'modle_ln_odds'),
        (1 / (1 + F.first('k') * F.exp(
            -(F.sum(F.col('module_score') * F.col(f'module_{weight_type}')) + F.first('module_intercept'))))).alias(
            'modle_pd'),
    )
    df_model_result = df_module.join(df_model, on=['load_date', 'uuid'], how='left')

    return df_model_result
