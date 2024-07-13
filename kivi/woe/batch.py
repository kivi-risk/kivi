import pandas as pd
from pandas import DataFrame as TypePandasDataFrame
from typing import Any, Dict, List, Tuple, Union, Callable, Optional
from IPython.display import display

from ..utils.utils import dispatch_tqdm
from ..utils.logger import LoggerMixin
from .woe_obj import *


__all__ = [
    "AppendRebinWoe",
    "Rebins",
    "WOEBatch",
    "_WOEBatch",
    "_WOEBatchWithRebin",
]


def AppendRebinWoe(df_woe, df_rebin):
    """
    描述：为原始分箱增加其他类型分箱。

    :param df_woe: 全量分箱。
    :param df_rebins: 补充分箱。
    :return: DataFrame
    """
    var_names = df_rebin.var_name.unique().tolist()
    df_origin = df_woe[df_woe.var_name.isin(var_names)].copy()

    origin_columns = df_origin.columns.tolist()
    rebin_columns = df_rebin.columns.tolist()
    subtract_columns = list(set(origin_columns) - set(rebin_columns)) + ['var_name']

    df_rebin = df_rebin.merge(df_origin[subtract_columns].drop_duplicates(), on='var_name')
    df_rebin = df_rebin[origin_columns]

    df_woe = df_woe[~df_woe.var_name.isin(var_names)]
    df_woe = df_woe.append(df_rebin)
    return df_woe


def Rebins(df, col_name, bins, target_name='target', abnormal_vals=[]):
    """
    描述：指定分箱阈值进行重分箱。
    :param df: DataFrame 数据。
    :param col_name: 需要进行重分箱的指标名称。
    :param bins: 分箱的截断点。
    :param target_name: 目标变量名称。
    :return:
    """
    target, x = df[target_name], df[col_name]
    cut = ManuallyBins(x, target, cutoffpoint=bins, fill_bin=True, abnormal_vals=abnormal_vals)
    df_rebin_woe = cut.fit()
    df_rebin_woe = df_rebin_woe.style.bar(
        subset=['bad_rate', 'woe', 'score'],
        align='mid', color=['#d65f5f', '#5fba7d'],)
    display(df_rebin_woe)


