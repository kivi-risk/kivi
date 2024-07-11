from typing import List, Dict, Union, Callable, Optional
from pyspark.sql import functions as F
from pyspark.sql import SparkSession
from pyspark.sql import DataFrame
from pyspark.sql.types import FloatType
from itertools import product
from ..spark import insert_into_hive
from .operator import *
from .schema import *
from .utils import *
from .date import *


__all__ = [
    "CollectIndex"
]


class CollectIndex(LoggerMixin):
    """"""
    index_schema_list = ['uuid', 'index_name', 'index_val', 'load_date']

    def __init__(
            self,
            df: Optional[DataFrame],
            index_fields: List[IndexField],
            spark: SparkSession,
            reset: Optional[bool] = False,
            group_mapping: Optional[Dict[str, str]] = None,
            decimal: Optional[int] = 6,
            logger: Optional[Callable] = None,
            verbose: Optional[bool] = False,
    ):
        self.df = df
        self.index_fields = index_fields
        self.spark = spark
        self.reset = reset
        self.group_mapping = group_mapping
        self.decimal = decimal
        self.logger = logger
        self.verbose = verbose

    def __call__(self, *args, **kwargs):
        """"""
        self.run()

    def _get_data(self, df: DataFrame, column: Union[List[str], str], start_date: str, end_date: str):
        """"""
        self._logger(msg=f"[{__class__.__name__}] Get data from {column} between {start_date} and {end_date}]")
        df = df.where(F.col("load_date").between(start_date, end_date))
        self._logger(msg=f"[{__class__.__name__}] In fact load_date: {len(df.select('load_date').distinct().collect())}")
        select_columns = ["uuid", "load_date"]
        if isinstance(column, str):
            select_columns.append(column)
        else:
            select_columns.extend(column)
        return df.select(select_columns)

    # def _run_core(self, df_origin: DataFrame) -> DataFrame:
    #     """"""
    #     df_origin = get_operator_data(df=)
    #     return df_origin

    def _run_basic(self):
        """"""

    def _run_qoq(self):
        """"""

    def _run_yoy(self):
        """"""

    def _save_index(self, df: DataFrame, index_field: IndexField, load_date: str, index_name: str):
        """"""
        insert_into_hive(
            df, db_name=index_field.save_db, table_name=index_field.save_table, spark=self.spark,
            partition=['load_date', 'index_name'], partition_val=[load_date, index_name],
        )
        self._logger(msg=f"[{__class__.__name__}] Save index data to {index_field.save_db}.{index_field.save_table}")

    def _one_column(
            self,
            index_field: IndexField,
            operate_name: str,
            month: Union[int, str],
            id_level: str,
            alias_operator: Optional[str] = None
    ):
        """"""
        collect_index_name = merge_index_name(
            id_level=id_level, index_name=index_field.index_name,
            operate_name=operate_name, month=month, alias_operator=alias_operator)
        self._logger(msg=f"[{__class__.__name__}] current index name: {collect_index_name}\n")
        start_date = get_start_and_end_date(biz_date=index_field.load_date, month=month)
        self.df_origin = self._get_data(
            df=self.df, column=index_field.columns, start_date=start_date, end_date=index_field.load_date)
        group_col = self.group_mapping.get(id_level)

        if isinstance(index_field.columns, str):
            agg_columns = [index_field.columns]
        else:
            agg_columns = index_field.columns
        agg_columns = [F.col(column).cast(FloatType()) for column in agg_columns]
        df_agg = self.df_origin.groupBy(group_col).agg(
            operator_mapping.get(operate_name)(*agg_columns).alias("index_val")
        )
        df_agg = df_agg.withColumn("index_val", F.round(df_agg["index_val"], self.decimal))
        df_agg = df_agg.withColumn("index_name", F.lit(collect_index_name))
        df_agg = df_agg.withColumn("load_date", F.lit(index_field.load_date))
        df_agg = df_agg.select(self.index_schema_list)
        self._save_index(
            df=df_agg, index_field=index_field, load_date=index_field.load_date, index_name=collect_index_name)
        return df_agg

    def _loop_load_date(
            self,
            index_field: IndexField,
            operate_name: str,
            month: Union[int, str],
            id_level: str
    ) -> DataFrame:
        """"""
        if index_field.alias_operators:
            alias_operator = index_field.alias_operators[index_field.operators.index(operate_name)]
        else:
            alias_operator = None
        df_agg = self._one_column(
            index_field=index_field, operate_name=operate_name, month=month, id_level=id_level,
            alias_operator=alias_operator)
        return df_agg

    def _loop_date_periods(self):
        """"""

    def run(self):
        """"""
        for index_field in self.index_fields:
            for operate_name, month, id_level in product(index_field.operators, index_field.months, index_field.id_levels):
                if index_field.load_date:
                    df_agg = self._loop_load_date(index_field=index_field, operate_name=operate_name, month=month, id_level=id_level)
                elif index_field.start_date and index_field.end_date:
                    pass
                else:
                    raise Exception("[start_date/end_date] or [load_date] must be set.")
