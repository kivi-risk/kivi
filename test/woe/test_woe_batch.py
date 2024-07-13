import unittest
import numpy as np
from kivi.datasets import Dataset
from kivi.woe.batch import *


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

