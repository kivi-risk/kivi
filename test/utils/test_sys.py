import sys
import unittest


class TestSystem(unittest.TestCase):
    """"""
    def test_system(self):
        print('ipython' in sys.argv[0].lower())
        print('ipykernel' in sys.modules)

