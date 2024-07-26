import unittest
import pandas as pd
from kivi.ahp import AHP


class TestAHP(unittest.TestCase):
    """"""
    def setUp(self):
        """"""
        self.metrix = pd.read_excel("../../tutorials/ahp.xlsx", sheet_name="metrix")
        self.schema = pd.read_excel("../../tutorials/ahp.xlsx", sheet_name="schema")

    def test_ahp(self):
        ahp = AHP(metrix=self.metrix)
        ahp.solve_metrix()
        for group, weight in ahp.metrix_weight.items():
            print(group)
            print(weight)

    def test_weight(self):
        """"""
        ahp = AHP(metrix=self.metrix)
        ahp.solve_metrix()
        df_weight = ahp.weight()
        print(df_weight)
