import numpy as np
import pandas as pd
from typing import Literal


__all__ = [
    "int_score",
    "detect_monotony",
    "monotony",
]


TypeOrder = Literal["上升下降	", "上升下降", "单调上升", "单调下降", "未知"]


def int_score(score):
    """
    将数值分数按 5 取整
    :param score: 浮点型分数
    :return: 按 5 取整分数
    """
    basic_score = np.arange(0, 101, 5)
    return basic_score[np.argmin(np.abs(score - basic_score))]


def detect_monotony(trend_mask):
    """"""
    if all(trend_mask):
        return '单调上升'
    elif not any(trend_mask):
        return '单调下降'
    else:
        return None


def monotony(values: pd.Series):
    """"""
    diff = values.diff().dropna()
    if len(diff) > 0:
        trend_mask = (diff >= 0).tolist()
        trend = detect_monotony(trend_mask)
        if trend:
            return trend
        else:
            for mask_id in range(len(trend_mask)):
                top_trend = detect_monotony(trend_mask[: mask_id])
                end_trend = detect_monotony(trend_mask[mask_id:])
                if all([top_trend, end_trend]):
                    trend = f'{top_trend[2:]}{end_trend[2:]}'
                    return trend
            return '未知'
    else:
        return '数据不足'

