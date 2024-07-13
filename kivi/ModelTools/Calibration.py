

import numpy as np
import os

from sklearn.preprocessing import label_binarize
from sklearn.utils import column_or_1d, check_consistent_length
from numpy import log
from pandas import cut, DataFrame, merge, Series
from pandas.api.types import is_numeric_dtype, is_object_dtype
from ..utils import saveCsv, Bins


class Calibration:
    def __init__(self, imageName=None):
        self.imageName = imageName

    def CalibrationCurve(self, y_true, y_prob, normalize=False, n_bins=5,
                         strategy='uniform'):
        """计算校正曲线(Calibration curve)的真实和预测概率。
            该方法假定输入来自二进制分类器。
            校准曲线也可以称为可靠性图(reliability diagrams)。

        参数
        ----------
        y_true : array, shape (n_samples,)
            True targets.
        y_prob : array, shape (n_samples,)
            Probabilities of the positive class.
        normalize : bool, optional, default=False
            是否需要将y_prob归一化为bin [0，1]，不是适当的概率。
            如果为True，则y_prob中的最小值映射到0，最大的映射到1。
        n_bins : int
            分箱数。更大的数量需要更多的数据。没有数据点的bin（即y_prob中没有相应的值）将不会返回，
            因此返回值中的n_bins可能少于n_bins。
        strategy : {'uniform', 'quantile'}, (default='uniform')
            uniform: 等距
            quantile: 等频
        返回值
        -------
        prob_true : array, shape (n_bins,) or smaller
            每个分箱中的真实概率 (fraction of positives).
        prob_pred : array, shape (n_bins,) or smaller
            每个分箱中的平均预测概率。
        """

        y_true = column_or_1d(y_true)
        y_prob = column_or_1d(y_prob)
        check_consistent_length(y_true, y_prob)

        if normalize:  # Normalize predicted values into interval [0, 1]
            y_prob = (y_prob - y_prob.min()) / (y_prob.max() - y_prob.min())
        elif y_prob.min() < 0 or y_prob.max() > 1:
            raise ValueError(
                "y_prob has values outside [0, 1] and normalize is "
                "set to False.")

        labels = np.unique(y_true)
        if len(labels) > 2:
            raise ValueError("Only binary classification is supported. "
                             "Provided labels %s." % labels)
        y_true = label_binarize(y_true, labels)[:, 0]

        if strategy == 'quantile':  # Determine bin edges by distribution of data
            quantiles = np.linspace(0, 1, n_bins + 1)
            bins = np.percentile(y_prob, quantiles * 100)
            bins[-1] = bins[-1] + 1e-8
        elif strategy == 'uniform':
            bins = np.linspace(0., 1. + 1e-8, n_bins + 1)
        else:
            raise ValueError("Invalid entry to 'strategy' input. Strategy "
                             "must be either 'quantile' or 'uniform'.")

        binids = np.digitize(y_prob, bins) - 1

        bin_sums = np.bincount(binids, weights=y_prob, minlength=len(bins))
        bin_true = np.bincount(binids, weights=y_true, minlength=len(bins))
        bin_total = np.bincount(binids, minlength=len(bins))

        nonzero = bin_total != 0
        prob_true = (bin_true[nonzero] / bin_total[nonzero])
        prob_pred = (bin_sums[nonzero] / bin_total[nonzero])

        return prob_true, prob_pred

    def Plot(self, y_true, predictLs, bins=10, normalize=False,
             strategy='uniform', **kwargs):
        """
        Des: 绘制概率校准曲线
        :param y_true: 真实标签
        :param predictLs: [(name, predict), (name, predict), ……]
        :param bins: 分箱数
        :param normalize : bool, optional, default=False
            是否需要将y_prob归一化为bin [0，1]，不是适当的概率。
            如果为True，则y_prob中的最小值映射到0，最大的映射到1。
        :param strategy : {'uniform', 'quantile'}, (default='uniform')
            uniform: 等距
            quantile: 等频
        :param kwargs: 图像参数['style', 'figsize', 'dpi', 'labelfontsize', title, 'x_label', 'y_label'……]
        :return: None
        """

        kwargs.setdefault('style', 'seaborn')
        kwargs.setdefault('figsize', (10, 10))
        kwargs.setdefault('dpi', 150)
        kwargs.setdefault('labelfontsize', 10)
        kwargs.setdefault('tickfontsize', 8)
        kwargs.setdefault('titlefontsize', 12)
        kwargs.setdefault('x_label', 'Mean predicted value')
        kwargs.setdefault('y_label', "Fraction of positives")
        kwargs.setdefault('title', 'Calibration plots  (reliability curve)')

        import matplotlib.pyplot as plt

        plt.figure(figsize=kwargs.get('figsize'), dpi=kwargs.get('dpi'))
        ax1 = plt.subplot2grid((3, 1), (0, 0), rowspan=2)
        ax2 = plt.subplot2grid((3, 1), (2, 0))

        ax1.plot([0, 1], [0, 1], "k:", label="Perfectly calibrated")
        for name, predict in predictLs:
            fraction_of_positives, mean_predicted_value = self.CalibrationCurve(
                y_true,
                predict,
                n_bins=bins,
                normalize=normalize,
                strategy=strategy,
            )

            ax1.plot(mean_predicted_value, fraction_of_positives, "s-",
                     label="%s" % (name,))

            ax2.hist(predict, range=(0, 1), bins=10, label=name,
                     histtype="step", lw=2)

        ax1.set_ylabel(kwargs.get('y_label'))
        ax1.set_ylim([-0.05, 1.05])
        ax1.legend(loc="lower right")
        ax1.set_title(kwargs.get('title'))

        ax2.set_xlabel(kwargs.get('x_label'))
        ax2.set_ylabel("Count")
        ax2.legend(loc="upper center", ncol=2)

        plt.tight_layout()

        if self.imageName:
            if not os.path.exists('img'):
                os.mkdir('img')
            plt.savefig(f'./img/{self.imageName}_calibration.png', )
            return None
        else:
            return plt.show()

