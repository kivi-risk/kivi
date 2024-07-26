import numpy as np
import pandas as pd
from pandas import DataFrame
from typing import Any, Dict, Tuple, Callable, Sequence, Optional
from ..utils.logger import LoggerMixin


__all__ = ['AHP']


class AHP(LoggerMixin):
    """"""
    df_weight: DataFrame

    def __init__(
            self,
            metrix: DataFrame,
            value: Optional[str] = 'value',
            control: Optional[str] = 'control',
            experimental: Optional[str] = 'experimental',
            logger: Optional[Callable] = None,
            verbose: Optional[bool] = True,
            *args: Any,
            **kwargs: Any,
    ):
        """"""
        self.metrix = metrix
        self.value = value
        self.control = control
        self.experimental = experimental
        self.metrix_weight = dict()
        self.metrix_data = dict()
        self.group_ci = dict()
        self.group_cr = dict()
        self.ri = {
            1: 1e-6, 2: 1e-6, 3: 0.58, 4: 0.9, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49,
            11: 1.51, 12: 1.54, 13: 1.56, 14: 1.58, 15: 1.59, 16: 1.60,
        }
        self.logger = logger
        self.verbose = verbose
        self.args = args
        self.kwargs = kwargs
        self._validate_data()

    def _validate_data(self):
        """"""
        for column in [self.value, self.control, self.experimental]:
            if column not in self.metrix.columns:
                raise KeyError(f"Column {column} not found in metrix.")

        for group_name, df_group in self.metrix.groupby("group"):
            group_shape = df_group.shape
            group_index_len = df_group[self.control].nunique()
            if group_shape[0] != group_index_len ** 2:
                raise ValueError(f"Metrix <{group_name}> shape {group_shape[0]} is not equal to {group_index_len ** 2}")

    def geometric_mean(self, numbers: Sequence) -> float:
        """"""
        return np.power(np.prod(numbers), 1 / len(numbers))

    def _ci_cr(self, metrix: DataFrame, metrix_weight: DataFrame, metrix_name: str) -> Tuple[float, float]:
        """
        计算一致性指标CI
        CI = (λ_avg - n) / (n - 1)
        CR = CI / RI
        """
        lambda_avg = (metrix.dot(metrix_weight.weight) / metrix_weight.weight).mean()
        _len = len(metrix_weight)
        ci = (lambda_avg - _len) / (_len - 1)
        if _len <= 2:
            cr = 0
        else:
            cr = ci / self.ri.get(_len)
        self.group_ci.update({metrix_name: ci})
        self.group_cr.update({metrix_name: cr})
        if cr > 0.1:
            self._logger(msg=f"[{__class__.__name__}] Metrix: <{metrix_name}> CR = {cr:.2f} CR is too large, please check your metrix.", color="red")
        else:
            self._logger(msg=f"[{__class__.__name__}] Metrix: <{metrix_name}> CR = {cr:.2f}", color="green")
        return ci, cr

    def solve_metrix(self):
        for group_name, df_group in self.metrix.groupby("group"):
            metrix = df_group.pivot_table(values="value", columns=['control'], index=["experimental"])
            metrix_weight = pd.DataFrame(
                metrix.apply(self.geometric_mean, axis=1),
                columns=["geo_mean"]
            )
            metrix_weight["weight"] = metrix_weight.geo_mean / metrix_weight.geo_mean.sum()
            ci, cr = self._ci_cr(metrix, metrix_weight, metrix_name=str(group_name))
            self.metrix_data.update({group_name: metrix})
            self.metrix_weight.update({group_name: metrix_weight})

    def weight(
            self,
    ) -> DataFrame:
        """"""
        df_weight = pd.concat([weight.reset_index(drop=False) for key, weight in self.metrix_weight.items()])
        df_weight.rename(columns={"experimental": "dst", "weight": "group_weight"}, inplace=True)
        self.df_weight = df_weight.reset_index(drop=True)
        return self.df_weight
