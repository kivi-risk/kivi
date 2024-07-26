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

    def test_create_dataset(self):
        make_data = MakeData()
        data = make_data.dataset()
        print("train", data.x_train.shape, data.y_train.shape)
        print("test", data.x_test.shape, data.y_test.shape)
        df_train, df_test = make_data.sample()
        print(df_train.shape, df_test.shape)