class ODDS(Bins):

    def __init__(self, csvName=None):
        """
        Des: 计算PSI
        :param margin: cutoff point 左右填充预留边界
        :param csvName: 结果保存的csv文件名称（如果需要保存的话）
        """
        super(ODDS, self).__init__()
        self.csvName = csvName

    def _odds(self, res):
        """
        Des: 计算PSI的核心函数
        :param res: 明细表
        :return: 明细表以及PSI值 res, psi
        """

        res['Expected_percentage'] = res.Expected / res.Expected.sum()
        res['target_percentage'] = res.target / res.target.sum()
        res['A-E'] = res.target_percentage - res.Expected_percentage
        res['A/E'] = res.target_percentage / res.Expected_percentage
        res['ln(A/E)'] = log(res['A/E'])
        res['index'] = res['A/E'] * res['ln(A/E)']
        psi = res['index'].sum()
        return res, psi

    def odds(self, score, target, bins=10, binType='distance', cutPoint=None):
        """
        Des: 连续型变量的PSI指标
        :param score: 预期分布
        :param target: 实际分布
        :param bins: 分箱数目
        :param binType: 分箱类型 'distance'等距 or 'frequency'等频 or 'customize'自定义
        :param csvName: 保存CSV Name, 默认不保存
        :return: 明细表以及PSI值 res, PSI
        """
        score.dropna(inplace=True)
        target.dropna(inplace=True)

        scoreMax = score.max()
        scoreMin = score.min()

        if not is_numeric_dtype(score):
            raise Exception(TypeError, 'score must be numeric!')

        if not is_numeric_dtype(target):
            raise Exception(TypeError, 'target must be numeric!')

        if binType == 'distance':
            cutoffPoint = self._cutoffPoint(
                bins=bins, min=scoreMin, max=scoreMax)
        elif binType == 'frequency':
            cutoffPoint = self._cutoffPoint(
                bins=bins, percent=True, score=score)
        elif binType == 'customize' and cutPoint:
            cutoffPoint = cutPoint
        else:
            raise Exception(TypeError, '分箱错误!')

        total, bad = target.count(), target.sum()
        good = total - bad

        Bucket = DataFrame({
            'score': score,
            'target': target,
            'bucket': cut(score, cutoffPoint, )
        }).groupby('bucket', as_index=True)

        res = DataFrame({
            'min_bin': Bucket.score.min(),
            'max_bin': Bucket.score.max(),
            'total': Bucket.target.count(),
            'bad': Bucket.target.sum(),
        })

        res['good'] = res.total - res.bad
        res['odd_bad/good'] = res.bad / res.good
        res['bad_rate'] = res['bad'] / res['total']  # 每个箱体中好样本所占总样本数的比例
        res['Ln(Odds)'] = log(res['odd_bad/good'])
        return res



        self.res, self.psi = self._odds(res)

        if self.csvName:
            saveCsv(res, self.csvName)
            return self.psi
        else:
            return self.res, self.psi
