import unittest
import numpy as np
import pandas as pd
from kivi.woe import *
from kivi.datasets import *
from kivi.utils.operator import *
from kivi.ModelEval import *


class TestWOE(unittest.TestCase):
    """"""
    def setUp(self):
        """"""
        self.df_bank = Dataset.BankData()
        print(self.df_bank.shape)

    def test_distance_bins(self):
        """"""
        bins = DistanceBins(self.df_bank.age, self.df_bank.target, bins=5)
        df_woe = bins.fit(score=True, origin_border=False)
        print(df_woe.to_markdown())

    def test_frequency_bins(self):
        """"""
        bins = FrequencyBins(self.df_bank.age, self.df_bank.target, bins=5)
        df_woe = bins.fit(score=True, origin_border=False)
        print(df_woe.to_markdown())

    def test_category_bins(self):
        """"""
        bins = CategoryBins(self.df_bank.job, self.df_bank.target, bins=5)
        df_woe = bins.fit(score=True, origin_border=False)
        print(df_woe.to_markdown())

    def test_kmeans_bins(self):
        """"""
        bins = KmeansBins(self.df_bank.age, self.df_bank.target, bins=5)
        df_woe = bins.fit()
        print(df_woe.to_markdown())

    def test_manually_bins(self):
        """"""
        manually = ManuallyBins(
            self.df_bank.age, self.df_bank.target, bins=[-np.inf, 20, 22, 50, 70, np.inf])
        df_woe = manually.fit()
        print(df_woe.to_markdown())

    def test_pearson_bins(self):
        """"""
        bins = PearsonBins(self.df_bank.age, self.df_bank.target, min_bin=3)
        df_woe = bins.fit()
        print(df_woe.to_markdown())

    def test_tree_bins(self):
        """
        """
        tree_bins = TreeBins(self.df_bank.age, self.df_bank.target, bins=5)
        df_woe = tree_bins.fit()
        print(df_woe.to_markdown())

    def test_ks_bins(self):
        """"""
        ks = KSBins(self.df_bank.age, self.df_bank.target, bins=5, )
        df_woe = ks.fit()
        print(df_woe.to_markdown())

    def test_chi2_bins(self):
        """
        """
        bins = Chi2Bins(
            self.df_bank.age, self.df_bank.target, init_bins=20, min_bins=5, max_bins=10,)
        df_woe = bins.fit()
        print(df_woe.to_markdown())


class TestWOEAbnormal(unittest.TestCase):
    """"""
    def setUp(self):
        """"""
        self.df_bank = Dataset.BankData()
        print(self.df_bank.shape)

    def test_tree_bins_abnormal(self):
        """
        """
        bins = TreeBins(self.df_bank.age, self.df_bank.target, bins=5, abnormal_vals=[19, 31])
        df_woe = bins.fit()
        print(df_woe.to_markdown())


class TestWOEWeight(unittest.TestCase):
    """"""
    def setUp(self):
        """"""

    def test_batch_woe(self):
        """"""
        df_data = pd.read_pickle('data/test_weight_bins_data.pkl')
        df_woe, fault_cols = WOEBatchWithRebin(
            df_data, drop_columns=['uuid', 'target', 'pd'],
            dtc_weight=df_data.pd, weight=df_data.pd)
