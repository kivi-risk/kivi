import os
import pandas as pd


path = os.path.dirname(__file__)


__all__ = [
    "Dataset",
    "MakeData",
]


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

    def __init__(self):
        pass

    def dataset(self, ):
        from sklearn import datasets
        import numpy as np
        np.random.seed(0)
        x, y = datasets.make_classification(
            n_samples=100000, n_features=20,
            n_informative=2, n_redundant=2)
        train_samples = 100
        x_train, x_test = x[:train_samples], x[train_samples:]
        y_train, y_test = y[:train_samples], y[train_samples:]
        return x_train, x_test, y_train, y_test
