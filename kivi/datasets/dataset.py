import os
import numpy as np
import pandas as pd
from pandas import DataFrame
from typing import Tuple, Optional
from sklearn import datasets
from sklearn.model_selection import train_test_split
from .schema import *


__all__ = [
    "Dataset",
    "MakeData",
]
path = os.path.dirname(__file__)


class Dataset:
    """
    描述：返回用于示例文档的数据集。

    Example:
        dataset = Dataset()
        df_bank = dataset.bank_data()
        df_crime = dataset.crime_data()
    """
    @staticmethod
    def bank_data():
        """
        描述：获取一份信贷数据，包括个人主体信息以及违约标签。
        :return: DataFrame
        """
        filename = os.path.join(path, 'bank.xlsx')
        df = pd.read_excel(filename)
        df['target'] = df['y'].apply(lambda x: 1 if x == 'yes' else 0)
        return df.drop('y', axis=1)

    @staticmethod
    def crime_data():
        """
        描述：获取一份欺诈犯罪数据，包括个人主体信息以及欺诈标签。
        :return: DataFrame
        """
        filename = os.path.join(path, 'crime_data.csv')
        return pd.read_csv(filename)


class MakeData:

    def __init__(
            self,
            n_samples: Optional[int] = 10000,
            n_features: Optional[int] = 5,
            n_informative: Optional[int] = 5,
            n_redundant: Optional[int] = 0,
            test_size: Optional[float] = 0.3,
    ):
        self.n_samples = n_samples
        self.n_features = n_features
        self.n_informative = n_informative
        self.n_redundant = n_redundant
        self.test_size = test_size

    def dataset(self, ) -> MakeDataOutput:
        np.random.seed(0)
        x, y = datasets.make_classification(
            n_samples=self.n_samples, n_features=self.n_features,
            n_informative=self.n_informative, n_redundant=self.n_redundant)
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=self.test_size, random_state=42)
        data = MakeDataOutput(x_train=x_train, x_test=x_test, y_train=y_train, y_test=y_test)
        return data

    def sample(self) -> Tuple[DataFrame, DataFrame]:
        """"""
        columns_name = [f"col_{i}" for i in range(self.n_features)]
        data = self.dataset()
        train = pd.concat([pd.DataFrame(data.x_train, columns=columns_name), pd.DataFrame(data.y_train, columns=['target'])], axis=1)
        test = pd.concat([pd.DataFrame(data.x_test, columns=columns_name), pd.DataFrame(data.y_test, columns=['target'])], axis=1)
        train["uuid"] = np.arange(len(train))
        test["uuid"] = np.arange(len(test))
        return train, test
