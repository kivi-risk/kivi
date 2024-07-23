import unittest
import numpy as np
from kivi.evaluate import BinaryMetrics


class TestBinaryMetrics(unittest.TestCase):
    def setUp(self):
        """"""
        self.target = np.random.randint(0, 2, size=100)
        self.proba = np.random.random(size=100)                          # 预测概率
        self.prediction = (self.proba > self.target.mean()).astype(int)  # 预测值

    def test_binary_metrics(self):
        """"""
        binary_metrics = BinaryMetrics(self.target, self.proba, self.prediction)
        metrics = binary_metrics.evaluate()
        metrics.show()

    def test_plot_roc(self):
        """"""
        binary_metrics = BinaryMetrics(self.target, self.proba, self.prediction)
        metrics = binary_metrics.evaluate()
        binary_metrics.plot_roc()

    def test_plot_pr(self):
        """"""
        binary_metrics = BinaryMetrics(self.target, self.proba, self.prediction)
        metrics = binary_metrics.evaluate()
        binary_metrics.plot_pr()

    def test_plot_confusion_matrix(self):
        """"""
        binary_metrics = BinaryMetrics(self.target, self.proba, self.prediction)
        metrics = binary_metrics.evaluate()
        binary_metrics.plot_confusion_matrix()
        binary_metrics.plot_confusion_matrix(normalized=True)

