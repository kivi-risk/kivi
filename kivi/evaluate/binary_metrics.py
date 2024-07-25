import numpy as np
import pandas as pd
import seaborn as sns
from typing import Any, List, Union, Sequence, Optional
import matplotlib.pyplot as plt
from scipy.stats import ks_2samp, t
from sklearn.feature_selection import chi2
from sklearn.metrics import (
    roc_auc_score, roc_curve, recall_score, precision_score, confusion_matrix, f1_score,
    precision_recall_curve
)
from .schema import *
from .utils import lift


__all__ = [
    'ks_test',
    "KSValue",
    'Chi2',
    'BinaryMetrics',
    'p_value',
    "BinaryMetrics",
]


def ks_test(feature, target):
    """ """
    try:
        return ks_2samp(feature[target == 1], feature[target == 0])
    except:
        return [-1, -1]


def KSValue(variables, target):
    """
    Des: 计算KS值，计算KS-test的P-value
    :param variables:
    :param target:
    :return: ks_value, p_value
    """
    from scipy.stats import ks_2samp
    get_ks = lambda variables, target: ks_2samp(variables[target == 1], variables[target == 0])
    ks_value, p_value = get_ks(variables, target)
    return ks_value, p_value


def Chi2(X, y):
    """ """
    try:
        chi_statistic, chi_pvalue = chi2(X, y)
        return float(chi_statistic[0]), float(chi_pvalue[0])
    except:
        return -1, -1


