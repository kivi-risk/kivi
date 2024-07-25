import unittest
import numpy as np
from kivi.evaluate import *
from kivi.datasets import MakeData
from kivi.woe import *


class TestBinaryMetrics(unittest.TestCase):
    def setUp(self):
        """"""
        make_data = MakeData()
        train, test = make_data.sample()

        # WOE
        batch = WOEBatch(train, verbose=False)
        df_woe = batch.woe_batch()
        woe_score = WOEScore(df=train, df_woe=df_woe, batch_size=2, verbose=False)
        self.train = woe_score.batch_run()
        woe_score = WOEScore(df=test, df_woe=df_woe, batch_size=2, verbose=False)
        self.test = woe_score.batch_run()
        self.samples = [self.train, self.test]

        # EVALUATE
        model_eval = ModelEvaluate(samples=self.samples, bins=10, verbose=False)
        model_eval.evaluate()

        df_score = model_eval.scores[0]
        self.target = df_score.target
        self.proba = df_score.proba
        self.score = df_score.score
        self.prediction = df_score.prediction

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

    def test_plot_score(self):
        """"""
        binary_metrics = BinaryMetrics(self.target, self.proba, self.prediction, score=self.score)
        metrics = binary_metrics.evaluate()
        binary_metrics.plot_score()

    def test_plot_ks(self):
        """"""
        binary_metrics = BinaryMetrics(self.target, self.proba, self.prediction, score=self.score)
        metrics = binary_metrics.evaluate()
        binary_metrics.plot_ks()
