

from sklearn.linear_model import RidgeCV
from pandas import DataFrame, Series
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.compose import TransformedTargetRegressor
import numpy as np



class Ridge:

    def __init__(self, data, y_name, alphas, normalize=False, log_y=False):
        """
        Des: Ridge | 岭回归方法
        :param data: 数据集
        :param y_name: y 名称
        :param alphas: 待选alpha参数
        :param normalize: 是否正则化，默认False
        :param log_y: 是否y取对数，默认False
        """
        y = data.pop(y_name)
        self.exog = data.copy()
        self.endog = y.copy()

        self.model = self.ridge(self.exog, self.endog, alphas, normalize, log_y)

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


    def ridge(self, X, y, alphas, normalize, log_y):
        """
        Des: Ridge 回归
        :param X:
        :param y:
        :param alphas:
        :param normalize:
        :param log_y:
        :return:
        """
        if log_y:
            _model = RidgeCV(alphas=alphas, normalize=normalize)
            tt_model = TransformedTargetRegressor(
                regressor=_model,
                func=np.log,
                inverse_func=np.exp
            )
            return tt_model.fit(X, y)
        else:
            return RidgeCV(alphas=alphas, normalize=normalize).fit(X, y)

