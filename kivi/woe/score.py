import pandas as pd
from pandas import DataFrame
from typing import Any, List, Callable, Literal, Optional
from ..utils import dispatch_tqdm, batches
from ..utils.logger import LoggerMixin


__all__ = [
    'WOEScore'
]


class WOEScore(LoggerMixin):
    """"""
    def __init__(
            self,
            df: DataFrame,
            df_woe: DataFrame,
            id_name: Optional[str] = 'uuid',
            target_name: Optional[str] = 'target',
            dtype: Optional[str] = 'float',
            batch_size: Optional[int] = 32,
            error='error',
            logger: Optional[Callable] = None,
            verbose: Optional[bool] = True,
            *args: Any,
            **kwargs: Any

    ):
        """
        :param df: 原始数据
        :param df_woe: woe编码后的数据
        :param id_name: uuid
        :param target_name: 目标变量名称，默认为 target
        :param dtype: 数据类型，默认为float
        :param batch_size: 批量大小，默认为32
        :param error: 错误处理方式，默认为error
        :param logger: 日志记录器，默认为None
        :param verbose: 是否显示进度条，默认为True
        """
        self.df = df
        self.df_woe = df_woe
        self.id_name = id_name
        self.target_name = target_name
        self.dtype = dtype
        self.batch_size = batch_size
        self.error = error
        self.logger = logger
        self.verbose = verbose
        self.args = args
        self.kwargs = kwargs

        self._validate_data()
        self._prepare_data()
        self.df_private = self.df[[id_name, target_name]].copy()

    def _validate_data(self):
        """"""
        if len(self.df) != len(self.df[self.id_name].unique()):
            raise ValueError('uuid is not unique, please check your data.')

        if self.id_name not in self.df.columns.tolist():
            raise ValueError(f'uuid {self.id_name} not in columns, please check your data.')

        if self.target_name not in self.df.columns.tolist():
            raise ValueError(f'target {self.target_name} not in columns, please check your data.')

    def _prepare_data(self):
        """"""
        self.df.reset_index(inplace=True, drop=True)

    def _trans_columns(self, columns: Optional[List[str]] = None):
        """"""
        if columns is None:
            columns = self.df.columns.tolist()
        for _drop in [self.id_name, self.target_name]:
            if _drop in columns:
                columns.remove(_drop)
        woe_columns = self.df_woe.var_name.unique().tolist()
        columns = list(set(woe_columns) & set(columns))
        return columns

    def wide_to_long(self, df_wide: DataFrame, columns: Optional[List[str]] = None) -> DataFrame:
        """ 宽表转为长表，用于WOE分数转换 """
        df_long = df_wide[columns].add_prefix('values_').join(self.df_private[[self.id_name]])
        df_long = pd.wide_to_long(
            df_long, stubnames='values',
            i=self.id_name, j='var_name', sep='_', suffix='\w+'
        )
        df_long.reset_index(inplace=True)
        df_long.reset_index(inplace=True, drop=True)
        df_long['values'] = df_long['values'].astype(self.dtype)
        return df_long

    def _match_miss_score(self, df_merge_score: DataFrame) -> DataFrame:
        """"""
        cond_miss = df_merge_score[['values', 'min_bin', 'max_bin']].isna().all(axis=1)
        df_miss_score = df_merge_score[cond_miss].copy()
        return df_miss_score

    def _match_normal_score(self, df_merge_score: DataFrame) -> DataFrame:
        """"""
        cond_normal = df_merge_score[['values', 'min_bin', 'max_bin']].isna().any(axis=1)
        df_score = df_merge_score[~cond_normal].copy()

        cond_eq = (df_score['values'] == df_score.min_bin) & (df_score['values'] == df_score.max_bin)
        cond_mid = (df_score['values'] > df_score.min_bin) & (df_score['values'] <= df_score.max_bin)
        cond_score = cond_mid | cond_eq

        df_score = df_score[cond_score]
        return df_score

    def match_woe(self, df_long: DataFrame, df_woe: DataFrame) -> DataFrame:
        """ """
        df_merge_score = df_long.merge(df_woe, on='var_name', how='left')
        df_normal_score = self._match_normal_score(df_merge_score)
        df_miss_score = self._match_miss_score(df_merge_score)
        df_score = pd.concat([df_normal_score, df_miss_score], axis=0, ignore_index=True)

        if self.error == 'error':
            if df_score.shape[0] != df_long.shape[0]:
                raise ValueError(f'sample shape {df_score.shape[0]} not match origin dataset shape {df_long.shape[0]}.')
        elif self.error == 'ignore':
            if df_score.shape[0] > df_long.shape[0]:
                self._logger(msg=f'Mutil Bins! {df_score.shape}, {df_long.shape}', color="red")
            elif df_score.shape[0] < df_long.shape[0]:
                self._logger(msg=f'Bins Margin Warn! {df_score.shape}, {df_long.shape}', color="red")
        return df_score

    def trans_woe_score(
            self,
            columns: Optional[List[str]] = None,
            values: Optional[Literal['woe', 'score']] = "score",
            add_target: Optional[bool] = True,
            batch_info: Optional[str] = None,
    ) -> DataFrame:
        """ 两种种WOE映射值 """
        columns = self._trans_columns(columns=columns)
        df_select = self.df[columns].copy()
        df_woe_select = self.df_woe[self.df_woe.var_name.isin(columns)].copy()

        if batch_info:
            logger_name = f"[{__class__.__name__}] {batch_info}"
        else:
            logger_name = f"[{__class__.__name__}]"

        self._logger(msg=f'{logger_name} Wide to Long ...', color="green")
        df_long = self.wide_to_long(df_select, columns=columns)
        self._logger(msg=f'{logger_name} Match WOE ...', color="green")
        df_score_long = self.match_woe(df_long=df_long, df_woe=df_woe_select)
        self._logger(msg=f'{logger_name} Match Over ...', color="green")

        df_score_wide = df_score_long.pivot(index=self.id_name, columns='var_name', values=values)
        if add_target:
            df_score_wide = df_score_wide.join(self.df_private.set_index(self.id_name), on=self.id_name)
        df_score_wide.sort_index(inplace=True)
        return df_score_wide

    def batch_run(
            self,
            columns: Optional[List[str]] = None,
            values: Optional[Literal['woe', 'score']] = "score",
            id_index: Optional[bool] = False,
    ):
        """ """
        columns = self._trans_columns(columns=columns)
        self._logger(msg=f"Start Trans WOE Score, total columns number is {len(columns)} ...", color="green")
        batch_list = [batch for batch in batches(lst=columns, batch_size=self.batch_size)]
        _batches = []
        batch_idx = 1
        for batch_columns in dispatch_tqdm(batch_list, desc=f'[{__class__.__name__}] WOE Batch'):
            df_batch = self.trans_woe_score(
                columns=batch_columns, values=values, add_target=False, batch_info=f'[{batch_idx} / {len(batch_list)}]')
            _batches.append(df_batch)
            batch_idx += 1
        df_score = pd.concat(_batches, axis=1, join="outer",)
        df_score = df_score.join(self.df_private.set_index(self.id_name), on=self.id_name)
        if not id_index:
            df_score.reset_index(inplace=True)
        return df_score
