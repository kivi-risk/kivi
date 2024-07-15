import sys
import pandas as pd
from pandas import DataFrame
from typing import Any, Dict, List, Tuple, Callable, Optional
from ..utils.utils import dispatch_tqdm
from ..utils.logger import LoggerMixin
from .woe_obj import *


__all__ = [
    "ManualBinsTool",
    "WOEBatch",
]


class ManualBinsTool(LoggerMixin):
    """
    """
    def __init__(
            self,
            df: Optional[DataFrame] = None,
            target_name: Optional[str] = 'target',
            abnormal_vals: Optional[List[Union[str, int, float]]] = None,
            logger: Optional[Callable] = None,
            verbose: Optional[bool] = True,
            *args: Any,
            **kwargs: Any
    ):
        """
        :param df: 数据集
        :param target_name: 目标变量名
        :param abnormal_vals: 异常值
        :param logger: 日志
        :param verbose: 是否打印日志
        """
        self.df = df
        self.target_name = target_name
        self.abnormal_vals = abnormal_vals
        self.logger = logger
        self.verbose = verbose
        self.args = args
        self.kwargs = kwargs

    @staticmethod
    def append_rebin_woe(df_woe: DataFrame, df_rebin: DataFrame) -> DataFrame:
        """
        为原始分箱增加其他类型分箱
        :param df_woe: 原始分箱
        :param df_rebin: 手工分箱
        """
        var_names = df_rebin.var_name.unique().tolist()
        df_origin = df_woe[df_woe.var_name.isin(var_names)].copy()
        
        origin_columns = df_origin.columns.tolist()
        rebin_columns = df_rebin.columns.tolist()
        subtract_columns = list(set(origin_columns) - set(rebin_columns)) + ['var_name']
    
        df_rebin = df_rebin.merge(df_origin[subtract_columns].drop_duplicates(), on='var_name')
        df_rebin = df_rebin[origin_columns]
    
        df_woe = df_woe[~df_woe.var_name.isin(var_names)]
        df_woe = pd.concat([df_woe, df_rebin], axis=0, ignore_index=True)
        return df_woe
    
    def manual_rebin(
            self,
            column: str,
            bins: List[Union[float, int]],
    ) -> DataFrame:
        """ 描述：指定分箱阈值进行重分箱。 """
        bins = ManuallyBins(
            variables=self.df[column], target=self.df[self.target_name],
            bins=bins, fill_bin=True, abnormal_vals=self.abnormal_vals)
        df_rebin_woe = bins.fit()
        ipython_woe = df_rebin_woe.style.bar(
            subset=['bad_rate', 'woe', 'score'],
            align='mid', color=['#d65f5f', '#5fba7d'],)
        if self.verbose:
            if 'ipykernel' in sys.modules:
                from IPython.display import display
                display(ipython_woe)
            else:
                print(df_rebin_woe)
        return df_rebin_woe


