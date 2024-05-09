

import pandas as pd
import numpy as np
from scipy.stats import ks_2samp, t
import matplotlib.pyplot as plt
from sklearn.feature_selection import chi2
from sklearn.metrics import roc_auc_score, roc_curve, recall_score, confusion_matrix

def KSTest(feature, target):
    """

    :param feature:
    :param target:
    :return:
    """
    try:
        return ks_2samp(feature[target == 1], feature[target == 0])
    except:
        return [-1, -1]

def Chi2(X, y):
    """

    :param X:
    :param y:
    :return:
    """
    try:
        chi_statistic, chi_pvalue = chi2(X, y)
        return float(chi_statistic), float(chi_pvalue)
    except:
        return -1, -1

def RocAucKs(true, predict, predict_binary=None):
    """

    :param true:
    :param predict:
    :return:
    """
    metrics_info = dict()
    fpr, tpr, _ = roc_curve(true, predict)
    ks = abs(fpr - tpr).max()

    metrics_info.update({
        'fpr': fpr,
        'tpr': tpr,
        'auc': roc_auc_score(true, predict),
        'ks': ks,})

    if predict_binary:
        metrics_info.update({'recall': recall_score(true, predict_binary)})

    return metrics_info

class ConfusionMatrix:

    def __init__(self):
        """
        Des: 计算混淆矩阵
        """
        pass

    def __call__(self, *args, **kwargs):
        pass

    def matrix(self, y_true, y_pred, labels=None, suffixes=('true_', 'pre_')):
        """
        Des: 计算混淆矩阵
        :param y_true: 真实值
        :param y_pred: 预测值
        :param labels: [none][list]标签名称
        :param suffixes: [None][tuple]对columns和index的补充
        :return: DataFrame
        """
        if not labels:
            labels = np.sort(np.unique(np.array(y_true)))
        if suffixes:
            cols = [suffixes[1] + str(item) for item in labels]
            ins = [suffixes[0] + str(item) for item in labels]
        else:
            cols = ins = labels
        return pd.DataFrame(
            confusion_matrix(y_true, y_pred),
            columns=cols,
            index=ins,
        )

    def plot_matrix(self, matrix, normalized=False):
        """
        Des: 绘制混淆矩阵图
        :param matrix: 混淆矩阵
        :param normalized: 是否归一化，默认为False
        :return: axis
        """
        if normalized:
            matrix = (matrix - matrix.min()) / (matrix.max() - matrix.min())
            matrix.fillna(0, inplace=True)
        import seaborn as sns
        ax = sns.heatmap(matrix, annot=True, cmap="YlGnBu")
        ax.set_xlabel('Predicted label')
        ax.set_ylabel('True label')
        ax.set_title('Confusion matrix')
        return ax

class AucRoc:

    def __init__(self, y_true, y_pre):
        """
        Des: AucRoc 方法
        :param y_true: 真实值
        :param y_pre: 预测值
        """
        self.auc_area = roc_auc_score(y_true, y_pre)
        self.roc(y_true, y_pre)


    def roc(self, y_true, y_pre):
        """
        Des: 计算Roc
        :param y_true: 真实值
        :param y_pre: 预测值
        :return: None
        """
        self.fpr, self.tpr, self.thresholds = roc_curve(y_true, y_pre)

    def plot_roc(self):
        """
        Des: 绘制roc图
        :return: None
        """
        lw = 2
        plt.plot(self.fpr, self.tpr, color='darkorange',
                 lw=lw, label='ROC curve (area = %0.2f)' % self.auc_area)
        plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Receiver operating characteristic')
        plt.legend(loc="lower right")
        plt.show()

def Pvalue(params, X, y, predict):
    """
    描述：计算广义线性回归 std_error t_value p_vale

    参数：
    :param params:
    :param X:
    :param y:
    :param predict:
    :return:
    """
    X = np.hstack([np.ones(len(X), 1), X])
    n_degress = (y.shape[0] - X.shape[1])

    mse = sum((y - predict) ** 2) / n_degress
    var_error = mse * np.linalg.inv(np.dot(X.T, X)).diagonal()
    std_error = np.sqrt(var_error)
    t_values = params / std_error
    p_values = 2 * (1 - t.cdf(np.abs(t_values), n_degress))

    return pd.DataFrame({
        'params': params,
        'std_error': std_error,
        't_values': t_values,
        'p_values': p_values,
    })
