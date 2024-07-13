import unittest
import numpy as np
from kivi.woe import *
from kivi.datasets import *


class TestScore(unittest.TestCase):

    def setUp(self):
        """"""
        self.df_bank = Dataset.BankData()
        self.df_bank['uuid'] = np.arange(0, len(self.df_bank))
        print(self.df_bank.shape)

        batch = WOEBatch(self.df_bank, verbose=False)
        self.df_woe = batch.woe_batch_with_rebin()

    def test_score(self):
        woe_score = WOEScore(df=self.df_bank, df_woe=self.df_woe, batch_size=3, verbose=True)
        df_score = woe_score.batch_run()
        print(df_score.shape)
        print(df_score)
