import unittest
import pandas as pd
from kivi.ahp import AHP


class TestAHP(unittest.TestCase):
    """"""
    def setUp(self):
        """"""
        self.metrix = pd.read_excel("../data/ahp.xlsx", sheet_name="metrix")
        self.schema = pd.read_excel("../data/ahp.xlsx", sheet_name="schema")

    def test_ahp(self):
        ahp = AHP(metrix=self.metrix)
        ahp.solve_metrix()
        print(ahp.metrix_weight.get("C1").to_markdown())
        print(ahp.group_ci)
        print(ahp.group_cr)

    def test_weight(self):
        """"""
        ahp = AHP(metrix=self.metrix)
        ahp.solve_metrix()
        df_weight = ahp.weight()
        print(df_weight.to_markdown())
