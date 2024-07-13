import numpy as np
import pandas as pd
import logging
from .utils import BetaDistribution


def get_omega(
        now_y: pd.Series = None,
        previous_y: pd.Series = None,
        tau=None,
):
    """
    获取ODD校准的omega值，给定采样前后的样本，或者给定tau概率
    :param now_y:
    :param previous_y:
    :param tau:
    :return:
    """
    if previous_y is not None:
        tau = sum(previous_y) / len(previous_y)
    if now_y is not None:
        y_ratio = sum(now_y) / len(now_y)
    omega = (tau / (1-tau)) * ((1 - y_ratio) / y_ratio)
    return omega


def calibration(X, coef, intercept, omega):
    """
    概率校准
    :param X: DataSet
    :param coef: 截距
    :param intercept: 斜率
    :param omega: omega 参数
    :return: 校准后的pd
    """
    calibration_pd = 1 / (1 + np.e ** (- intercept - np.log(omega) - np.dot(X, coef)))
    return calibration_pd

class BetaCalibration(BetaDistribution):
    """
    基本步骤:
        1. 确定各个评级占比及对应的得分区间；
        2. 统计落入各个评级的客户数及违约数；
        3. 二项检验；
        4. 计算校准后的实际违约率。
    """
    def __init__(
            self,
            Alpha: float,
            Beta: float,
            target_grade: int,
            alpha: float = 0.05):
        super(BetaCalibration, self).__init__(Alpha, Beta)
        self.alpha = alpha
        self.target_grade = target_grade

        self.target_grade_rate, self.CDF = self.grade_rate(self.target_grade)
        self.arange = np.arange(1, target_grade+1, 1)
        self.calibration_distritution = pd.DataFrame({
            'rating': self.arange,
            'percentile': [f'{i}/{target_grade}'for i in self.arange],
            'accum_dis': self.target_grade_rate,
            'distribution': self.CDF,
        })


    def score_to_rank(self, predict_default=None, score=None):
        """
        得分映射区间
        :return:
        """
        if predict_default is not None:
            # 计算 Beta 分布下分位点的 PD 值
            self.quantile = [np.quantile(predict_default, cdf) for cdf in self.CDF]
        if score is not None:
            # 计算 Beta 分布下分位点的 Score 值
            self.quantile = [np.quantile(score, cdf) for cdf in self.CDF]
        self.quantile.insert(0, 0)
        if len(np.unique(self.quantile)) != len(self.quantile):
            logging.error('等级过细，存在相同数值截断点！')

    def count_default(self, target, predict_default=None, score=None, right=True):
        """

        :param target:
        :param predict_default:
        :param score:
        :param right:
        :return:
        """
        if predict_default is not None:
            pass
        if score is not None:

            buckets = pd.DataFrame({
                'score': score,
                'target': target,
                'bucket': pd.cut(score, self.quantile, include_lowest=True, right=right, duplicates='drop')
            }).groupby('bucket', as_index=True)

            # 校准后分布
            self.real_data_distribution = pd.DataFrame({
                'rating': self.arange,
                'bin_samples': buckets.target.count(),
                'default_count': buckets.target.sum()
            })

    def to_rank(self, predict_default: float, grade: list):
        """
        PD 到主标尺等级的映射
        :param pd: 预测PD
        :param ranking: 主标尺分箱的max bin
        :return: 等级
        """
        return sum(np.array(grade) <= predict_default) - 1

    def binomial_test(self, ):
        # ranking = [ for ]
        # bt = BinomialTest(ranking=, target=, proba=)
        # bt.binomial_boundary()
        # return
        return None


if __name__ == '__main__':
    np.random.seed(1)
    ranking = np.random.randint(0, 100, size=100)
    target = np.random.binomial(1, 0.3, size=100)
    bc = BetaCalibration(2.65, 2.95, 19, ranking, target, proba)
    print(bc.target_grade_rate, bc.CDF)
    # 根据 score predict_default 找截断点
    print(bc.score_to_rank(score=ranking))
    bc.count_default(target=target, score=ranking)
