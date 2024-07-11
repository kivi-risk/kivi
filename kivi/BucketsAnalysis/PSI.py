import numpy as np
import pandas as pd
from ..utils.Bins import Bins
from .BucketsUtils import psi

class PSI(Bins):

    def __init__(self,):
        """
        Des: 计算PSI
        """

    def miss_data_cnt(self, expected, actual):
        """

        """
        sum_ex = sum(expected.isna())
        sum_ac = sum(actual.isna())

        if sum_ex > 0 or sum_ac > 0:
            na_bin = pd.DataFrame({
                'min_bin': [np.nan],
                'max_bin': [np.nan],
                'Expected': [sum_ex],
                'Actual': [sum_ac],
            })
            return na_bin
        else:
            return None

    @staticmethod
    def _psi(res):
        """
        Des: 计算PSI的核心函数
        :param res: 明细表
        :return: 明细表以及PSI值 res, psi
        """
        if 0 in res.Expected:
            res.Expected += 1
        if 0 in res.Actual:
            res.Actual += 1

        res['Expected_percentage'] = res.Expected / res.Expected.sum()
        res['Actual_percentage'] = res.Actual / res.Actual.sum()
        res['A-E'] = res.Actual_percentage - res.Expected_percentage
        res['A/E'] = res.Actual_percentage / res.Expected_percentage
        res['ln(A/E)'] = np.log(res['A/E'])
        res['index'] = res['A-E'] * res['ln(A/E)']
        res['psi'] = res['index'].sum()
        return res

    def Continue(self, expected, actual, bins=10, cut_type='distance', cutpoint=None):
        """
        Des: 连续型变量的PSI指标
        :param expected: 预期分布
        :param actual: 实际分布
        :param bins: 分箱数目
        :param binType: 分箱类型 'distance'等距 or 'frequency'等频 or 'customize'自定义
        :return: 明细表以及PSI值 res, PSI
        """
        if not pd.api.types.is_numeric_dtype(expected):
            raise Exception(TypeError, 'expected must be numeric!')

        if not pd.api.types.is_numeric_dtype(actual):
            raise Exception(TypeError, 'actual must be numeric!')

        if cutpoint is not None:
            self.cutoffpoint = cutpoint
        else:
            self.Getcutoffpoint(bins, expected, cut_type=cut_type)

        df_ex = pd.DataFrame(
            pd.cut(expected, self.cutoffpoint, include_lowest=True).value_counts(sort=False),
            columns=['Expected'])
        df_ac = pd.DataFrame(
            pd.cut(actual, self.cutoffpoint, include_lowest=True).value_counts(sort=False),
            columns=['Actual'])

        res = df_ex.join(df_ac, how='outer')
        res['min_bin'] = self.cutoffpoint[: -1]
        res['max_bin'] = self.cutoffpoint[1: ]

        na_bin = self.miss_data_cnt(expected, actual)
        if na_bin is not None: res = res.append(na_bin)

        return psi(res)

    def Category(self, expected, actual):
        """
        Des: 类别型变量的PSI
        :param expected:
        :param actual:
        :return: 明细表以及PSI值 res, PSI
        """
        expected.dropna(inplace=True)
        actual.dropna(inplace=True)

        expectedGroup = expected.value_counts(sort=False)
        actualGroup = actual.value_counts(sort=False)

        res = pd.merge(
            pd.DataFrame({'category': expectedGroup.index, 'Expected': expectedGroup.values}),
            pd.DataFrame({'category': actualGroup.index, 'Actual': actualGroup.values}),
            on='category',
            how='outer',
        )
        return psi(res)
    
    def fit(self, expected, actual, data_type='continue', bins=10, cut_type='distance', cutpoint=None):
        """
        描述：拟合 PSI 。
        :param expected: 期望数据
        :param actual: 实际数据
        :param data_type: 数据类型，continue 或 category。
        :param bins: 分箱数目。
        :param cut_type: 分箱类型 distance 或 frequency
        :param cutpoint: 分箱截断点。
        :return:
        """
        
        if data_type == 'continue':
            return self.Continue(expected, actual, bins=bins, cut_type=cut_type, cutpoint=cutpoint)
        elif data_type == 'category':
            return self.Category(expected, actual)
