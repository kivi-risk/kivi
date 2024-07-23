import unittest
from kivi.feature import *
from kivi.datasets import *


class TestStepwise(unittest.TestCase):
    """"""
    def setUp(self):
        """"""
        df_bank = Dataset.bank_data()
        self.df_bank = df_bank.select_dtypes(['int64', 'float64']).copy()
        self.dependent = FeatureEvaluate(df=self.df_bank).stats()

    def test_step_wize_forward(self):
        """"""
        step_wise = StepWise(df=self.df_bank, dependent=self.dependent, early_stop=0.05)
        forward_report = step_wise.forward()
        print(forward_report.to_markdown())

    def test_step_wize_backward(self):
        """"""
        step_wise = StepWise(df=self.df_bank, dependent=self.dependent, early_stop=-0.001)
        forward_report = step_wise.backward()
        print(forward_report.to_markdown())
