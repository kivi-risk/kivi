import unittest
from kivi.index.operator import *


class TestOperator(unittest.TestCase):
    """"""

    def test_operator(self, ):
        """"""
        amounts = [0]
        result = operator_growth_months(amounts)
        print(f"growth months is: {result}")

        amounts = [0, 1, 3]
        result = operator_growth_months(amounts)
        print(f"growth months is: {result}")

        amounts = [1, 0]
        result = operator_growth_months(amounts)
        print(f"growth months is: {result}")

        amounts = [1, 0, 2, 4, 7, 6]
        result = operator_growth_months(amounts)
        print(f"growth months is: {result}")

        amounts = [100, 120, 110, 130, 150, 160, 170, 180, 190, 200]
        result = operator_growth_months(amounts)
        print(f"growth months is: {result}")

    def test_operator_growth_months(self, ):
        """"""
        # amounts = [0]
        # result = operator_consecutive_growth_months(amounts)
        # print(f"growth months is: {result}")
        #
        # amounts = [0, 1, 3]
        # result = operator_consecutive_growth_months(amounts)
        # print(f"growth months is: {result}")
        #
        # amounts = [1, 0]
        # result = operator_consecutive_growth_months(amounts)
        # print(f"growth months is: {result}")

        amounts = [1, 0, 2, 4, 7, 6]
        result = operator_consecutive_growth_months(amounts)
        print(f"growth months is: {result}")

        amounts = [1, 0, 2, 4, 7, 6, 7, 8, 9, 10, 11]
        result = operator_consecutive_growth_months(amounts)
        print(f"growth months is: {result}")

        amounts = [100, 120, 110, 130, 150, 160, 170, 180, 190, 200]
        result = operator_consecutive_growth_months(amounts)
        print(f"growth months is: {result}")
