import unittest
import numpy as np
import pandas as pd
from pandas import DataFrame
from kivi.woe import *
from kivi.evaluate import *
from kivi.datasets import MakeData


class TestScoreEvaluate(unittest.TestCase):
    """"""
    def setUp(self):
        """"""
        self.scores = [self.create_sample() for i in range(3)]

    def create_sample(self) -> DataFrame:
        """"""
        df_sample = pd.DataFrame({
            "target": np.random.randint(0, 2, 100),
            "score": np.random.rand(100) * 100,
        })
        return df_sample

    def test_init(self):
        model_eval = ScoreEvaluate(scores=self.scores, bins=10, border=(0, 100))
        df_eval = model_eval.score_evaluate()
        print(df_eval)

    def test_psi(self):
        """"""
        model_eval = ScoreEvaluate(scores=self.scores, bins=10, border=(0, 100))
        df_eval = model_eval.score_evaluate()
        df_psi = model_eval.score_psi()
        print(df_psi)

    def test_add_psi(self):
        """"""
        model_eval = ScoreEvaluate(scores=self.scores, bins=10, border=(0, 100))
        df_eval = model_eval.score_evaluate()
        df_psi = model_eval.add_psi()
        print(df_psi)


class TestModelEvaluate(unittest.TestCase):
    """"""
    def setUp(self):
        make_data = MakeData()
        train, test = make_data.sample()

        batch = WOEBatch(train, verbose=False)
        df_woe = batch.woe_batch()

        woe_score = WOEScore(df=train, df_woe=df_woe, batch_size=2, verbose=False)
        self.train = woe_score.batch_run()
        woe_score = WOEScore(df=test, df_woe=df_woe, batch_size=2, verbose=False)
        self.test = woe_score.batch_run()
        self.samples = [self.train, self.test]

    def test_concat(self):
        """"""
        model_eval = ModelEvaluate(samples=self.samples, bins=10, verbose=True)
        model_eval.evaluate()
        print(model_eval.df_lifts.to_markdown())

    def test_plot_score(self):
        """"""
        model_eval = ModelEvaluate(samples=self.samples, bins=10, verbose=True)
        model_eval.evaluate()
