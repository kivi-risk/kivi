from pyspark.ml.feature import VectorAssembler
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.regression import LinearRegression
from pyspark.ml.stat import ChiSquareTest


__all__ = ['SparkUnivariate']


class SparkUnivariate(object):
    """

    """
    def __init__(self, df, target_name='target', na='drop'):
        self.df = df

    def describe(self, ):
        df_res = self.df.describe()

    def modelRes(self, col):
        return None
