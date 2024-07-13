import logging
import numpy as np
import pandas as pd
from collections import defaultdict


def get_one_score(value, group, variable_name, cut_point_name='max_bin', woe_point_name='woe_score_int'):

    # 获取此字段的最大最小值
    _max = group.max_bin.max()
    _min = group.min_bin.min()

    # 处理空箱的赋值
    if pd.isna(value):
        score = group[woe_point_name][group.min_bin.isna().tolist()]
        # 找到唯一的空箱，并赋值相应的分数
        if len(score) == 1:
            return int(score)
        # 未找到空箱警告，并对未找到的空值赋分数nan
        elif len(score) == 0:
            logging.warning(f'{variable_name} Not Found Nan Bin! return np.nan!')
            return np.nan
    # 非空箱赋值
    else:
        # 如果真实值，未在分箱给定的最大值与最小值的范围内，则给出报错
        if not (_min <= value <= _max):
            raise Exception(ValueError, f'{variable_name}: {_min} <= {value} <= {_max} Value is out of range!')
        # 获得该值在 group 中的 index
        group.sort_values(by=cut_point_name, inplace=True)
        cut_point = group[cut_point_name].dropna().tolist()
        cut_point.insert(0, -np.inf)
        cut_point[-1] = np.inf
        index = [False] * len(group)
        for i_cut_point in range(len(cut_point) - 1):
            if float(cut_point[i_cut_point]) < value <= float(cut_point[i_cut_point + 1]):
                index[i_cut_point] = True
        # 如果未能找到该值的分箱，则给出报错
        if True not in index:
            raise Exception(ValueError, f'Not fund that bin: {value}')
        # 如果得到唯一的分箱对应值，则返回该值的分箱对应值
        elif sum(index) == 1:
            return int(group[woe_point_name][index])
        # 如果找到多个分箱的对应值，则给出警告，并返回 'multi nums' 多值字符串
        else:
            logging.warning(f'multi nums {variable_name}')
            return 'multi nums'


def get_all_point(
        df_sample: pd.DataFrame, df_woe: pd.DataFrame,
        values_name='values', sample_variable_name='name',
        woe_variable_name='name', woe_point_name='woe_score_int',
        id_name=None, pbar_type=None, des=None,
):
    """
    根据计算的WOE值计算评分卡单项的得分
    :param df_sample: 样本表，每行为一个样本，每列为特征
    :param df_woe: WOE值的表
    :param values_name: df_sample 中的真实样本值的列名称
    :param sample_variable_name: df_sample 中的字段名称列的名字
    :param woe_variable_name: df_woe 中的字段名称列的名字
    :param woe_point_name: df_woe 中的woe值列的名字
    :param id_name: id列的名字
    :param pbar_type: 进度条的展示方式，如果在jupyter notebook中使用则
    :param des: 进度条分割展示的分割虚线标题
    :return: 单项得分表
    """
    res_dict = defaultdict(list)
    if id_name and id_name in df_sample.columns:
        res_dict['id'] = df_sample[id_name].tolist()
    res_dict['variable'] = df_sample[sample_variable_name].tolist()

    values = df_sample[values_name]
    variable_names = df_sample[sample_variable_name]

    # shell & Notebook 进度条
    if pbar_type is not None:
        from tqdm import tqdm_notebook as tqdm
    else:
        from tqdm import tqdm

    # 获取 scheme 下的赋值分数
    print(f"{15 * '='} {des} {15 * '='}")
    with tqdm(total=len(values), desc=f'{des} scoring:') as pbar:
        for value, variable_name in zip(values, variable_names):
            res_dict['point'].append(get_one_score(
                value=value,
                variable_name=variable_name,
                group=df_woe[df_woe[woe_variable_name] == variable_name].copy(),
                woe_point_name=woe_point_name,
            ))
            pbar.update(1)
    return pd.DataFrame(res_dict)





