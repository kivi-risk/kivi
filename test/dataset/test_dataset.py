import unittest
from kivi.datasets import *


class TestDataset(unittest.TestCase):
    def test_bank(self):
        ds = Dataset()
        df_bank = ds.bank_data()
        print(df_bank.shape)

    def test_crime(self):
        ds = Dataset()
        df_crime = ds.crime_data()
        print(df_crime.shape)
