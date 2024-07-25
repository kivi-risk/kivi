import numpy as np
import pandas as pd
from statsmodels.api import OLS
from tqdm import tqdm_notebook

from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression
from statsmodels.stats.outliers_influence import variance_inflation_factor as vif


class VIF:
    """
    全部VIF方法
    1. statsmodels `vif()`            statsmodels VIF
    2. statsmodels `StatsTableVIF()`  statsmodels 计算全表VIF
    3. statsmodels `LowVIFFeatures()` 依据VIF设定阈值，选择最小VIF特征组合
    4. PySpark     `SparkVIF()`       PySpark 计算变量VIF
    5. PySpark     `SparkTableVIF()`  PySpark 计算全表VIF
    """
    @staticmethod
    def vif(exog, exog_idx):
        """
        改进 statsmodels 中的 variance_inflation_factor
        :param exog:
        :param exog_idx:
        :return:
        """
        k_vars = exog.shape[1]
        x_i = exog[:, exog_idx]
        mask = np.arange(k_vars) != exog_idx
        x_noti = exog[:, mask]
        r_squared_i = OLS(x_i, x_noti, missing='drop').fit().rsquared
        return 1. / (1. - r_squared_i)

    @staticmethod
    def StatsTableVIF(df):
        """
        描述：statsmodels `StatsTableVIF()` 计算全表 VIF

        参数：
        :param df[pandas.DataFrame]: 全量需要计算`VIF`的特征`DataFrame`

        示例：
        >>> pd.DataFrame(VIF.StatsTableVIF(df))
        """
        feature_vif = []
        for i, column_name in enumerate(df.columns):
            feature_vif.append({
                'feature': column_name,
                'vif_value': vif(df.values, i)
            })
        return feature_vif

    @staticmethod
    def LowVIFFeatures(df, thresh=5):
        """
        描述：选择最低VIF特征组合。

        参数：
        :param df[pandas.DataFrame]: 特征
        :param thresh[int]: VIF阈值
        :return [pandas.DataFrame]: 指标名称列表，筛选明细

        示例：
        >>> VIF.LowVIFFeatures(df, thresh=5)
        """
        feature_vif = VIF.StatsTableVIF(df)
        df_vif = pd.DataFrame(feature_vif)
        max_vif = df_vif.vif_value.max()

        while max_vif >= thresh and len(df.columns) > 2:
            vif_sums = []
            vif_maxs = []
            vif_ress = []

            for col in df.columns:
                new_vif = pd.DataFrame(VIF.StatsTableVIF(df.drop(col, axis=1)))
                vif_sums.append(new_vif.vif_value.sum())
                vif_maxs.append(new_vif.vif_value.max())
                vif_ress.append(new_vif)

            min_index = vif_sums.index(min(vif_sums))
            max_vif = vif_maxs[min_index]
            vif_res = vif_ress[min_index]
            drop_col = df.columns[min_index]
            df.drop(drop_col, axis=1, inplace=True)
            df_vif = df_vif.merge(vif_res, on='feature', how='left')
            features = df_vif.iloc[:, -1].dropna().shape[0]
            print(f'features: {features}')

        columns_name = ['feature'] + [f'step_{i}' for i in range(1, len(df_vif.columns))]
        df_vif.columns = columns_name
        return df_vif

    @staticmethod
    def SparkVIF(df, var_name, other_vars=None):
        """
        描述：计算方差膨胀因子

        参数：
        :param df[PySpark DataFrame]: 数据表 PySpark DataFrame
        :param var_name[str]: 需要计算 VIF 的字段名称
        :param other_vars[list]: 需要计算 VIF 的参照变量，默认为 `df` 中除了 `var_name` 的全部变量
        :return vif[float]: 变量 `var_name` 的方差膨胀因子

        示例：
        >>> VIF.SparkVIF(df, 'col_0')
        """
        if other_vars is None:
            other_vars = df.drop(var_name).columns

        vector_translate = VectorAssembler(inputCols=other_vars, outputCol='features')
        df_feature = vector_translate.transform(df)

        linear = LinearRegression(
            labelCol=var_name,
            fitIntercept=False,
        ).fit(df_feature)

        r_squared = linear.summary.r2
        return 1. / (1. - r_squared)

    @staticmethod
    def SparkTableVIF(df):
        """
        描述：计算整个Spark DataFrame表的方差膨胀因子。

        :param df: Spark DataFrame
        :return: Pandas DataFrame
        """
        columns_name = df.columns
        vifs = []
        for column_name in tqdm_notebook(columns_name):
            vifs.append(VIF.SparkVIF(df, var_name=column_name))
        return pd.DataFrame({
            'var_name': columns_name,
            'VIF': vifs,
        })


