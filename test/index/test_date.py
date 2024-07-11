import unittest
from kivi.index.date import *


class TestDate(unittest.TestCase):
    """"""

    def test_get_start_and_end_date(self):
        """"""
        month = 3
        biz_date = "20200131"
        print(get_start_and_end_date(biz_date, month))
        print(get_start_and_end_date(biz_date, month))
        print(get_start_and_end_date(biz_date, month=2))
        print(get_start_and_end_date(biz_date, month="hist"))