class WOEBatch(LoggerMixin):
    """
    todo: 自动判断分箱的数据类型，对类别型变量选择合适的分箱方式。需要检测类别的数目。
    todo: 按照月份进行跑批，规避不同月份中出现同一UUID的情况
    """
    def __init__(
            self,
            df: DataFrame,
            bins: Optional[Union[int, Dict[str, List[Union[float, int]]]]] = 5,
            max_bin: Optional[int] = 6,
            min_bin: Optional[int] = 3,
            rebin: Optional[bool] = True,
            woe_type: TypeWoe = TreeBins,
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
        :param bins[int, dict]: [int]分箱数量，默认为 5；[dict(var_name: bins)]依据截断点分箱。
        :param max_bin: 允许最大分箱数量。
        :param min_bin: 允许最小分箱数量。
        :param rebin: 是否重新分箱，默认为 `True`。
        :param woe_type: 分箱方法，默认为决策树分箱 `TreeBins`。
        :param woe_columns: 需要进行分箱的字段，默认为全部字段。
        :param target_name: 标签名称，默认为 `target`。
        :param observe_order: 保留分箱单调性，默认为 `['单调上升','单调下降']`；即对不满足条件的数据进行重分箱。
        :param abnormal_vals: 需要剔除异常值，如[-9099, -4404]
        :param protect_columns: 需要剔除分箱的字段, 如不需要进行分箱的字段['uuid', 'target']。
        :param logger: 日志记录器，默认为 `None`。
        :param verbose: 是否打印分箱日志，默认为 `False`。

        Example：
            df_woe = WOEBatch(df, rebin=False)
            df_woe = WOEBatch(df, max_bins=5, min_bins=2, rebin=True)
        """
        self.df = df
        self.bins = bins
        self.max_bin = max_bin
        self.min_bin = min_bin
        self.woe_type = woe_type
        self.woe_columns = woe_columns
        self.target_name = target_name
        self.abnormal_vals = abnormal_vals
        self.rebin = rebin
        self.logger = logger
        self.verbose = verbose
        self.args = args
        self.kwargs = kwargs

        self.woe_container = []
        self.error_woe_columns = []
        if protect_columns is None:
            self.protect_columns = ["uuid", "target"]
        else:
            self.protect_columns = protect_columns
        if observe_order is None:
            self.observe_order = ['单调上升', '单调下降']
        self._get_woe_columns()

    def __call__(self, *args, **kwargs):
        """"""

    def _get_woe_columns(self):
        """"""
        total_columns = self.df.columns.tolist()
        if self.woe_columns is None:
            for column in self.protect_columns:
                if column in total_columns:
                    total_columns.remove(column)
            self.woe_columns = total_columns

    def _detect_observe_bins(self, df_woe: DataFrame) -> Tuple[DataFrame, DataFrame, List[str]]:
        """"""
        df_woe_observe = df_woe[df_woe.order.isin(self.observe_order)].copy()
        df_woe_rebin = df_woe[~df_woe.order.isin(self.observe_order)].copy()
        rebin_columns = df_woe_rebin.var_name.unique().tolist()
        return df_woe_observe, df_woe_rebin, rebin_columns

    def woe_batch(self,) -> DataFrame:
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

    def _set_woe_batch(self, woe_columns: Optional[List[str]] = None) -> DataFrame:
        """"""
        if woe_columns:
            self.woe_columns = woe_columns
        self.bins = self.max_bin
        self.woe_container = []
        df_woe = self.woe_batch()
        return df_woe

    def woe_batch_with_rebin(self, ) -> DataFrame:
        """"""
        df_woe = self._set_woe_batch()
        df_woe_observe, df_woe_rebin, rebin_columns = self._detect_observe_bins(df_woe)

        self._logger(msg=f'[{__class__.__name__}] Bins: {self.max_bin}; Success: {len(df_woe_observe)}; Rebin: {len(df_woe_rebin)}; Error: {len(self.error_woe_columns)}', color='green')
        df_woe_total = df_woe_observe.copy()

        self.max_bin -= 1
        while len(rebin_columns) > 0 and self.max_bin >= self.min_bin:
            df_woe = self._set_woe_batch(woe_columns=rebin_columns)
            df_woe_observe, df_woe_rebin, rebin_columns = self._detect_observe_bins(df_woe)
            df_woe_total = pd.concat([df_woe_total, df_woe_observe], axis=0, ignore_index=True)
            self._logger(
                msg=f'[{__class__.__name__}] Bins: {self.max_bin}; Success: {len(df_woe_observe)}; Rebin: {len(df_woe_rebin)}; Error: {len(self.error_woe_columns)}', color='green')
            self.max_bin -= 1
        df_woe_total = pd.concat([df_woe_total, df_woe_rebin], axis=0, ignore_index=True)
        return df_woe_total

    def fit(self) -> DataFrame:
        """"""
        if self.rebin:
            df_woe = self.woe_batch_with_rebin()
        else:
            df_woe = self.woe_batch()
        return df_woe
