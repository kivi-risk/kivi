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

    def test_score(self):
        """"""
        batch = WOEBatch(self.df_bank, verbose=False)
        self.df_woe = batch.woe_batch_with_rebin()

        woe_score = WOEScore(df=self.df_bank, df_woe=self.df_woe, batch_size=3, verbose=True)
        df_score = woe_score.batch_run()
        print(df_score.shape)
        print(df_score)

    def test_na_data(self):
        """检查分箱赋分在OOT中发现缺失值，但WOE中未发现相应分箱的情况"""
        batch = WOEBatch(self.df_bank, rebin=False, verbose=True)
        self.df_woe = batch.woe_batch()

        self.df_bank.at[10, "age"] = np.nan
        woe_score = WOEScore(df=self.df_bank, df_woe=self.df_woe, batch_size=3, verbose=True)
        # df_score = woe_score.batch_run()
        # print(df_score.shape)
        # print(df_score)


