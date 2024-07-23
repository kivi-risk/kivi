import unittest
from kivi.feature import *
from kivi.datasets import *


class VarTest(unittest.TestCase):
    """"""
    def setUp(self):
        """"""
        df_bank = Dataset.bank_data()
        self.df_bank = df_bank.select_dtypes(['int64', 'float64']).copy()

    def test_univar(self):
        """"""
        feature_eval = FeatureEvaluate(df=self.df_bank)
        df_ans = feature_eval.stats()
        print(df_ans.to_markdown())