class BinaryMetrics:
    metrics_output: BinaryMetricsOutput

    def __init__(
            self,
            target: Sequence,
            proba: Optional[Sequence] = None,
            prediction: Optional[Sequence] = None,
            score: Optional[Sequence] = None,
            **kwargs: Any,
    ):
        """
        :param target: 真实标签
        :param proba: 预测概率
        :param prediction: 预测标签
        :param score: 预测得分
        :param kwargs: 其他参数
        """
        self.target = target
        self.proba = proba
        self.prediction = prediction
        self.score = score
        self.metrics_output = BinaryMetricsOutput()
        self.kwargs = kwargs
        self.metrics_method = []
        self._validate_data()

    def _validate_data(self):
        """"""
        value_length = [len(item) for item in [self.target, self.proba, self.prediction, self.score] if item is not None]
        if value_length[0] == 0 or len(set(value_length)) > 1:
            raise ValueError("All input data must have the same length")

        if self.prediction is None and self.proba is None:
            raise ValueError("Either prediction or proba must be provided")
        if self.proba is not None:
            self.metrics_method.extend([
                "auc", "roc_curve",
            ])
        if self.prediction is not None:
            self.metrics_method.extend([
                "recall", "f1_score", "precision", "pr_curve",
                "confusion_matrix",
            ])

    def auc(self):
        """"""
        self.metrics_output.auc = roc_auc_score(y_true=self.target, y_score=self.proba)

    def roc_curve(self):
        """"""
        fpr, tpr, thresholds = roc_curve(y_true=self.target, y_score=self.proba)
        _roc_curve = ROCCurveOutput(fpr=fpr.tolist(), tpr=tpr.tolist(), thresholds=thresholds)
        self.metrics_output.roc_curve = _roc_curve
        self.metrics_output.ks = float(abs(fpr - tpr).max())

    def pr_curve(self):
        """"""
        precision, recall, thresholds = precision_recall_curve(y_true=self.target, probas_pred=self.proba)
        _pr_curve = PrecisionRecallCurveOutput(
            precision=precision.tolist(), recall=recall.tolist(), thresholds=thresholds)
        self.metrics_output.pr_curve = _pr_curve

    def recall(self):
        """"""
        self.metrics_output.recall = recall_score(y_true=self.target, y_pred=self.prediction)

    def f1_score(self):
        """"""
        self.metrics_output.f1_score = f1_score(y_true=self.target, y_pred=self.prediction)

    def precision(self):
        """"""
        self.metrics_output.precision = precision_score(y_true=self.target, y_pred=self.prediction)
        self.metrics_output.lift = float(self.metrics_output.precision / np.array(self.target).mean())

    def confusion_matrix(self):
        """"""
        tn, fp, fn, tp = confusion_matrix(y_true=self.target, y_pred=self.prediction).ravel()
        self.metrics_output.confusion_matrix = ConfusionMatrixOutput(tn=tn, fp=fp, fn=fn, tp=tp)

    def evaluate(self) -> BinaryMetricsOutput:
        """"""
        for metrics in self.metrics_method:
            getattr(self, metrics)()
        return self.metrics_output

    def plot_roc(self):
        """ Des: 绘制roc图 """
        if self.metrics_output.roc_curve is None or self.metrics_output.auc is None:
            raise ValueError('auc/roc is None, please run evaluate first')

        max_idx = np.argmax(abs(np.array(self.metrics_output.roc_curve.tpr) - np.array(self.metrics_output.roc_curve.fpr)))

        plt.plot(
            self.metrics_output.roc_curve.fpr, self.metrics_output.roc_curve.tpr,
            color='darkorange', lw=2, label=f'ROC curve (area = {self.metrics_output.auc:.2f}, ks = {self.metrics_output.ks:.2f})')
        plt.scatter(
            self.metrics_output.roc_curve.fpr[max_idx],
            self.metrics_output.roc_curve.tpr[max_idx],
            alpha=0.7, marker='*', s=50, color='tab:red', label=r'$ks\ max\ point$'
        ).set_zorder(10)

        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.0])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Receiver operating characteristic')
        plt.legend(loc="lower right")
        plt.show()

    def plot_pr(self):
        """
        Des: 绘制pr图
        :return: None
        """
        if self.metrics_output.pr_curve is None or self.metrics_output.auc is None:
            raise ValueError('auc/pr is None, please run evaluate first')
        plt.plot(
            self.metrics_output.pr_curve.recall,
            self.metrics_output.pr_curve.precision, color='darkorange',
            lw=2, label=f'PR curve (area = {self.metrics_output.auc:.2f})')
        plt.plot([0, 1], [1, 0], color='navy', lw=2, linestyle='--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.0])
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title('Precision-Recall Curve')
        plt.legend(loc="lower right")
        plt.show()

    def plot_confusion_matrix(self, normalized=False):
        """
        Des: 绘制混淆矩阵图
        :param normalized: 是否归一化，默认为False
        """
        if self.metrics_output.confusion_matrix is None:
            raise ValueError("Please call evaluate() first")

        matrix = np.array([
            [self.metrics_output.confusion_matrix.tp, self.metrics_output.confusion_matrix.fp],
            [self.metrics_output.confusion_matrix.fn, self.metrics_output.confusion_matrix.tn],
        ])

        if normalized:
            matrix = (matrix - matrix.min()) / (matrix.max() - matrix.min())
        ax = sns.heatmap(matrix, annot=True, cmap="YlGnBu")
        ax.set_xlabel('True label')
        ax.set_xticklabels(["P", "N"])
        ax.set_ylabel('Predicted label')
        ax.set_yticklabels(["P", "N"])
        ax.set_title('Confusion matrix')
        plt.show()

    def plot_score(self, **kwargs):
        """"""
        """"""
        if self.score is None:
            raise ValueError("Score is None.")

        sns.set_style("whitegrid")
        fig, axs = plt.subplots()
        good_score = self.score[self.target == 0]
        bad_score = self.score[self.target == 1]
        with sns.color_palette("muted", n_colors=2):
            sns.histplot(good_score, label="good", kde=True, stat="percent", **kwargs)
            sns.histplot(bad_score, label="bad", kde=True, stat="percent", **kwargs)
        axs.legend()
        axs.set_title(r"$Score\ Distribution$")
        axs.set_xlabel('$Score$')
        axs.set_ylabel('$Percent$')
        plt.show()

    def plot_ks(
            self,
            bins: Optional[Union[int, List[Union[int, float]]]] = 40,
            show_bucket: Optional[bool] = False,
    ):
        """"""
        df_score = pd.DataFrame({"score": self.score, "target": self.target})
        df_lift = lift(df_score, bins=bins)
        x = range(len(df_lift.index.tolist()))
        mark_line_good = df_lift.loc[df_lift.ks == df_lift.ks.max(), "cum_good"].values[0]
        mark_line_bad = df_lift.loc[df_lift.ks == df_lift.ks.max(), "cum_bad"].values[0]

        fig, axs = plt.subplots()
        axs.plot(x, df_lift.ks * 100, marker='o', ms=2, linewidth=1.5, c='tab:blue', label="ks")
        axs.plot(x, df_lift.cum_good * 100, marker='o', ms=2, linewidth=1.5, c='tab:green', label="cum_good")
        axs.plot(x, df_lift.cum_bad * 100, marker='o', ms=2, linewidth=1.5, c='tab:red', label="cum_bad")

        axs.axvline(x=np.argmax(df_lift.ks.to_list()), linestyle='--', linewidth=0.7, alpha=0.5, c='gray')
        axs.axhline(y=df_lift.ks.max() * 100, linestyle='--', linewidth=0.7, alpha=0.5, c='tab:blue')
        axs.axhline(y=mark_line_good * 100, linestyle='--', linewidth=0.7, alpha=0.5, c='tab:green')
        axs.axhline(y=mark_line_bad * 100, linestyle='--', linewidth=0.7, alpha=0.5, c='tab:red')

        axs.set_title(f'KS = {df_lift.ks.max(): .2f} at {bins} bucket')
        axs.legend()
        axs.set_xlabel("buckets")
        axs.set_ylabel(r'$Rate(\%)$')
        if show_bucket:
            axs.set_xticks(range(len(df_lift.index)))
            axs.set_xticklabels(df_lift.index.tolist(), rotation=90)
        plt.tight_layout()
        plt.show()


def p_value(params, x, y, predict):
    """ 描述：计算广义线性回归 std_error t_value p_vale """
    x = np.hstack([np.ones(len(x), 1), x])
    n_degree = (y.shape[0] - x.shape[1])

    mse = sum((y - predict) ** 2) / n_degree
    var_error = mse * np.linalg.inv(np.dot(x.T, x)).diagonal()
    std_error = np.sqrt(var_error)
    t_values = params / std_error
    p_values = 2 * (1 - t.cdf(np.abs(t_values), n_degree))

    return pd.DataFrame({
        'params': params,
        'std_error': std_error,
        't_values': t_values,
        'p_values': p_values,
    })
