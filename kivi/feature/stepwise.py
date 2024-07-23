import pandas as pd
import statsmodels.api as sm
from pandas import DataFrame
from typing import Any, List, Callable, Literal, Optional

from ..utils.logger import LoggerMixin
from ..ModelEval import RocAucKs
from .schema import StepwiseReport


__all__ = [
    "StepWise",
    "StepwiseMixin",
]


class StepwiseMixin(LoggerMixin):
    """逐步回归法"""
    df: DataFrame

    def step_fit(self, columns: List[str], target, report: StepwiseReport) -> StepwiseReport:
        """"""
        x_data = sm.add_constant(self.df[columns], has_constant='add')
        y_data = target
        report.num_features = len(columns)
        try:
            model = sm.Logit(y_data, x_data).fit(disp=0)
            metrics = RocAucKs(true=model.model.endog, predict=model.predict())
            report = report.model_copy(update=metrics)
        except Exception as e:
            self._logger(msg=f'Model Error! Feature Name: {columns}, Error Msg: {e}', color="red")
        return report


class StepWise(StepwiseMixin):
    """向前逐步回归"""
    def __init__(
            self,
            df: pd.DataFrame,
            columns: Optional[List[str]] = None,
            target_name: Optional[str] = "target",
            var_field: Optional[str] = "var_name",
            dependent: Optional[DataFrame] = None,
            indicator: Optional[str] = 'auc',
            early_stop: Optional[float] = 0.01,
            logger: Optional[Callable] = None,
            verbose: Optional[bool] = True,
            *args: Any,
            **kwargs: Any,
    ):
        """"""
        self.df = df
        self.target_name = target_name
        self.var_field = var_field
        self.columns = columns
        self.dependent = dependent
        self.indicator = indicator
        self.early_stop = early_stop
        self.logger = logger
        self.verbose = verbose
        self.args = args
        self.kwargs = kwargs
        self._validate_data()
        self._prepare_data()

    def __call__(self, step_type: Literal["forward", "backward"], *args, **kwargs) -> DataFrame:
        """"""
        if step_type == "forward":
            return self.forward()
        elif step_type == "backward":
            return self.backward()
        else:
            raise ValueError(f"step_type {step_type} not supported")

    def _validate_data(self):
        """"""
        if self.target_name not in self.df.columns:
            raise ValueError(f"target_name {self.target_name} not in df.columns: {self.df.columns.tolist()}")
        if self.var_field not in self.dependent.columns:
            raise ValueError(f"var_field {self.var_field} not in dependent.columns: {self.dependent.columns.tolist()}")

    def _prepare_data(self):
        if self.columns is None:
            self.columns = self.df.columns.tolist()

    def _get_candidate_columns(self):
        """"""
        self.candidate_columns = self.dependent.sort_values(by=self.indicator, ascending=False)[self.var_field].tolist()
        self.candidate_columns = [column for column in self.candidate_columns if column in self.columns]

    def forward(self) -> DataFrame:
        """"""
        self._get_candidate_columns()
        steps = []
        for i in range(len(self.candidate_columns)):
            columns = self.candidate_columns[: i + 1]
            step_report = StepwiseReport(feature=columns)
            step_report = self.step_fit(columns=columns, target=self.df[self.target_name], report=step_report)
            steps.append(step_report.model_dump())
        return pd.DataFrame(steps)

    def backward(self) -> DataFrame:
        return pd.DataFrame()
