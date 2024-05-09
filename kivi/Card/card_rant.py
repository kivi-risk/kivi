
import numpy as np
import pandas as pd

def PDToRant(pd: float, ranking: list, max_grade: int = 16):
    """
    PD 到主标尺等级的映射
    :param pd: 预测PD
    :param ranking: 主标尺分箱的max bin
    :return: 等级
    """
    if pd==1.:
        return max_grade
    else:
        return sum(np.array(ranking) <= pd) + 1
