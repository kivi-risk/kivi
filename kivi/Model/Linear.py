

import warnings
warnings.filterwarnings('ignore')


import numpy as np
import statsmodels.stats.api as sms
from tqdm import tqdm
import statsmodels.api as sm
from pandas import DataFrame, Series
from statsmodels.compat import lzip
from itertools import combinations, product
from statsmodels.stats.outliers_influence import OLSInfluence
from collections import defaultdict
import matplotlib.pyplot as plt


class LinearRegression:

    def __init__(self, data: DataFrame, y_name='endog', estimate='ols', log_cols=None):
        """
        Des: 线性回归方法
        :param data: [DataFrame] 数据
        :param y_name: [str] y 在数据集DataFrame中的名称
        :param log_cols: [str, list] 对给定的列取对数，可以是list给定列名称，
            也可以是字符串:
                'all', 全部取对数
                'endog', 因变量(y)取对数
                'exdog', 自变量(X)取对数
        :param estimate: [str] 估计方式 'ols' 普通最小二乘 or 'rlm' Robust lm
        """
        if isinstance(log_cols, list):
            self._log(log_cols, data)
            if y_name in log_cols:
                y_name = 'log_' + y_name

        elif log_cols == 'exdog':
            exdog_cols = data.columns.to_list()
            exdog_cols.remove(y_name)
            self._log(exdog_cols, data)

        elif log_cols == 'endog':
            data[y_name] = np.log(data[y_name])
            data.rename(columns={y_name: 'log_' + y_name}, inplace=True)
            y_name = 'log_' + y_name

        elif log_cols == 'all':
            cols = data.columns.to_list()
            self._log(cols, data)
            y_name = 'log_' + y_name
        else:
            Exception(ValueError, 'log_col value error!')


        y = data.pop(y_name)
        self.exog = data.copy()
        self.endog =y.copy()
        # 估计方式OLS or RLM
        self.estimate = estimate


    def _log(self, cols, data):
        """
        Des: 对列取对数
        :param cols:
        :param data:
        :return: None
        """
        for col in cols:
            data['log_' + col] = np.log(data[col])
        data.drop(cols, axis=1, inplace=True)


    def ols(self, X, y, constant=True):
        """
        Des: 最小二乘估计
        :param X: 数据X
        :param y: 数据y
        :param constant: 是否添加常数项
        :return: 回归结果
        """
        if constant and ('const' not in X.columns):
            X = sm.add_constant(X)
        return sm.OLS(y, X).fit()


    def rlm(self, X, y, constant=True):
        """
        Des: 最小二乘估计
        :param X: 数据X
        :param y: 数据y
        :param constant: 是否添加常数项
        :return: 回归结果
        """
        if constant and ('const' not in X.columns):
            X = sm.add_constant(X)
        return sm.RLM(y, X, M=sm.robust.norms.HuberT()).fit()


    def metrics(self, res):
        if self.estimate == 'ols':
            if self.exog.shape[-1] != 1:
                self.cond_num = self.condition_number(self.exog)
                self.vif_value = self.vif(self.exog)
            self.heteroske_test = self.heteroskedasticity(res)
            self.residuals_norm_test = self.residuals_norm(res)
            self.linearity_test = self.linearity(res)
            self.influence_test = self.influence(res)
            self.DW = self.dw(res)
        if self.estimate == 'rlm':
            raise Exception(ValueError, 'rlm 的回归诊断还未开发！')


    def vif(self, exog, exog_idx=None, ls=False):
        """
        Des: 方差膨胀因子 - 多重共线性参考指标
        :param exog: 变量
        :param exog_idx: 变量索引，在不指定变量索引时计算全部变量的vif，并以字典形式返回计算结果
        :param ls: 以list的形式返回数据
        :return: float or dict vif
        """
        from statsmodels.stats.outliers_influence import variance_inflation_factor
        if exog_idx:
            return variance_inflation_factor(exog, exog_idx)
        elif ls:
            return [variance_inflation_factor(exog.values, i) for i in range(exog.shape[-1])]
        else:
            vif_dict = {}
            for i, name in enumerate(exog):
                if name == "const":
                    continue
                vif_dict[name] = variance_inflation_factor(exog.values, i)
            return vif_dict


    def condition_number(self, exog):
        """
        Des: 条件数 - 多重共线性参考指标
        :param exog: 变量
        :return: [float] 条件数
        """
        return np.linalg.cond(exog)


    def residuals_norm(self, res):
        """
        Des: 残差正态性检验，Jarque-Bera，Omni-score 两种方法
        :param res: 回归结果
        :return: [dict]
        """
        residuals_norm_test_res = {}

        name = ['Jarque-Bera', 'Chi^2 two-tail prob.', 'Skew', 'Kurtosis']
        test = sms.jarque_bera(res.resid)
        residuals_norm_test_res['Jarque-Bera'] = lzip(name, test)

        name = ['Chi^2 score', 'Two-tail probability']
        test = sms.omni_normtest(res.resid)
        residuals_norm_test_res['Omni'] = lzip(name, test)
        return residuals_norm_test_res


    def heteroskedasticity(self, res):
        """
        Des: 异方差检验 Breush - Pagan 与 Goldfeld - Quandt两种检验方法
        :param res: 回归结果
        :return: [dict]
        """
        # Breush - Pagan
        heteroske_test_res = {}
        name = ['Lagrange multiplier statistic', 'p-value',
                'f-value', 'f p-value']
        test = sms.het_breuschpagan(res.resid, res.model.exog)
        heteroske_test_res['Breush-Pagan'] = lzip(name, test)

        # Goldfeld - Quandt
        name = ['F statistic', 'p-value']
        test = sms.het_goldfeldquandt(res.resid, res.model.exog)
        heteroske_test_res['Goldfeld-Quandt'] = lzip(name, test)
        return heteroske_test_res


    def linearity(self, res):
        """
        Des: 线性性检验
        :param res: 回归结果
        :return: [list]
        """
        name = ['t value', 'p value']
        test = sms.linear_harvey_collier(res)
        return lzip(name, test)


    def influence(self, res):
        """
        Des: 影响测试
        :param res: 回归结果
        :return: DataFrame
        """
        influence_test = OLSInfluence(res)
        return influence_test.summary_frame()


    # Plot leverage statistics vs. normalized residuals squared
    def plot_leverage_resid2(self, res):
        """
        Des: leverage vs. resid
        :param res: 回归结果
        :return: plt
        """
        sm.graphics.plot_leverage_resid2(res)
        return None


    def plot_variance_homogeneity(self, exog, resid, **kwargs):
        """

        :param exog:
        :param res:
        :param kwargs:
        :return:
        """
        if isinstance(exog, DataFrame):
            cols = exog.columns.to_list()
            kwargs.setdefault('figsize', (10, len(cols) * 3.5))

        kwargs.setdefault('style', 'seaborn')
        kwargs.setdefault('dpi', 150)
        kwargs.setdefault('labelfontsize', 10)
        kwargs.setdefault('tickfontsize', 8)
        kwargs.setdefault('titlefontsize', 12)
        kwargs.setdefault('x_label', 'False Positive Rate')
        kwargs.setdefault('y_label', 'True Positive Rate')
        kwargs.setdefault('title', 'Receiver operating characteristic')

        plt.style.use(kwargs.get('style'))

        if isinstance(exog, Series):
            plt.figure(figsize=(6, 4), dpi=kwargs.get('dpi'))
            plt.scatter(exog, resid)
            plt.axhline(y=0, color='tab:red', linestyle='--')
            plt.xlabel(exog.name)
            plt.ylabel('Residual')
            return None

        fig, axs = plt.subplots(
            len(cols),
            figsize=kwargs.get('figsize'),
            dpi=kwargs.get('dpi')
        )
        for i, col in enumerate(cols):
            axs[i].scatter(exog[col], resid)
            axs[i].set_xlabel(col)
            axs[i].axhline(y=0, color='tab:red', linestyle='--')
            axs[i].set_ylabel('Residual')
        return None


    def plot_resid(self):
        import seaborn as sns
        from scipy.stats import norm
        sns.distplot(
            self.res.resid,
            fit=norm,
            kde=False,
        )
        return None


    def plot_pp(self):
        pq = sm.ProbPlot(self.res.resid)
        pq.ppplot(line='45')
        return None


    def plot_qq(self):
        pq = sm.ProbPlot(self.res.resid)
        pq.qqplot(line='q')
        return None


    def dw(self, res):
        return sm.stats.stattools.durbin_watson(res.resid)


    def bp_test(self, ):
        return sm.stats.diagnostic.het_breuschpagan(self.res.resid, self.res.model.exog)


    def plot_regression(self, x, res, **kwargs):

        if res.params[0] <= 0:
            kwargs.setdefault('title', f'$y = {res.params[-1]: .2f} x {res.params[0]: .2f}$')
        else:
            kwargs.setdefault('title', f'$y = {res.params[-1]: .2f} x + {res.params[0]: .2f}$')

        kwargs.setdefault('xlabel', 'exdog')
        kwargs.setdefault('ylabel', 'endog')
        kwargs.setdefault('dpi', 100)
        kwargs.setdefault('figsize', (8, 6))

        fig, ax = plt.subplots(figsize=kwargs.get('figsize'), dpi=kwargs.get('dpi'))
        ax.plot(x, self.endog, 'o', label="data")
        ax.plot(x, res.fittedvalues, 'r--.', label="Regression")
        ax.set_xlabel(kwargs.get('xlabel'))
        ax.set_ylabel(kwargs.get('ylabel'))
        ax.set_title(kwargs.get('title'))
        ax.legend()


    def different_variable_combinations(self, *args):
        """
        Des: OLS Different variable combinations
        :param features_num: 变量数
        :return: model_index, variables_index
        """
        res_dict = defaultdict(list)
        cols = self.exog.columns.to_list()

        variables_index = DataFrame()

        if "const" in cols:
            cols.remove("const")

        combins = None

        if isinstance(args[0], int):
            features_num = args[0]
            if len(cols) < features_num:
                raise Exception(ValueError, 'features_num must more than the columns!')
            combins = list(enumerate(combinations(cols, features_num)))
        elif args:
            features_num=None
            combins = list(enumerate(product(*args)))

        if combins:
            for i, temp_cols in tqdm(combins, desc=f'Total regressions {len(combins)}'):
                exog = self.exog[list(temp_cols)]
                res = self.ols(exog, self.endog)
                res_dict['columns'].append(temp_cols)
                res_dict['nobs'].append(res.nobs)
                res_dict['rsquared'].append(res.rsquared)
                res_dict['rsquared_adj'].append(res.rsquared_adj)
                res_dict['f_pvalue'].append(res.f_pvalue)
                res_dict['aic'].append(res.aic)
                res_dict['bic'].append(res.bic)
                res_dict['DW'].append(self.dw(res))

                if features_num != 1:
                    variables_index[f'group_{i}'] = res.pvalues.index
                    variables_index[f'pvalues_{i}'] = res.pvalues.values
                    vifLs = self.vif(exog, ls=True)
                    vifLs.insert(0, np.nan)
                    variables_index[f'vif_{i}'] = vifLs

            return DataFrame(res_dict), variables_index
        else:
            raise Exception(ValueError, 'combins are None!')