class WOEBatch(LoggerMixin):
    """"""
    def __init__(
            self,
            df: TypePandasDataFrame,
            bins: Optional[Union[int, Dict[str, List[Union[float, int]]]]] = 5,
            max_bin: Optional[int] = 6,
            min_bin: Optional[int] = 3,
            woe_type: Optional[TypeWoe] = TreeBins,
            woe_columns: Optional[List[str]] = None,
            target_name: Optional[str] = "target",
            observe_order: Optional[List[str]] = None,
            abnormal_vals: Optional[List[Union[str, int, float]]] = None,
            protect_columns: Optional[List[str]] = None,
            logger: Optional[Callable] = None,
            verbose: Optional[bool] = False,
            *args: Any,
            **kwargs: Any,
    ):
        """
        描述：批量计算WOE IV值

        参数：
        :param df: DataFrame 原始数据集。
        :param bins[int, dict]: [int]分箱数量，默认为5；[dict(var_name: bins)]依据截断点分箱。
        :param max_bin: 允许最大分箱数量。
        :param min_bin: 允许最小分箱数量。
        :param woe_type: 分箱方法，默认为决策树分箱 `Frequency`。
        :param woe_columns: 需要进行分箱的字段。
        :param target_name: 标签名称，默认为 `target`。
        :param observe_order: 保留分箱单调性，默认为 `['单调上升','单调下降']`；即对不满足条件的数据进行重分箱。
        :param protect_columns: 需要剔除分箱的字段。

        Example：
            df_woe, faulted_cols = WOEBatch(
                df, columns_name=df.drop('target', axis=1).columns, target_name='target')
        """
        self.df = df
        self.bins = bins
        self.max_bin = max_bin
        self.min_bin = min_bin
        self.woe_type = woe_type
        self.woe_columns = woe_columns
        self.target_name = target_name
        self.abnormal_vals = abnormal_vals
        self.logger = logger
        self.verbose = verbose
        self.args = args
        self.kwargs = kwargs

        self.woe_container = []
        self.error_woe_columns = []
        if protect_columns is None:
            self.protect_columns = ["uuid", "target"]
        if observe_order is None:
            self.observe_order = ['单调上升', '单调下降']
        self._get_woe_columns()

    def __call__(self, *args, **kwargs):
        """"""

    def _get_woe_columns(self):
        """"""
        if self.woe_columns is None:
            self.woe_columns = self.df.drop(self.protect_columns, axis=1).columns.tolist()

    def _detect_observe_bins(self, df_woe: TypePandasDataFrame) -> Tuple[TypePandasDataFrame, TypePandasDataFrame, List[str]]:
        """"""
        df_woe_observe = df_woe[df_woe.order.isin(self.observe_order)].copy()
        df_woe_rebin = df_woe[~df_woe.order.isin(self.observe_order)].copy()
        rebin_columns = df_woe_rebin.var_name.unique().tolist()
        return df_woe_observe, df_woe_rebin, rebin_columns

    def woe_batch(self,) -> TypePandasDataFrame:
        """"""
        self._logger(msg=f"[{__class__.__name__}] WOE Batch samples shape: {self.df.shape}.\n", color="green")
        for woe_column in dispatch_tqdm(self.woe_columns, desc=f'[{__class__.__name__}] Batch WOE'):
            try:
                if isinstance(self.woe_type, ManuallyBins):
                    _bins = self.bins.get(woe_column)
                else:
                    _bins = self.bins
                woe_fun = self.woe_type(
                    variables=self.df[woe_column],
                    target=self.df[self.target_name],
                    abnormal_vals=self.abnormal_vals,
                    bins=_bins,
                    **self.kwargs
                )
                woe = woe_fun.fit()
                self.woe_container.append(woe)
            except Exception as e:
                self._logger(msg=f"[{__class__.__name__}] {woe_column} WOE Error: {e}", color="red")
                self.error_woe_columns.append({woe_column: e})
        df_woe = pd.concat(self.woe_container, axis=0, ignore_index=True)
        return df_woe

    def woe_batch_with_rebin(self, ) -> TypePandasDataFrame:
        """"""
        df_woe = self.woe_batch()
        df_woe_observe, df_woe_rebin, rebin_columns = self._detect_observe_bins(df_woe)

        self._logger(msg=f'[{__class__.__name__}] Bins: {self.max_bin}; Success: {len(df_woe_observe)}; Rebin: {len(df_woe_rebin)}; Error: {len(self.error_woe_columns)}', color='green')
        df_woe_total = df_woe_observe.copy()

        self.max_bin -= 1
        while len(rebin_columns) > 0 and self.max_bin >= self.min_bin:
            df_woe = self.woe_batch()
            df_woe_observe, df_woe_rebin, rebin_columns = self._detect_observe_bins(df_woe)
            df_woe_total = pd.concat([df_woe_total, df_woe_observe], axis=0, ignore_index=True)
            self._logger(
                msg=f'[{__class__.__name__}] Bins: {self.max_bin}; Success: {len(df_woe_observe)}; Rebin: {len(df_woe_rebin)}; Error: {len(self.error_woe_columns)}', color='green')
            self.max_bin -= 1
        df_woe_total = pd.concat([df_woe_total, df_woe_rebin], axis=0, ignore_index=True)
        return df_woe_total


