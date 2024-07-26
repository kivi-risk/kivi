import unittest
from pyspark.sql import SparkSession
from kivi.spark.operator import SparkBaseOperator


class TestSparkBaseOperator(unittest.TestCase):
    """"""
    def setUp(self):
        self.spark = SparkSession.builder.appName("My App").getOrCreate()

    def test_spark_base_operator(self):
        base_operator = SparkBaseOperator()
        print(base_operator.sum("col"))


