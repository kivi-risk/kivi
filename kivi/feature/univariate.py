import numpy as np
import pandas as pd
from pandas import DataFrame, Series
import statsmodels.api as sm
from typing import Any, List, Dict, Tuple, Callable, Literal, Optional

from ..utils.utils import dispatch_tqdm
from ..utils.operator import Div, mode
from ..utils.logger import LoggerMixin
from ..evaluate.Metrics import ks_test, RocAucKs, Chi2
from .schema import *


__all__ = [
    "FeatureEvaluate",
]


class FeatureEvaluate(LoggerMixin):
    """"""
    df_report: DataFrame
    report_data: List[Dict[str, Any]]

    def __init__(
            self,
            df: DataFrame,
            target_name: str = 'target',
            columns: Optional[List[str]] = None,
            columns_mapping: Optional[Dict[Any, str]] = None,
            eval_method: Optional[Literal["origin", "woe"]] = "origin",
            logger: Optional[Callable] = None,
            verbose: Optional[bool] = True,
            *args: Any,
            **kwargs: Any,
    ):
        """"""
        self.df = df
        self.target_name = target_name
        self.columns_mapping = columns_mapping
        self.eval_method = eval_method
        self.logger = logger
        self.verbose = verbose
        self.args = args
        self.kwargs = kwargs
        self._validate_data()
        self._analysis_columns(columns)
        self._base_stats()
        self.output_fields = [
            'var_name', 'desc', 'bad_rate', 'missing', 'miss_bad_rate', 'not_miss_bad_rate',
            'null_lift', 'not_null_lift', 'min', 'max', 'std', 'mode', 'skew', 'kurt',
            'cv', 'unique', 'bad', 'count', 'good', 'ks_test', 'R2', 'intercept',
            'pvalue_intercept', 'param', 'pvalue_param', 'fpr', 'tpr', 'auc', 'ks',
            'chi_statistic', 'chi_pvalue'
        ]

    def __call__(self, *args, **kwargs):
        """"""

    def _div(self, a, b, else_value=-9999.):
        """"""
        if b != 0:
            return a / b
        else:
            return else_value

    def _validate_data(self):
        """"""
        if not isinstance(self.df, DataFrame):
            raise TypeError(f'df must be a pandas DataFrame, got {type(self.df)}')
        if self.target_name not in self.df.columns:
            raise ValueError(f'target_name {self.target_name} not in df.columns')

    def _analysis_columns(self, columns: Optional[List[str]] = None):
        """"""
        if columns is None:
            columns = self.df.columns.to_list()
            for drop_col in [self.target_name]:
                if drop_col in columns:
                    columns.remove(drop_col)
            self.columns = columns
        else:
            self.columns = columns

    def _prepare_data(self, column: Series, target: Series) -> Tuple[Series, Series]:
        """"""
        condition = ~(column.isna() | (np.isinf(column.astype('float'))))
        column_data = column[condition].copy()
        target_data = target[condition].copy()
        return column_data, target_data

    def _base_stats(self):
        """"""
        self.bad_rate = self.df[self.target_name].mean()

    def _column_info(self, column: Series, report: FeatureEvaluateSchema):
        """"""
        report.var_name = column.name
        report.bad_rate = self.bad_rate
        if self.columns_mapping:
            report.desc = self.columns_mapping.get(report.var_name)

    def _column_base(self, column_data: Series, target_data: Series, report: FeatureEvaluateSchema):
        """"""
        report.min = float(column_data.min())
        report.max = float(column_data.max())
        report.std = float(column_data.std())
        report.mode = float(column_data.mode(dropna=True).tolist()[0])
        report.skew = float(column_data.skew())
        report.kurt = float(column_data.kurt())
        report.cv = Div.div(float(column_data.std()), float(column_data.mean()))
        report.unique = len(column_data.unique())
        report.bad = int(target_data.sum())
        report.count = int(target_data.count())
        report.good = int(report.count - report.bad)
        report.ks_test = ks_test(column_data, target_data)[0]

        # chi2
        chi_statistic, chi_pvalue = Chi2(
            column_data.values.reshape(-1, 1),
            target_data.values)
        report.chi_statistic = chi_statistic
        report.chi_pvalue = chi_pvalue

    def _column_missing(self, column: Series, target: Series, report: FeatureEvaluateSchema):
        """"""
        report.missing = column.isna().mean()
        report.miss_bad_rate = target[column.isna()].mean()
        report.not_miss_bad_rate = target[column.notna()].mean()
        report.null_lift = self._div(report.miss_bad_rate, self.bad_rate)
        report.not_null_lift = self._div(report.not_miss_bad_rate, self.bad_rate)

    def _column_logist(
            self,
            column: Optional[Series] = None,
            target: Optional[Series] = None,
            column_data: Optional[Series] = None,
            target_data: Optional[Series] = None,
            report: Optional[FeatureEvaluateSchema] = None,
    ) -> FeatureEvaluateSchema:
        """"""
        if self.eval_method == "origin":
            x_data = column_data
            y_data = target_data
        elif self.eval_method == "woe":
            x_data = column
            y_data = target
        else:
            raise ValueError(f"eval_method {self.eval_method} not support")
        x_data = sm.add_constant(x_data, has_constant='add')
        try:
            model = sm.Logit(y_data, x_data).fit(disp=0)
            report.R2 = model.prsquared
            report.intercept = model.params.const
            report.pvalue_intercept = model.pvalues.const
            report.param = model.params[report.var_name]
            report.pvalue_param = model.pvalues[report.var_name]
            report = report.model_copy(update=RocAucKs(true=model.model.endog, predict=model.predict()))
        except Exception as e:
            self._logger(msg=f'Model Error! Feature Name: {report.var_name}, Error Msg: {e}', color="red")
        return report

    def stats(self) -> DataFrame:
        """"""
        eval_report = []
        for column_name in dispatch_tqdm(self.columns, desc="FeatureEvaluate"):
            feature_report = FeatureEvaluateSchema()
            column = self.df[column_name]
            column_data, target_data = self._prepare_data(column=column, target=self.df[self.target_name])
            self._column_info(column=column, report=feature_report)
            self._column_missing(column=column, target=self.df[self.target_name], report=feature_report)
            self._column_base(column_data=column_data, target_data=target_data, report=feature_report)
            feature_report = self._column_logist(
                column=column, target=self.df[self.target_name],
                column_data=column_data, target_data=target_data,
                report=feature_report
            )
            eval_report.append(feature_report.model_dump())
        return pd.DataFrame(eval_report)[self.output_fields]
