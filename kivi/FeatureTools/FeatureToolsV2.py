from tqdm import tqdm
from ..spark import unpivot, insert_into_hive, get_index_partition
from ..utils.date import date_range
from ..spark.operator import operator_mapping
from pyspark.sql import functions as F
from pyspark.sql.types import *
from ..spark import pct_rank


__all__ = [
    'one_batch_data',
    'features_agg',
    'batch_unpivot',
    'gen_batch_features',
]


def one_batch_data(df, now_date, month_range=[3, 6, 9, 12], fmt: str = 'yyyyMMdd'):
    """"""
    df = df.withColumn('now_date', F.lit(now_date))
    df = df.withColumn('month_diff', F.months_between(F.to_date('now_date', fmt), F.to_date('load_date', fmt)))

    batch_datas = [df.where(F.col('month_diff').between(0, month - 1)) for month in month_range]
    return batch_datas


def features_agg(batch_datas, column='info', month_range=[3, 6, 9, 12], operator=['cnt', 'sum', 'avg']):
    """

    :param batch_datas:
    :param column:
    :param month_range:
    :param operator: 计算算子，默认为['cnt', 'sum', 'avg']。支持以下算子：
        - 'cnt'
        - 'avg'
        - 'sum'
        - 'cnt_dist'
        - 'sum_dist'
        - "min"
        - "max"
        - "mean"
        - "first"
        - "last"
        - "skewness"
        - "kurtosis"
        - "collect_set"
        - "collect_list"
        - "approx_count_distinct"
        - 'stddev'
        - 'stddev_samp'
        - 'stddev_pop'
        - 'variance'
        - 'var_pop'
        - 'var_samp'
    :return:

    示例：
    >>> load_date = '20221130'
    >>> df_features_zzc = gen_batch_features(
    >>>     df_origin, column='zzc', now_date=load_date, month_range=[3, 6, 9, 12],
    >>>     operator=['cnt', 'sum'], spark=spark)
    >>> df_features_zzc.show()
    >>> df_origin
    +----+---+---+---------+
    |uuid|zzc|nsr|load_date|
    +----+---+---+---------+
    |   3| 81| 10| 20191231|
    |   3| 40| 73| 20200131|
    |   0| 24| 44| 20200229|
    |   2| 79| 75| 20200331|
    |   1| 22| 37| 20200430|
    |   3|  0| 10| 20200531|
    """
    agg_datas = []
    for batch_data, month in zip(batch_datas, month_range):

        op = [operator_mapping.get(item)(column).alias(f'ent_{column}_last_{month}_{item}') for item in operator]

        agg_data = batch_data.groupBy('uuid').agg(*op)
        agg_datas.append(agg_data)
    return agg_datas


def batch_unpivot(agg_features, now_date='20221130', spark=None):
    """"""
    schema = StructType([
        StructField("uuid", StringType(), True),
        StructField("index_name", StringType(), True),
        StructField("index_val", FloatType(), True),
    ])

    df = spark.createDataFrame([], schema=schema)

    for batch_feature in agg_features:
        columns = batch_feature.drop('uuid').columns
        df_batch = unpivot(
            batch_feature, columns, val_type=FloatType, index_name='uuid',
            feature_name='index_name', feature_value='index_val')
        df = df.unionAll(df_batch)

    df = df.withColumn('index_id', F.lit(''))
    df = df.withColumn('load_date', F.lit(now_date))
    return df


def gen_batch_features(
        df_origin, column='info', now_date='20221130',
        month_range=[3, 6, 9, 12], operator=['cnt', 'sum', 'avg'],
        spark=None):
    """
    描述：生成一个时间点的回溯跑批
    :param df_origin:
    :param column:
    :param now_date:
    :param month_range:
    :param operator: 计算算子，默认为['cnt', 'sum', 'avg']。
    :param spark:
    :return:
    """
    feature_datas = one_batch_data(df_origin, now_date=now_date, month_range=month_range)
    agg_features = features_agg(feature_datas, column=column, month_range=month_range, operator=operator)
    df_feature = batch_unpivot(agg_features, now_date=now_date, spark=spark)
    return df_feature


