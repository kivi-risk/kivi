import unittest
import numpy as np
from kivi.datasets import Dataset
from kivi.woe import *


class TestWoeBatch(unittest.TestCase):

    def setUp(self):
        """"""
        self.df_bank = Dataset.BankData()
        self.df_bank['uuid'] = np.arange(0, len(self.df_bank))
        print(self.df_bank.shape)

    def test_batch(self):
        """"""
        batch = WOEBatch(self.df_bank, verbose=True)
        df_woe = batch.woe_batch()
        print(df_woe.shape)

    def test_woe_batch_with_rebin(self):
        """"""
        batch = WOEBatch(self.df_bank, verbose=False)
        df_woe = batch.woe_batch_with_rebin()
        print(df_woe.shape)
        print(df_woe)

    def test_woe_rebin_times(self):
        """"""
        batch = WOEBatch(self.df_bank, woe_type=TreeBins, max_bin=5, min_bin=2, rebin=True, verbose=True)
        df_woe = batch.fit()
        print(df_woe.to_markdown())

    def test_rebin_tools(self):
        rebin_tool = ManualBinsTool(df=self.df_bank)
        df_rebin_woe = rebin_tool.manual_rebin(column="age", bins=[-np.inf, 20, 22, 50, 70, np.inf])

    def test_rebin_append(self):
        batch = WOEBatch(self.df_bank, verbose=False)
        df_woe = batch.woe_batch_with_rebin()

        rebin_tool = ManualBinsTool(df=self.df_bank, verbose=False)
        df_rebin_woe = rebin_tool.manual_rebin(column="age", bins=[-np.inf, 20, 22, 50, 70, np.inf])

        print(df_woe[df_woe.var_name == "age"])
        df = rebin_tool.append_rebin_woe(df_woe=df_woe, df_rebin=df_rebin_woe)
        print(df[df.var_name == "age"])

