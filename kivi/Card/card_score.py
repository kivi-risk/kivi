import numpy as np
import pandas as pd
from ..utils.operator import NumRange

def PDToScore(PD, base_score=300, pdo=17, log='log2'):
    """
    描述：将预测概率转换为分数，这里区分以e为底取log或以2为底取log。
    以2为底取log，B 即为 pdo
    以e为底取log，B 即为 pdo / ln(2)
    1. ln(odds) = ln(p / 1 - p) = WX^T + b
    2. score = A - B ln(odds)
             = A - B ln(p / 1 - p)
             = A - B (WX^T + b)
    2. score = A - B log2(odds)
             = A - B log2(p / 1 - p)
             = A - B (WX^T + b)
    参数：
    :param PD: 违约概率
    :param base_score: 基准分
    :param pod: Points to Duble the Odds, Odds（好坏比）变为2倍时，所减少的信用分。
    :return: 分数
    """
    if log == 'log2':
        log = np.log2
    else:
        log = np.log
    return base_score + pdo * log((1 - PD) / PD)

def BaseScoreAndPDO(odds=1/50, base_score=600, pdo=20):
    """
    计算 base_score, pdo

    参数：
    :param odds:
    :param base_score:
    :param pdo:
    :return: A, B

    示例：
    >>> BaseScoreAndPDO()
    """
    B = pdo / np.log(2)
    A = base_score + B * np.log(odds)
    return A, B

def model_score_by_weight(
        df_woeval, df_param, weight_name='weight',
        target_name='target', reset_index=True, score_border=None):
    """
    描述：使用 logistics 回归的系数作为权重，返回模型分数。

    :param df_woeval: 指标经过 WOE 转换的分数值。
    :param df_param: 指标的权重。
    :param weight_name: 权重的名称。
    :param target_name: 标签的名称。
    :param reset_index: 重置 index。
    :param score_border: 分值的值域。
    :return:
    """

    df_score = pd.DataFrame()
    columns = df_param.index.tolist()

    if isinstance(df_param, pd.DataFrame):
        weight = np.array(df_param[weight_name].tolist())
    elif isinstance(df_param, pd.Series):
        weight = np.array(df_param.tolist())
    else:
        weight = [0] * len(df_param)

    weight = weight / weight.sum()
    score = df_woeval[columns].dot(weight)

    if score_border:
        a, b = score_border
        X_min, X_max = score.min(), score.max()
        df_score['score'] = NumRange(a, b, X_min, X_max, score)
    else:
        df_score['score'] = score

    df_score[target_name] = df_woeval[target_name]

    if reset_index:
        df_score.reset_index(inplace=True, drop=True)

    return df_score