def _WOEBatch(df, columns_name, target_name, WOEFun=FrequencyBins, bins:[int, dict]=5, abnormal_vals=[], **kwargs):
    """
    描述：批量计算WOE IV值

    参数：
    :param df: DataFrame 原始数据集。
    :param columns_name: 需要进行分箱的字段。
    :param target_name: 标签名称，默认为 `target`。
    :param WOEFun: 分箱方法，默认为决策树分箱 `Frequency`。
    :param bins[int, dict]: [int]分箱数量，默认为5；[dict(var_name: bins)]依据截断点分箱。

    :return:

    示例：
    >>> df_woe, faulted_cols = WOEBatch(
    >>>     df, columns_name=df.drop('target', axis=1).columns,
    >>>     target_name='target')
    """
    print(f'Samples shape: {df.shape}.')
    faulted_cols = []
    woe_container = []
    for col_name in dispatch_tqdm(columns_name, desc='计算WOE'):
        try:
            if WOEFun == CategoryBins:
                woe_fun = WOEFun(df[col_name], df[target_name], abnormal_vals=abnormal_vals)
            elif WOEFun == ManuallyBins:
                woe_fun = WOEFun(df[col_name], df[target_name], cutoffpoint=bins.get(col_name), fill_bin=True, abnormal_vals=abnormal_vals)
            elif WOEFun in [TreeBins, ManuallyBins]:
                woe_fun = WOEFun(df[col_name], df[target_name], bins=bins, fill_bin=True, abnormal_vals=abnormal_vals, **kwargs)
            elif WOEFun in [Chi2Bins]:
                woe_fun = WOEFun(df[col_name], df[target_name], fill_bin=True, init_bins=20, min_bins=2, max_bins=bins, abnormal_vals=abnormal_vals)
            else:
                Exception(ValueError, 'Bin Type Error!')
            woe = woe_fun.fit()
            woe.reset_index(inplace=True)
            woe_container.append(woe)
        except Exception as e:
            faulted_cols.append({col_name: e})
    print(faulted_cols)
    print(f'Faulted columns: {len(faulted_cols)}')
    print(len(woe_container))
    df_woe = pd.concat(woe_container, axis=0, ignore_index=True)
    if len(faulted_cols) == 0:
        return df_woe, None
    else:
        return df_woe, faulted_cols


def _WOEBatchWithRebin(
        df, target_name='target', WOEFun=TreeBins, bins_type=['单调上升','单调下降'],
        max_bin=5, min_bin=2, columns_name=None, drop_columns=['uuid', 'target'], **kwargs):
    """
    描述：`WOEMixin` 计算批量化并进行自动合并分箱。

    参数：
    :param df: DataFrame 原始数据集。
    :param target_name: 标签名称，默认为 `target`。
    :param WOEFun: 分箱方法，默认为决策树分箱 `TreeBins`。
    :param bins_type: 保留分箱单调性，默认为 `['单调上升','单调下降']`；即对不满足条件的数据进行重分箱。
    :param max_bin: 允许最大分箱数量。
    :param min_bin: 允许最小分箱数量。
    :param columns_name: 需要进行分箱的字段。
    :param drop_columns: 需要剔除分箱的字段。
    :return:
    """
    bins = max_bin

    df_woe_total = pd.DataFrame()
    fault_cols = []

    if drop_columns and columns_name is None:
        columns_name = df.drop(drop_columns, axis=1).columns.tolist()

    df_woe, fault_col = WOEBatch(
        df=df, columns_name=columns_name, target_name=target_name, WOEFun=WOEFun, bins=bins, **kwargs)

    df_woe_monot = df_woe[df_woe.order.isin(bins_type)].copy()
    df_woe_rebin = df_woe[~df_woe.order.isin(bins_type)].copy()
    columns_rebin = df_woe_rebin.var_name.unique().tolist()

    print(f'bins: {bins}; columns_rebin: {len(columns_rebin)}; fault: {fault_cols}')
    df_woe_total = df_woe_monot.copy()
    fault_cols.append(fault_col)

    bins -= 1
    while len(columns_rebin) > 0 and bins >= min_bin:
        df_woe_new, fault_col_new = WOEBatch(
            df=df, columns_name=columns_rebin, target_name=target_name, WOEFun=WOEFun, bins=bins, **kwargs)
        df_woe_monot = df_woe_new[df_woe_new.order.isin(bins_type)].copy()
        df_woe_rebin = df_woe_new[~df_woe_new.order.isin(bins_type)].copy()
        columns_rebin = df_woe_rebin.var_name.unique().tolist()

        df_woe_total = pd.concat([df_woe_total, df_woe_monot], axis=0)
        fault_cols.append(fault_col_new)

        print(f'bins: {bins}; columns_rebin: {len(columns_rebin)}; fault: {fault_col_new}')
        bins -= 1

    df_woe_total = pd.concat([df_woe_total, df_woe_rebin], axis=0)
    return df_woe_total, fault_cols

