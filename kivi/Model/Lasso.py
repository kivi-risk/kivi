

import numpy as np
from sklearn.linear_model import LassoCV
import matplotlib.pyplot as plt
from pandas import DataFrame, Series
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.compose import TransformedTargetRegressor



class Lasso:

    def __init__(self, data, y_name, alphas, normalize=False, random_state=None, log_y=False):
        """
        Des: Lasso 回归方法
        :param data: 数据集
        :param y_name: y 名称
        :param alphas: 待选alpha参数
        :param normalize: 是否正则化，默认False
        :param random_state: 随机种子
        :param log_y: 是否y取对数，默认False
        """
        y = data.pop(y_name)
        self.exog = data.copy()
        self.endog = y.copy()

        self.model = self.lasso(self.exog, self.endog, alphas, normalize, random_state, log_y)
        if log_y:
            self.coef = Series(self.model.regressor_.coef_, index=self.exog.columns).abs().sort_values(ascending=False)
            self.intercept = self.model.regressor_.intercept_
            self.alpha = self.model.regressor_.alpha_

        else:
            self.coef = Series(self.model.coef_, index=self.exog.columns).abs().sort_values(ascending=False)
            self.intercept = self.model.intercept_

        y_pre = self.model.predict(self.exog)
        self.mse = mean_squared_error(self.endog, y_pre)
        self.r2_score = r2_score(self.endog, y_pre)

    def lasso(self, X, y, alphas, normalize, random_state, log_y):
        """
        Des: Lasso 回归
        :param X:
        :param y:
        :param alphas:
        :param normalize:
        :param random_state:
        :param log_y:
        :return:
        """
        if log_y:
            _model = LassoCV(alphas=alphas, normalize=normalize)
            tt_model = TransformedTargetRegressor(
                regressor=_model,
                func=np.log,
                inverse_func=np.exp
            )
            return tt_model.fit(X, y)
        else:
            return LassoCV(alphas=alphas, normalize=normalize, random_state=random_state).fit(X, y)

    def plot_variable_importance(self, ):
        """
        Des: 绘制参数重要性图
        :return:
        """
        plt.figure(dpi=80)
        plt.bar(self.coef.index, self.coef.values)
        return None

    def select_features(self, feature_nums=None, min_treshold=0.1):
        """
        Des: 选择最重要的几个特征
        :param feature_nums: 选择特征数
        :param min_treshold: 特征重要性阈值
        :return: 相应特征的数据
        """
        if feature_nums >= self.exog.shape[-1]:
            raise Exception(ValueError, 'feature_nums must be less than exog columns!')

        try:
            from sklearn.feature_selection import SelectFromModel
            sfm = SelectFromModel(self.model, threshold=min_treshold, prefit=True)
            n_features = sfm.transform(self.exog).shape[1]

            while n_features > feature_nums:
                sfm.threshold += 0.1
                X_transform = sfm.transform(self.exog)
                n_features = X_transform.shape[1]
            if feature_nums != n_features:
                return self.exog[self.coef.index[: feature_nums]]
            return DataFrame(X_transform, columns=self.coef.index[: feature_nums])

        except:
            return self.exog[self.coef.index[: feature_nums]]
