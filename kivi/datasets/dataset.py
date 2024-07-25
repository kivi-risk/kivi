import os
import numpy as np
import pandas as pd
from typing import Optional
from sklearn import datasets
from sklearn.model_selection import train_test_split


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

    def dataset(self, ):
        np.random.seed(0)
        x, y = datasets.make_classification(
            n_samples=self.n_samples, n_features=self.n_features,
            n_informative=self.n_informative, n_redundant=self.n_redundant)
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=self.test_size, random_state=42)
        return x_train, x_test, y_train, y_test

    def sample(self):
        """"""
        columns_name = [f"col_{i}" for i in range(self.n_features)]
        x_train, x_test, y_train, y_test = self.dataset()
        train = pd.concat([pd.DataFrame(x_train, columns=columns_name), pd.DataFrame(y_train, columns=['target'])], axis=1)
        test = pd.concat([pd.DataFrame(x_test, columns=columns_name), pd.DataFrame(y_test, columns=['target'])], axis=1)
        train["uuid"] = np.arange(len(train))
        test["uuid"] = np.arange(len(test))
        return train, test
