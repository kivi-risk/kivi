
import numpy as np
import pandas as pd
from numpy import linspace, percentile

class Bins:

    def Getcutoffpoint(self, bins, data, cut_type='qcut'):
        """
        Des: 计算cutoff point，包括等距分箱，等频分箱
        :param bins: 分箱数
        :param percent: 是否使用等频分箱，默认为不使用False
        :param kwargs: 其他参数
        :return: cutoff point
        """

        if cut_type == 'qcut':
            cut = pd.qcut
        elif cut_type == 'cut':
            cut = pd.cut

        _, self.cutoffpoint = cut(
            data, bins, retbins=True, include_lowest=True, duplicates='drop',
        )

        self.cutoffpoint[0] = -np.inf
        self.cutoffpoint[-1] = np.inf

