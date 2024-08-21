import unittest
import numpy as np
import pandas as pd
from kivi.evaluate.psi import PSI


class TestPSI(unittest.TestCase):
    """"""
    def test_qcut(self):
        """等频分箱"""
        psi = PSI(
            pd.Series(np.random.randint(0, 100, size=1000)),
            pd.Series(np.random.randint(0, 100, size=1000)),
            cut_type="qcut", bins=5
        )
        df_psi = psi.fit()
        print(df_psi.to_markdown())

    def test_cut(self):
        """等距"""
        psi = PSI(
            pd.Series(np.random.randint(0, 100, size=1000)),
            pd.Series(np.random.randint(0, 100, size=1000)),
            cut_type="cut", bins=5, _max=100, _min=0
        )
        df_psi = psi.fit()
        print(df_psi.to_markdown())

    def test_cut_na(self):
        """存在空值"""
        psi = PSI(
            pd.Series(np.random.randint(0, 100, size=1000)),
            pd.Series(np.random.randint(0, 20, size=1000)),
            cut_type="cut", bins=5, _max=80, _min=0,
        )
        df_psi = psi.fit()
        print(df_psi.to_markdown())

    def test_cut_abnormal(self):
        """存在空值"""
        psi = PSI(
            pd.Series(np.random.randint(0, 100, size=1000)),
            pd.Series(np.random.randint(0, 100, size=1000)),
            cut_type="cut", bins=5, _max=100, _min=0, abnormal_vals=[7, 8]
        )
        df_psi = psi.fit()
        print(df_psi.to_markdown())

    def test_cut_cate(self):
        """存在空值"""
        cate = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
        psi = PSI(
            pd.Series(np.random.choice(cate, size=1000)),
            pd.Series(np.random.choice(cate, size=1000)),
        )
        df_psi = psi.fit()
        print(df_psi.to_markdown())