def batch_derivative_index(
        df_origin, column=None, start_date=None, end_date=None,
        db_name=None, table_name=None, insert=True, spark=None):
    """

    :param df_origin:
    :param column:
    :param start_date:
    :param end_date:
    :param insert:
    :param spark:
    :return:
    """
    dates = date_range(start_date, end_date)

    for load_date in tqdm(dates, desc=column):
        df_features = gen_batch_features(
            df_origin, column=column, now_date=load_date, month_range=[3, 6, 9, 12], spark=spark)

        index_names = df_features.select('index_name').distinct().collect()
        index_names = [item['index_name'] for item in index_names]

        df_features = df_features.select('uuid', 'index_val', 'index_id').persist()

        for index_name in index_names:

            df_features = df_features.where(F.col('index_name') == index_name)
            if df_features.count() > 0:
                if insert:
                    insert_into_hive(
                        df_features, db_name=db_name, table_name=table_name, spark=spark,
                        partition=['index_name', 'load_date'],
                        partition_val=[index_name, load_date], )
                else:
                    df_features.show()
            else:
                pass
        df_features.unpersist()

    return None


def index_indu_pct(db_name, table_name, spark, sqlContext, part_info=None, industry_level='l1_code', tmp_table_name='temp_table'):
    """
    描述：行业排名衍生
    :param db_name: 数据库名
    :param table_name: 数据表名，原始数据和新生成的行业排名指标将储存在同一库中。
    :param spark: spark session
    :param part_info: 跑批信息，[(load_date, column_name), (load_date, column_name)]
    :param industry_level: 行业级别，默认为`l1_code`。
    :param tmp_table_name: 临时表表名称，默认为`temp_table`。
    :return: None
    """

    industry_col = [
        'industry_l1_code','industry_l2_code','industry_l3_code','industry_l4_code',]

    if part_info is None:
        part_info = get_index_partition(db_name, table_name, spark)
    else:
        pass

    for load_date, col in part_info:
        pct_col = f'rank_indu_{col}'
        if ((load_date, pct_col) not in part_info) and (col not in industry_col) and ('rank_indu'not in col):
            df_index = spark.sql(f"""
                SELECT uuid, index_val FROM {db_name}.{table_name}
                WHERE load_date ='{load_date}'
                    AND index_val IS NOT NULL
                    AND index_name '{col}'
                """)
            df_index = df_index.where(F.col('index_val').isNotNull() & ~F.isnan('index_val'))
            df_index.write.mode("overwrite").parquet(tmp_table_name)
            df_index = sqlContext.read.parquet(tmp_table_name)
            df_index = df_index.persist()

            df_indu = spark.sql(f"""
                SELECT uuid, index_val AS indu
                FROM {db_name}.t_ent_index_basic
                WHERE load_date = '{load_date}'
                    AND index_name = 'industry_{industry_level}'
                """)
            if table_name == 't_ent_index_basic':
                df_indu.write.mode("overwrite").parquet('tmp_indu')
                df_indu = sqlContext.read.parquet('tmp_indu')

            df_indu = df_indu.persist()

            if df_index.count() > 0:
                df_index = df_index.join(df_indu, on='uuid', how='left')
                df_index = pct_rank(df_index, 'index_val', index_name=col, partitionby=['indu'])

                # return df_index,Load_date,pct_col,db_name,table_name
                df_index = df_index.select('uuid', F.col(pct_col).alias('index_val'))
                insert_into_hive(
                    df_index, db_name, table_name, spark=spark,
                    partition=['load_date', 'index_name'],
                    partition_val=[load_date, pct_col])
                df_index.unpersist()
                df_indu.unpersist()
            else:
                pass
        else:
            pass
