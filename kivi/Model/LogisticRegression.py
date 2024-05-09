


from itertools import product, combinations
from collections import defaultdict
import statsmodels.api as sm
from tqdm import tqdm
import pandas as pd
from ..ModelTools import get_ks

from sklearn.linear_model import LogisticRegressionCV
from ..ModelTools import statsmodel_metrics, sklearn_metrics

class Logistic:

    def __init__(self, data, y_name, alphas=None, framework='sklearn', threshold=0.5):

        y = data.pop(y_name)
        self.exog = data.copy()
        self.endog = y.copy()
        self.framework = framework
        self.threshold=threshold


    def logistic(self, exog, endog):

        if self.framework == 'sklearn':
            model = LogisticRegressionCV(cv=5, random_state=0)
            self.model = model.fit(exog, endog)

        elif self.framework == 'statsmodel':
            self.model = sm.Logit(endog, exog).fit(disp=0)

        else:
            Exception(ValueError, 'Framework Error!')


    def metrics(self, model, col, res, prefix):
        if self.framework=='statsmodel':
            statsmodel_metrics(
                res=res,
                prefix=prefix,
                model=model,
                col=col,
                threshold=self.threshold,
            )
        elif self.framework=='sklearn':
            sklearn_metrics(
                res=res,
                model=model,
                threshold=self.threshold,
                prefix=prefix,
            )


    def plot_roc(self):
        pass


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


    def different_variable_combinations(self, col_description=None, normalized=True, *args, **kwargs):
        """
        Des: OLS Different variable combinations
        :param features_num: 变量数
        :return: model_index, variables_index
        """
        res_dict = defaultdict(list)
        cols = self.exog.columns.to_list()

        variables_index = pd.DataFrame()

        if "const" in cols:
            cols.remove("const")

        if isinstance(args[0], int) and len(args) == 1:
            if len(cols) < args[0]:
                raise Exception(ValueError, 'features_num must more than the columns!')
            combins = list(enumerate(combinations(cols, args[0])))

        else:
            combins = list(product(*args))

        if combins:
            for temp_cols in tqdm(combins, desc=f'Total regressions {len(combins)}'):
                temp_cols = list(temp_cols)
                temp_data = self.exog[temp_cols]

                # data clean
                temp_data['target'] = self.endog
                temp_data.dropna(axis=0, inplace=True)

                if temp_data.target.sum() != 0:
                    res_dict['coll_name'].append(temp_cols)

                    # chinese description for columns
                    if isinstance(col_description, dict):
                        if len(temp_cols) > 1:
                            res_dict['des'].append([col_description.get(col) for col in temp_cols])
                        else:
                            res_dict['des'].append(col_description.get(temp_cols))
                            try:
                                res_dict['ks'].append(get_ks(temp_data[temp_cols], temp_data.target)[0])
                            except:
                                res_dict['ks'].append(0)

                    res_dict['missing_rate'].append(float(len(temp_data) / len(self.endog)))
                    res_dict['bad'].append(temp_data.target.sum())
                    res_dict['count'].append(temp_data.target.count())
                    res_dict['good'].append(temp_data.target.count() - temp_data.target.sum())
                    res_dict['bad_rate'].append(temp_data.target.sum() / temp_data.target.count())

                    X = sm.add_constant(temp_data[temp_cols])
                    try:
                        self.logistic(X, temp_data.target)
                    except Exception as e:
                        print(e, temp_cols)

                    statsmodel_metrics(res=res_dict, prefix='', model=self.model, col=temp_cols)

                    # if kwargs.get('normalized'):
                    if normalized:
                        X = sm.add_constant(
                            (temp_data[temp_cols] - temp_data[temp_cols].min()) / (temp_data[temp_cols].max() - temp_data[temp_cols].min()),
                        )

                        try:
                            self.logistic(X, temp_data.target)
                        except Exception as e:
                            print(e, temp_cols)

                        statsmodel_metrics(res=res_dict, prefix='normal_', model=self.model, col=temp_cols)

                    if len(temp_cols) != 1:
                        vifLs = self.vif(temp_data[temp_cols], ls=True)
                    res_dict['vif'].append(vifLs)
                else:
                    continue

            return pd.DataFrame(res_dict)
        else:
            raise Exception(ValueError, 'combins are None!')

