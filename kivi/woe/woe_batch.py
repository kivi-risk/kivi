import numpy as np
import pandas as pd
from ..utils.utils import dispatch_tqdm
from .woe_category import CategoryBins
from .woe_manually import ManuallyBins
from .woe_frequency import FrequencyBins
from .woe_chi2 import Chi2Bins
from .woe_tree import TreeBins

from IPython.display import display


__all__ = [
    "AppendRebinWoe",
    "Rebins",
    "IntScore",
    "FillBins",
    "FillBinScore",
    "WOEBatch",
    "WOEBatchWithRebin",
]


def AppendRebinWoe(df_woe, df_rebin):
    """
    描述：为原始分箱增加其他类型分箱。

    :param df_woe: 全量分箱。
    :param df_rebins: 补充分箱。
    :return: DataFrame
    """
    var_names = df_rebin.var_name.unique().tolist()
    df_origin = df_woe[df_woe.var_name.isin(var_names)].copy()

    origin_columns = df_origin.columns.tolist()
    rebin_columns = df_rebin.columns.tolist()
    subtract_columns = list(set(origin_columns) - set(rebin_columns)) + ['var_name']

    df_rebin = df_rebin.merge(df_origin[subtract_columns].drop_duplicates(), on='var_name')
    df_rebin = df_rebin[origin_columns]

    df_woe = df_woe[~df_woe.var_name.isin(var_names)]
    df_woe = df_woe.append(df_rebin)
    return df_woe


def Rebins(df, col_name, bins, target_name='target', abnormal_vals=[]):
    """
    描述：指定分箱阈值进行重分箱。
    :param df: DataFrame 数据。
    :param col_name: 需要进行重分箱的指标名称。
    :param bins: 分箱的截断点。
    :param target_name: 目标变量名称。
    :return:
    """
    target, x = df[target_name], df[col_name]
    cut = ManuallyBins(x, target, cutoffpoint=bins, fill_bin=True, abnormal_vals=abnormal_vals)
    df_rebin_woe = cut.fit()
    df_rebin_woe = df_rebin_woe.style.bar(
        subset=['bad_rate', 'woe', 'score'],
        align='mid', color=['#d65f5f', '#5fba7d'],)
    display(df_rebin_woe)


def IntScore(score):
    """
    将数值分数按 5 取整
    :param score: 浮点型分数
    :return: 按 5 取整分数
    """
    basic_score = np.arange(0, 101, 5)
    return basic_score[np.argmin(np.abs(score - basic_score))]


def FillBins(group, sort_by):
    """
    描述：

    参数：
    :param group:
    :param sort_by:
    :return:

    示例：

    """
    group.loc[:, 'woe_score'], group.loc[:, 'woe_score_int'] = -1, -1

    group = group.reset_index(drop=True)
    group.sort_values(by='woe', inplace=True)

    # select non inf data
    index = (-np.isinf(group.woe)).tolist()
    woe = group.woe[index]

    # order or not order
    diff = woe[1:] - woe[:-1]
    if np.all(diff >= 0) or np.all(diff <= 0):
        order = True
    else:
        order = False

    neg_woe = -woe
    woe_score = (neg_woe - neg_woe.min()) / (neg_woe.max() - neg_woe.min())
    group.loc[index, 'woe_score'] = woe_score * 100
    group.loc[index, 'woe_score_int'] = group.woe_score.apply(IntScore)
    group.loc[:, 'order'] = order
    return group.sort_values(by=sort_by)


def FillBinScore(data, col_name, sort_by="min_bin"):
    '''
    fill woe score in bins
    :param data: woe result
    :param col_name: feature name
    :return:
    '''
    df_new_woe = pd.DataFrame()
    for groupName, group in data.groupby(col_name):
        group = group.copy()
        group = FillBins(group, sort_by)
        if len(group) == 0:
            df_new_woe = group
        else:
            df_new_woe = df_new_woe.append(group)
    return df_new_woe


