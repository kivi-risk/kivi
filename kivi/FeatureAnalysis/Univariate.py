import pandas as pd
import numpy as np
from tqdm import tqdm_notebook
import statsmodels.api as sm
from ..utils.operator import Div, mode
from ..ModelTools.Metrics import KSTest, RocAucKs, Chi2


def StatsMetrics(column_info, model, column_name):
    """

    :param column_info:
    :param model:
    :param column_name:
    :param threshold:
    :return:
    """
    column_info.update({'R2': model.prsquared})
    column_info.update({'intercept': model.params.const})
    column_info.update({'pvalue_intercept': model.pvalues.const})
    column_info.update({'param': model.params[column_name]})
    column_info.update({'pvalue_param': model.pvalues[column_name]})
    column_info.update(RocAucKs(model.model.endog, predict=model.predict()))


def StatsUnivariate(df, col_description=dict(), target_name='target'):
    """
    描述：单变量回归，用于批量评估指标性能

    参数：
    :param df: DataFrame 需要进行单变量分析的数据。
    :param col_description: 字段的中英文映射字典；{var_name: cn_name}。
    :param target_name: 目标变量名称。
    :return:

    示例：
    >>>
    """
    columns_info = []
    columns_name = df.drop(target_name, axis=1).columns.to_list()
    sample_bad_rate = df[target_name].mean()

    for column_name in tqdm_notebook(columns_name, desc='单变量回归'):
        column_info = dict()
        column_info.update({'var_name': column_name})
        column_info.update({'bad_rate': sample_bad_rate})
        # 增加字段描述
        column_info.update({'des': col_description.get(column_name)})
        # 缺失率计算
        column_info.update({'missing': df[column_name].isna().sum() / df.shape[0]})

        miss_bad_rate = df[target_name][df[column_name].isna()].mean()
        not_miss_bad_rate = df[target_name][~df[column_name].isna()].mean()

        null_lift = Div.div(miss_bad_rate, sample_bad_rate)
        not_null_lift = Div.div(not_miss_bad_rate, sample_bad_rate)

        column_info.update({'miss_bad_rate': miss_bad_rate})
        column_info.update({'not_miss_bad_rate': not_miss_bad_rate})
        column_info.update({'null_lift': null_lift})
        column_info.update({'not_null_lift': not_null_lift})

        condition = ~(df[column_name].isna() | (np.isinf(df[column_name].astype('float'))))
        column_data = df[[column_name, target_name]][condition].copy()

        column_info.update({'min': column_data[column_name].min()})
        column_info.update({'max': column_data[column_name].max()})
        column_info.update({'std': float(column_data[column_name].std())})
        column_info.update({'mode': mode(column_data[column_name])})

        column_info.update({'skew': float(column_data[column_name].skew())})
        column_info.update({'kurt': float(column_data[column_name].kurt())})
        column_info.update({'cv': Div.div(float(column_data[column_name].std()), float(column_data[column_name].mean()))})
        column_info.update({'unique': len(column_data[column_name].unique())})

        column_info.update({'bad': column_data[target_name].sum()})
        column_info.update({'count': column_data[target_name].count()})
        column_info.update({'good': column_data[target_name].count() - column_data[target_name].sum()})
        column_info.update({'ks-test': KSTest(column_data[column_name], column_data[target_name])[0]})

        chi_statistic, chi_pvalue = Chi2(
            column_data[column_name].values.reshape(-1, 1),
            column_data[target_name].values)
        column_info.update({'chi_statistic': chi_statistic})
        column_info.update({'chi_pvalue': chi_pvalue})

        # 逻辑回归部分
        X = sm.add_constant(column_data[column_name], has_constant='add')
        try:
            model = sm.Logit(column_data[target_name], X).fit(disp=0)
            StatsMetrics(column_info, model=model, column_name=column_name)
        except Exception as e:
            print(e, f'Feature Name: {column_name}', col_description.get(str(column_name)), 'Model Error!')

        columns_info.append(column_info)
    return pd.DataFrame(columns_info)[[
        'var_name', 'des', 'bad_rate', 'missing', 'miss_bad_rate', 'not_miss_bad_rate',
        'null_lift', 'not_null_lift', 'min', 'max', 'std', 'mode', 'skew', 'kurt',
        'cv', 'unique', 'bad', 'count', 'good', 'ks-test', 'R2', 'intercept',
        'pvalue_intercept', 'param', 'pvalue_param', 'fpr', 'tpr', 'auc', 'ks',
        'chi_statistic', 'chi_pvalue']]



