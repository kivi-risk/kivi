import pandas as pd
from ..utils.Bins import Bins


class CSI(Bins):
    def __init__(self, score=None):
        """
        Des: 计算CSI
        :param score: 分箱分数
        :param margin: cutoff point 左右填充预留边界
        """
        super(CSI, self).__init__()
        self.score = score

    def _csi(self, res):
        """
        Des: 计算CSI的核心函数
        :param res: 明细表
        :return: 明细表以及CSI值 res, csi
        """

        res['Expected_percentage'] = res.Expected / res.Expected.sum()
        res['Actual_percentage'] = res.Actual / res.Actual.sum()
        res['A-E'] = res.Actual_percentage - res.Expected_percentage
        if len(res) != len(self.score):
            raise Exception(TypeError, 'Score len error!')
        res['score'] = self.score
        res['index'] = res['A-E'] * self.score
        csi = res['index'].sum()
        return res, csi

    def Continue(self, expected, actual, bins=10, binType='distance', cutPoint=None):
        """
        Des: 连续型变量的CSI指标
        :param expected: 预期分布
        :param actual: 实际分布
        :param bins: 分箱数目
        :param binType: 分箱类型 'distance'等距 or 'frequency'等频 or 'customize'自定义
        :param csvName: 保存CSV Name, 默认不保存
        :return: 明细表以及CSI值 res, CSI
        """
        expected.dropna(inplace=True)
        actual.dropna(inplace=True)

        expectedMax = expected.max()
        expectedMin = expected.min()
        actualMax = actual.max()
        actualMin = actual.min()

        if not pd.api.types.is_numeric_dtype(expected):
            raise Exception(TypeError, 'expected must be numeric!')

        if not pd.api.types.is_numeric_dtype(actual):
            raise Exception(TypeError, 'actual must be numeric!')

        if (expectedMax == expectedMin) or (actualMax == actualMin):
            raise Exception()

        if (expectedMin > actualMin) or (expectedMax < actualMax):
            raise Exception()

        if binType == 'distance':
            cutoffPoint = self._cutoffPoint(
                bins=bins, min=expectedMin, max=expectedMax)
        elif binType == 'frequency':
            cutoffPoint = self._cutoffPoint(
                bins=bins, percent=True, expected=expected)
        elif binType == 'customize' and cutPoint:
            cutoffPoint = cutPoint
        else:
            raise Exception(TypeError, '分箱错误!')

        res = pd.DataFrame({
            'Expected': pd.cut(expected, cutoffPoint).value_counts(sort=False),
            'Actual': pd.cut(actual, cutoffPoint).value_counts(sort=False),
        },)

        return self._csi(res)

    def Category(self, expected, actual):
        """
        Des: 类别型变量的CSI
        :param expected:
        :param actual:
        :return: 明细表以及CSI值 res, CSI
        """
        if (not pd.api.types.is_string_dtype(expected)) or (not pd.api.types.is_object_dtype(expected)):
            raise Exception(TypeError, 'expected must be string or object!')
        if (not pd.api.types.is_string_dtype(actual)) or (not pd.api.types.is_object_dtype(actual)):
            raise Exception(TypeError, 'actual must be string or object!')

        expected.dropna(inplace=True)
        actual.dropna(inplace=True)

        expectedGroup = expected.value_counts(sort=False)
        actualGroup = actual.value_counts(sort=False)

        res = pd.merge(
            pd.DataFrame({'category': expectedGroup.index, 'Expected': expectedGroup.values}),
            pd.DataFrame({'category': actualGroup.index, 'Actual': actualGroup.values}),
            on='category',
            how='outer',)

        self.res, self.csi = self._csi(res)
        return self.res, self.csi