def WOEBatch(df, columns_name, target_name, WOEFun=FrequencyBins, bins:[int, dict]=5, abnormal_vals=[], **kwargs):
    """
    描述：批量计算WOE IV值

    参数：
    :param df: DataFrame 原始数据集。
    :param columns_name: 需要进行分箱的字段。
    :param target_name: 标签名称，默认为 `target`。
    :param WOEFun: 分箱方法，默认为决策树分箱 `Frequency`。
    :param bins[int, dict]: [int]分箱数量，默认为5；[dict(var_name: bins)]依据截断点分箱。

    :return:

    示例：
    >>> df_woe, faulted_cols = WOEBatch(
    >>>     df, columns_name=df.drop('target', axis=1).columns,
    >>>     target_name='target')
    """
    print(f'Samples shape: {df.shape}.')
    faulted_cols = []
    woe_container = []
    for col_name in dispatch_tqdm(columns_name, desc='计算WOE'):
        try:
            if WOEFun == CategoryBins:
                woe_fun = WOEFun(df[col_name], df[target_name], abnormal_vals=abnormal_vals)
            elif WOEFun == ManuallyBins:
                woe_fun = WOEFun(df[col_name], df[target_name], cutoffpoint=bins.get(col_name), fill_bin=True, abnormal_vals=abnormal_vals)
            elif WOEFun in [TreeBins, ManuallyBins]:
                woe_fun = WOEFun(df[col_name], df[target_name], bins=bins, fill_bin=True, abnormal_vals=abnormal_vals, **kwargs)
            elif WOEFun in [Chi2Bins]:
                woe_fun = WOEFun(df[col_name], df[target_name], fill_bin=True, init_bins=20, min_bins=2, max_bins=bins, abnormal_vals=abnormal_vals)
            else:
                Exception(ValueError, 'Bin Type Error!')
            woe = woe_fun.fit()
            woe.reset_index(inplace=True)
            woe_container.append(woe)
        except Exception as e:
            faulted_cols.append({col_name: e})
    print(faulted_cols)
    print(f'Faulted columns: {len(faulted_cols)}')
    print(len(woe_container))
    df_woe = pd.concat(woe_container, axis=0, ignore_index=True)
    if len(faulted_cols) == 0:
        return df_woe, None
    else:
        return df_woe, faulted_cols


def WOEBatchWithRebin(
        df, target_name='target', WOEFun=TreeBins, bins_type=['单调上升','单调下降'],
        max_bin=5, min_bin=2, columns_name=None, drop_columns=['uuid', 'target'], **kwargs):
    """
    描述：`WOEMixin` 计算批量化并进行自动合并分箱。

    参数：
    :param df: DataFrame 原始数据集。
    :param target_name: 标签名称，默认为 `target`。
    :param WOEFun: 分箱方法，默认为决策树分箱 `TreeBins`。
    :param bins_type: 保留分箱单调性，默认为 `['单调上升','单调下降']`；即对不满足条件的数据进行重分箱。
    :param max_bin: 允许最大分箱数量。
    :param min_bin: 允许最小分箱数量。
    :param columns_name: 需要进行分箱的字段。
    :param drop_columns: 需要剔除分箱的字段。
    :return:
    """
    bins = max_bin

    df_woe_total = pd.DataFrame()
    fault_cols = []

    if drop_columns and columns_name is None:
        columns_name = df.drop(drop_columns, axis=1).columns.tolist()

    df_woe, fault_col = WOEBatch(
        df=df, columns_name=columns_name, target_name=target_name, WOEFun=WOEFun, bins=bins, **kwargs)

    df_woe_monot = df_woe[df_woe.order.isin(bins_type)].copy()
    df_woe_rebin = df_woe[~df_woe.order.isin(bins_type)].copy()
    columns_rebin = df_woe_rebin.var_name.unique().tolist()

    print(f'bins: {bins}; columns_rebin: {len(columns_rebin)}; fault: {fault_cols}')
    df_woe_total = df_woe_monot.copy()
    fault_cols.append(fault_col)

    bins -= 1
    while len(columns_rebin) > 0 and bins >= min_bin:
        df_woe_new, fault_col_new = WOEBatch(
            df=df, columns_name=columns_rebin, target_name=target_name, WOEFun=WOEFun, bins=bins, **kwargs)
        df_woe_monot = df_woe_new[df_woe_new.order.isin(bins_type)].copy()
        df_woe_rebin = df_woe_new[~df_woe_new.order.isin(bins_type)].copy()
        columns_rebin = df_woe_rebin.var_name.unique().tolist()

        df_woe_total = pd.concat([df_woe_total, df_woe_monot], axis=0)
        fault_cols.append(fault_col_new)

        print(f'bins: {bins}; columns_rebin: {len(columns_rebin)}; fault: {fault_col_new}')
        bins -= 1

    df_woe_total = pd.concat([df_woe_total, df_woe_rebin], axis=0)
    return df_woe_total, fault_cols

