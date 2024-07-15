import unittest
import numpy as np
from kivi.woe import *
from kivi.datasets import *


class TestScore(unittest.TestCase):

    def setUp(self):
        """"""
        self.df_bank = Dataset.BankData()
        self.df_bank['uuid'] = np.arange(0, len(self.df_bank))

        batch = WOEBatch(self.df_bank, rebin=False, verbose=False)
        self.df_woe = batch.fit()

    def test_score(self):
        """"""
        bin_tool = ManualBinsTool(df=self.df_bank, verbose=True)

        # method: 不指定字段，自动对全部字段进行补充Nan
        df_woe = bin_tool.add_nan_bin(df_woe=self.df_woe)
        print(df_woe[df_woe.var_name == "age"].to_markdown())
        print(self.df_woe.shape, df_woe.shape, len(self.df_woe.var_name.unique()))

        # method: 指定字段进行补全Nan
        df_woe = bin_tool.add_nan_bin(df_woe=self.df_woe, columns=["age"])
        print(df_woe[df_woe.var_name == "age"].to_markdown())
        print(self.df_woe.shape, df_woe.shape)

        df_woe = bin_tool.add_nan_bin(df_woe=self.df_woe, columns=["duration"])
        print(df_woe[df_woe.var_name == "duration"].to_markdown())
        print(self.df_woe.shape, df_woe.shape)

        # method: 指定字段，并指定分数
        df_woe = bin_tool.add_nan_bin(df_woe=self.df_woe, columns={"age": 15, "duration": 30})
        print(df_woe[df_woe.var_name.isin(["age", "duration"])].to_markdown())
        print(self.df_woe.shape, df_woe.shape)
