import numpy as np
import pandas as pd
from typing import Optional, Literal, Tuple, Union, List, Any
from pandas.api.types import is_numeric_dtype
from kivi.evaluate.utils import BinsMixin
from kivi.evaluate.BucketsUtils import psi


__all__ = ['PSI']


class PSI(BinsMixin):
    cut_bins: Optional[List[float]]

    def __init__(
            self,
            expected: pd.Series,
            actual: pd.Series,
            bins: Union[int, float, List[Union[int, float]]] = 10,
            cut: Literal["cut", "qcut"] = 'cut',
            _min: Optional[float] = None,
            _max: Optional[float] = None,
            abnormal_vals: Optional[List[Union[str, int, float]]] = None,
            return_columns: Optional[List[str]] = None,
            decimal: Optional[int] = 6,
            **kwargs: Any,
    ):
        """
        计算 PSI
        :param expected: 期望数据
        :param actual: 实际数据
        :param bins: 分箱数目或分箱截断点
        :param cut: 分箱类型 等距`cut` 或 等频`qcut`
        :param _min: 最小值
        :param _max: 最大值
        :param abnormal_vals: 异常值
        :param return_columns: 返回列名
        :param decimal: 保留小数位数
        """
        self.expected = expected
        self.actual = actual
        self.bins = bins
        self.cut = cut
        self._min = _min
        self._max = _max
        self.abnormal_vals = abnormal_vals
        self.return_columns = return_columns
        self.decimal = decimal
        self.cut_bins = None
        self.kwargs = kwargs
        self.set_return_columns()
        self.is_numeric = self._validate_numeric()

    def set_return_columns(self):
        """"""
        if self.return_columns is None:
            self.return_columns = [
                "min_bin", "max_bin", "Expected", "Actual",
                "Expected_percentage", "Actual_percentage",
                "psi_val", "psi",
            ]

    def _validate_numeric(self) -> bool:
        """"""
        if all([is_numeric_dtype(data) for data in [self.expected, self.actual]]):
            return True
        else:
            return False

    def _get_bins(self):
        """"""
        if isinstance(self.bins, list):
            self.cut_bins = self.bins
        else:
            if self.cut == 'qcut':
                _, self.cut_bins = pd.qcut(self.expected, self.bins, retbins=True, duplicates='drop',)
            elif self.cut == 'cut' and self._min is not None and self._max is not None:
                self.cut_bins = np.linspace(self._min, self._max, self.bins + 1).tolist()
            elif self.cut == 'cut':
                _, self.cut_bins = pd.cut(self.expected, self.bins, retbins=True, include_lowest=True, duplicates='drop')
            self.cut_bins[0] = -np.inf
            self.cut_bins[-1] = np.inf

    def _miss_data_cnt(self) -> Optional[pd.DataFrame]:
        """"""
        sum_ex = sum(self.expected.isna())
        sum_ac = sum(self.actual.isna())
        if sum_ex > 0 or sum_ac > 0:
            na_bin = pd.DataFrame({
                'min_bin': [np.nan], 'max_bin': [np.nan], 'Expected': [sum_ex], 'Actual': [sum_ac],
            })
            return na_bin
        return None

    def _abnormal_val_cnt(self, ) -> Optional[pd.DataFrame]:
        """"""
        abnormal_data = []
        if isinstance(self.abnormal_vals, list):
            for val in self.abnormal_vals:
                sum_ex = (self.expected == val).sum()
                sum_ac = (self.actual == val).sum()
                abnormal_data.append(pd.DataFrame({
                    'min_bin': [val], 'max_bin': [val], 'Expected': [sum_ex], 'Actual': [sum_ac],
                }))
            return pd.concat(abnormal_data, axis=0)
        return None

    def prepare_data(self) -> Tuple[pd.Series, pd.Series]:
        """"""
        expected, actual = self.expected.dropna(), self.actual.dropna()
        if isinstance(self.abnormal_vals, list):
            expected = expected[~expected.isin(self.abnormal_vals)]
            actual = actual[~actual.isin(self.abnormal_vals)]
        return expected, actual

    def _normal_val(self) -> Optional[pd.DataFrame]:
        """"""
        expected, actual = self.prepare_data()
        df_ex = pd.DataFrame(pd.cut(expected, self.cut_bins, include_lowest=True).value_counts(sort=False))
        df_ac = pd.DataFrame(pd.cut(actual, self.cut_bins, include_lowest=True).value_counts(sort=False))
        df_psi = pd.concat([df_ex, df_ac], axis=1)
        df_psi.columns = ['Expected', 'Actual']
        df_psi = self.add_bins(df_psi.fillna(0))
        return df_psi

    def add_bins(self, df_psi: pd.DataFrame) -> pd.DataFrame:
        """"""
        df_psi['min_bin'] = self.cut_bins[: -1]
        df_psi['max_bin'] = self.cut_bins[1:]
        return df_psi

    def _value_decimal(self, psi: pd.DataFrame) -> pd.DataFrame:
        """"""
        decimal_columns = [
            "Expected_percentage", "Actual_percentage", "psi_val", "psi"
        ]
        for col in decimal_columns:
             psi[col] = psi[col].round(self.decimal)
        return psi

    def numeric(self):
        """"""
        self._get_bins()
        psi_data = [self._normal_val(), self._miss_data_cnt(), self._abnormal_val_cnt()]
        psi_data = [item for item in psi_data if item is not None]
        df_psi = pd.concat(psi_data, axis=0)
        return psi(df_psi, fill_bin=True)[self.return_columns]

    def _category(self) -> pd.DataFrame:
        """"""
        expected, actual = self.expected.dropna(), self.actual.dropna()
        df_psi = pd.concat([
            pd.DataFrame(expected.value_counts(sort=False)),
            pd.DataFrame(actual.value_counts(sort=False)),
        ], axis=1)
        df_psi.columns = ['Expected', 'Actual']
        df_psi["min_bin"] = df_psi.index
        df_psi["max_bin"] = df_psi.index
        df_psi.sort_index(inplace=True)
        return psi(df_psi, fill_bin=True)[self.return_columns]
    
    def fit(self, ) -> pd.DataFrame:
        """"""
        if self.is_numeric:
            df_psi = self.numeric()
        else:
            df_psi = self._category()
        df_psi = self._value_decimal(df_psi)
        return df_psi
