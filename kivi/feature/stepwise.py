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

    def implication(self, model, columns: List[str], report: StepwiseReport) -> StepwiseReport:
        """"""
        params = model.params[columns]
        report.params = params.round(6).to_dict()
        report.woe_impact = params[params < 0].index.tolist()
        report.positive_impact = params[params > 0].index.tolist()
        report.negative_impact = params[params < 0].index.tolist()
        return report

    def step_fit(self, columns: List[str], target, report: StepwiseReport) -> StepwiseReport:
        """"""
        x_data = sm.add_constant(self.df[columns], has_constant='add')
        y_data = target
        report.num_features = len(columns)
        try:
            model = sm.Logit(y_data, x_data).fit(disp=0)
            report = self.implication(model, columns, report)
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
            indicator: Optional[Literal["auc", "ks", "lift"]] = 'auc',
            early_stop: Optional[float] = None,
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

    def _validate_early_stop(
            self,
            steps_type: Literal["forward", "backward"] = "forward"
    ):
        """"""
        if steps_type == "forward" and self.early_stop < 0:
            raise ValueError(f"early_stop increase {self.early_stop} must be greater than or equal to 0")

        if steps_type == "backward" and self.early_stop > 0:
            raise ValueError(f"early_stop decrease {self.early_stop} must be less than or equal to 0")

    def _prepare_data(self):
        if self.columns is None:
            self.columns = self.df.columns.tolist()

    def _get_candidate_columns(self):
        """"""
        self.candidate_columns = self.dependent.sort_values(by=str(self.indicator), ascending=False)[self.var_field].tolist()
        self.candidate_columns = [column for column in self.candidate_columns if column in self.columns]

    def _get_step_columns(
            self,
            i_step: int,
            steps_type: Literal["forward", "backward"] = "forward"
    ) -> List[str]:
        """"""
        if steps_type == "forward":
            columns = self.candidate_columns[: i_step + 1]
        else:
            if i_step == 0:
                columns = self.candidate_columns
            else:
                columns = self.candidate_columns[:-i_step]
        return columns

    def early_stop_monitor(
            self,
            steps: List[StepwiseReport],
            i_step: int,
            steps_type: Literal["forward", "backward"] = "forward",
    ) -> bool:
        """"""
        if isinstance(self.early_stop, float) and i_step > 0:
            pre_step = steps[i_step - 1]
            cur_step = steps[i_step]
            pre_indicator = pre_step.model_dump().get(str(self.indicator))
            cur_indicator = cur_step.model_dump().get(str(self.indicator))
            indicator_change = (cur_indicator - pre_indicator) / pre_indicator
            cur_step.indicator_change = indicator_change
            if indicator_change < self.early_stop:
                if steps_type == "forward":
                    self._logger(
                        msg=f"dependent {self.indicator} increase is {indicator_change:.4f} < {self.early_stop}, stop.",
                        color="blue")
                elif steps_type == "backward":
                    self._logger(
                        msg=f"dependent {self.indicator} decrease is {indicator_change:.4f} < {self.early_stop}, stop.",
                        color="blue")
                return True
            else:
                return False
        else:
            return False

    def steps(
            self,
            steps_type: Literal["forward", "backward"] = "forward"
    ) -> DataFrame:
        """"""
        self._get_candidate_columns()
        steps: List[StepwiseReport] = []

        if isinstance(self.early_stop, float):
            self._validate_early_stop(steps_type=steps_type)

        for i in range(len(self.candidate_columns)):
            columns = self._get_step_columns(i_step=i, steps_type=steps_type)
            step_report = StepwiseReport(feature=columns)
            step_report = self.step_fit(columns=columns, target=self.df[self.target_name], report=step_report)
            steps.append(step_report)
            if self.early_stop_monitor(steps=steps, i_step=i, steps_type=steps_type):
                break
        return pd.DataFrame([step.model_dump() for step in steps])

    def forward(self) -> DataFrame:
        """"""
        return self.steps("forward")

    def backward(self) -> DataFrame:
        """"""
        return self.steps("backward")

    @staticmethod
    def top_n_features(df_woe, var_name='var_name', sort_by='ks', top_n=3, dim='dim'):
        """
        描述：依据指标的效果排序筛选指标。
        :param df_woe:
        :param var_name:
        :param sort_by:
        :param top_n:
        :param dim:
        :return:
        """
        columns = [var_name, 'des', 'ks', 'auc', 'dim']
        df_features = pd.DataFrame(columns=columns)
        df_woe = df_woe[columns].drop_duplicates()
        for group_name, group in df_woe.groupby(dim):
            df_group = group.copy()
            df_group.sort_values(sort_by, ascending=False, inplace=True)
            df_features = df_features.append(df_group.head(top_n))
        return df_features
