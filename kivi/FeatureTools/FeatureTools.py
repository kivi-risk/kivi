

import numpy as np
import pandas as pd


def ratio(df: pd.DataFrame, dividend: str, divisor: str, new_col: str):
    df[new_col] = df[dividend] / df[divisor]


def cross_nan(item):
    if np.isnan(item[cols[0]]) and np.isnan(item[cols[1]]):
        return "A"
    elif np.isnan(item[cols[0]]) and (not np.isnan(item[cols[1]])):
        return "B"
    elif (not np.isnan(item[cols[0]])) and np.isnan(item[cols[1]]):
        return "C"
    else:
        return "D"


def cross_median(item, ):
    """
    median_a 月份数
    median_b 融资次数
    :param item:
    :return:
    """
    if (item[cols[0]] <= median_a) and (item[cols[1]] <= median_b):
        return 2
    elif (item[cols[0]] <= median_a) and (item[cols[1]] > median_b):
        return 3
    elif (item[cols[0]] > median_a) and (item[cols[1]] <= median_b):
        return 5
    elif (item[cols[0]] > median_a) and (item[cols[1]] > median_b):
        return 4
    else:
        return 1


def joint_feature(df, corss_type, med_a=None, med_b=None, dropna=False):
    global cols, median_a, median_b

    if dropna == True:
        df.dropna(axis=0, inplace=True)

    cols = df.columns.tolist()
    target_name = cols.pop(-1)
    if med_a is not None:
        median_a = med_a
        median_b = med_b
    else:
        median_a = df[cols[0]].median()
        median_b = df[cols[1]].median()
    if corss_type == 'nan':
        df['corr'] = df.apply(cross_nan, axis=1)
    elif corss_type == 'median':
        df['corr'] = df.apply(cross_median, axis=1)
    return df


class FeatureTools:

    def __init__(self, df, conf: [dict, str], spark):

        if isinstance(conf, dict):
            self.conf = conf
        elif isinstance(conf, str):
            self.conf = self._load_config(conf)

        self.min_value = 1e-6
        self.spark = spark
        self.df = df.orderBy('uuid', 'month')
        self.df_res = self.df.select('uuid').dropDuplicates()
        self.datas = []
        self.datas_aggs = []
        self.__gen_months()
        self.__gen_datas()
        print('Pre Code Done!')

    def __gen_months(self, ):
        start_month = pd.to_datetime(self.conf.get('observe_time') + '01') - pd.DateOffset(
            months=int(self.conf.get('months_cnt')) - 1)
        end_month = pd.to_datetime(self.conf.get('observe_time') + '01') + pd.DateOffset(months=1)
        months = pd.date_range(start_month, end_month, freq='M', closed='left').astype(str).tolist()
        self.conf['months'] = [month.replace('-', '')[: 6] for month in months]

    def __gen_datas(self):

        def month_to_observe_time(months):
            def f(month):
                return 11 - months.index(month)

            return F.udf(f, returnType=IntegerType())

        for filter_rule in self.conf.get('filter_rules'):
            act_type, values = list(filter_rule.items())[0]

            df_agg_rule = self.df.where(self.df[act_type].isin(values))

            self.datas.append(df_agg_rule)

            self.datas_aggs.append(
                df_agg_rule.groupBy(self.conf.get('group_cols')).agg(
                    {}.fromkeys(self.conf.get('basic_vars'), self.conf.get('agg_type'))
                )
            )

        for i, data_agg in enumerate(self.datas_aggs):
            # 修正字段名称
            for col in data_agg.columns:
                if '(' in col:
                    data_agg = data_agg.withColumnRenamed(col, col.split('(')[1].split(')')[0])

            data_agg = data_agg.withColumn(
                'time_mean',
                F.abs(data_agg[self.conf.get('basic_vars')][0] / data_agg[self.conf.get('basic_vars')][1]))

            # 差分
            window = Window.orderBy('month').partitionBy('uuid', 'direction')
            data_agg = data_agg.withColumn('amt_lag_1', F.lag(data_agg.amt_raw).over(window))
            data_agg = data_agg.withColumn('cnt_lag_1', F.lag(data_agg.cnt_raw).over(window))
            data_agg = data_agg.withColumn('amt_lag', data_agg.amt_raw - data_agg.amt_lag_1)
            data_agg = data_agg.withColumn('cnt_lag', data_agg.cnt_raw - data_agg.cnt_lag_1)
            # 距今月数
            data_agg = data_agg.withColumn("month_to_observe",
                                           month_to_observe_time(self.conf['months'])(data_agg.month))
            self.datas_aggs[i] = data_agg

    def _get_month_filter(self, time_interval: int):
        return self.conf['months'][-time_interval:]

    def cal_index(self, data, rule_prefix='R1'):

        months = self.conf['months']

        def continuous_month(months_ls):
            if len(months_ls) == 0:
                return 0
            elif len(months_ls) < 2:
                return 1
            else:
                months_ls = [month[4:] for month in sorted(months_ls)]
                diff = []
                for index in range(len(months_ls) - 1):
                    diff.append(int(months_ls[index]) - int(months_ls[index + 1]))
                diff = [1 if diff_value == -1 or diff_value == 11 else 0 for diff_value in diff]
                diff = ''.join([str(diff_value) for diff_value in diff])
                counts = [item.count('1') for item in diff.split('0')]
                return max(counts) + 1

        @F.udf(returnType=IntegerType())
        def non_pay_month(month_ls):
            max_month = max(month_ls)
            return 11 - months.index(max_month)

        @F.udf(returnType=IntegerType())
        def continuous_pay_month(months_ls):
            return continuous_month(months_ls)

        def continuous_no_pay_month(month_filter):
            def fun(months_ls):
                month_ls = list(set(month_filter) - set(months_ls))
                return continuous_month(month_ls)

            return F.udf(fun, returnType=IntegerType())

        def value_compare(values):
            if len(values) == 0:
                return [0]
            else:
                values = [float(value) for value in values]
                mean = sum(values) / len(values)
                values = [0 if (value - mean) < 0 else 1 for value in values]
                return values

        @F.udf(returnType=IntegerType())
        def more_than_cnt(values):
            return value_compare(values).count(1)

        @F.udf(returnType=IntegerType())
        def less_than_cnt(values):
            return value_compare(values).count(0)

        def trend_analysis(values):
            values = [float(value) for value in values]
            pres = values[: -1]
            tails = values[1:]
            return [tail - pre for pre, tail in zip(pres, tails)]

        @F.udf(returnType=IntegerType())
        def increase(values):
            if len(values) <= 1:
                return -1
            else:
                masks = trend_analysis(values)
                masks = [mask > 0 for mask in masks]
                return 1 if all(masks) else 0

        @F.udf(returnType=IntegerType())
        def decrease(values):
            if len(values) <= 1:
                return -1
            else:
                masks = trend_analysis(values)
                masks = [mask < 0 for mask in masks]
                return 1 if all(masks) else 0

        df_res = data.select('uuid').dropDuplicates()
        for time_interval, direction in product(self.conf.get('time_range_list'), self.conf.get('direction_type')):
            month_filter = self._get_month_filter(time_interval)
            cond = data.month.isin(month_filter) & (data[self.conf.get('direction')] == direction)
            part_data = data.where(cond)

            # month_filter_spark = self.spark.sparkContext.broadcast(month_filter)
            part_res = part_data.groupBy('uuid').agg(
                # 金额
                F.sum(part_data.amt_raw).alias(f'{rule_prefix}_{time_interval}M_{direction}_amt_sum'),
                F.max(part_data.amt_raw).alias(f'{rule_prefix}_{time_interval}M_{direction}_amt_max'),
                F.min(part_data.amt_raw).alias(f'{rule_prefix}_{time_interval}M_{direction}_amt_min'),
                F.avg(part_data.amt_raw).alias(f'{rule_prefix}_{time_interval}M_{direction}_amt_avg'),
                F.stddev(part_data.amt_raw).alias(f'{rule_prefix}_{time_interval}M_{direction}_amt_std'),

                # 次数
                F.sum(part_data.cnt_raw).alias(f'{rule_prefix}_{time_interval}M_{direction}_cnt_sum'),
                F.max(part_data.cnt_raw).alias(f'{rule_prefix}_{time_interval}M_{direction}_cnt_max'),
                F.min(part_data.cnt_raw).alias(f'{rule_prefix}_{time_interval}M_{direction}_cnt_min'),
                F.avg(part_data.cnt_raw).alias(f'{rule_prefix}_{time_interval}M_{direction}_cnt_avg'),
                F.stddev(part_data.cnt_raw).alias(f'{rule_prefix}_{time_interval}M_{direction}_cnt_std'),

                # 月份类
                # 总交易月份数
                F.countDistinct(part_data.month).alias(f'{rule_prefix}_{time_interval}M_{direction}_months_pay_cnt'),
                # 距今交易最近月份
                F.max(part_data.month).alias(f'{rule_prefix}_{time_interval}M_{direction}_months_rct'),
                # 距今未交易日期数，距今无交易月份数
                F.min(part_data.month_to_observe).alias(
                    f'{rule_prefix}_{time_interval}M_{direction}_months_rct_no_pay'),
                # 交易日期比例
                (F.countDistinct(part_data.month) / len(month_filter)).alias(
                    f'{rule_prefix}_{time_interval}M_{direction}_months_pay_rate'),
                # 未交易日期数
                (len(month_filter) - F.countDistinct(part_data.month)).alias(
                    f'{rule_prefix}_{time_interval}M_{direction}_months_nopay_cnt'),
                # 最大连续交易月数
                continuous_pay_month(F.collect_list(part_data.month)).alias(
                    f'{rule_prefix}_{time_interval}M_{direction}_months_max_ctn_cnt'),
                # 最大连续不交易数
                continuous_no_pay_month(month_filter)(F.collect_list(part_data.month)).alias(
                    f'{rule_prefix}_{time_interval}M_{direction}_months_max_nopay_ctn_cnt'),

                # 笔均金额
                (F.sum(part_data.amt_raw) / F.sum(part_data.cnt_raw)).alias(
                    f'{rule_prefix}_{time_interval}M_{direction}_amt_atm_avg'),
                F.max(part_data.time_mean).alias(f'{rule_prefix}_{time_interval}M_{direction}_amt_atm_avg_max'),
                F.min(part_data.time_mean).alias(f'{rule_prefix}_{time_interval}M_{direction}_amt_atm_avg_min'),
                F.avg(part_data.time_mean).alias(f'{rule_prefix}_{time_interval}M_{direction}_amt_atm_avg_avg'),
                F.stddev(part_data.time_mean).alias(f'{rule_prefix}_{time_interval}M_{direction}_amt_atm_avg_std'),

                # 月交易金额小于月均金额月数
                less_than_cnt(F.collect_list(part_data.amt_raw)).alias(
                    f'{rule_prefix}_{time_interval}M_{direction}_amt_less_than_avg'),
                # 月交易金额大于等于月均金额月数
                more_than_cnt(F.collect_list(part_data.amt_raw)).alias(
                    f'{rule_prefix}_{time_interval}M_{direction}_amt_more_than_avg'),
                # 月交易次数小于月均次数
                less_than_cnt(F.collect_list(part_data.cnt_raw)).alias(
                    f'{rule_prefix}_{time_interval}M_{direction}_cnt_less_than_avg'),
                # 月交易次数大于等于月均次数
                more_than_cnt(F.collect_list(part_data.cnt_raw)).alias(
                    f'{rule_prefix}_{time_interval}M_{direction}_cnt_more_than_avg'),

                # 交易金额严格递增
                increase(F.collect_list(part_data.amt_raw)).alias(
                    f'{rule_prefix}_{time_interval}M_{direction}_amt_abs_increase'),
                # 交易金额严格递减
                decrease(F.collect_list(part_data.amt_raw)).alias(
                    f'{rule_prefix}_{time_interval}M_{direction}_amt_abs_decrease'),
                # 交易次数严格递增
                increase(F.collect_list(part_data.cnt_raw)).alias(
                    f'{rule_prefix}_{time_interval}M_{direction}_cnt_abs_increase'),
                # 交易次数严格递减
                decrease(F.collect_list(part_data.cnt_raw)).alias(
                    f'{rule_prefix}_{time_interval}M_{direction}_cnt_abs_decrease'),

                # 一阶差分，交易金额严格递增
                increase(F.collect_list(part_data.amt_lag)).alias(
                    f'{rule_prefix}_{time_interval}M_{direction}_amt_lag_increase'),
                # 一阶差分，交易金额严格递减
                decrease(F.collect_list(part_data.amt_lag)).alias(
                    f'{rule_prefix}_{time_interval}M_{direction}_amt_lag_decrease'),
                # 一阶差分，交易次数严格递增
                increase(F.collect_list(part_data.cnt_lag)).alias(
                    f'{rule_prefix}_{time_interval}M_{direction}_cnt_lag_increase'),
                # 一阶差分，交易次数严格递减
                decrease(F.collect_list(part_data.cnt_lag)).alias(
                    f'{rule_prefix}_{time_interval}M_{direction}_cnt_lag_decrease'),
            )

            df_res = df_res.join(part_res, how='left', on='uuid')

        # 近X月次数或金额比近12月次数或金额
        for time_interval, direction in product(self.conf.get('time_range_list')[:-1], self.conf.get('direction_type')):
            if time_interval * 2 <= self.conf.get('time_range_list')[-1]:
                # 2TR
                df_res = df_res.withColumn(f'{rule_prefix}_{time_interval}M_{direction}_amt_sum_div2tr',
                                           df_res[f'{rule_prefix}_{time_interval}M_{direction}_amt_sum'] / (df_res[
                                                                                                                f'{rule_prefix}_{time_interval * 2}M_{direction}_amt_sum'] - self.min_value))
                df_res = df_res.withColumn(f'{rule_prefix}_{time_interval}M_{direction}_cnt_sum_div2tr',
                                           df_res[f'{rule_prefix}_{time_interval}M_{direction}_cnt_sum'] / (df_res[
                                                                                                                f'{rule_prefix}_{time_interval * 2}M_{direction}_cnt_sum'] - self.min_value))
                # 环比
                df_res = df_res.withColumn(f'{rule_prefix}_{time_interval}M_{direction}_amt_sum_chain_rate',
                                           df_res[f'{rule_prefix}_{time_interval}M_{direction}_amt_sum'] / (df_res[
                                                                                                                f'{rule_prefix}_{time_interval * 2}M_{direction}_amt_sum'] -
                                                                                                            df_res[
                                                                                                                f'{rule_prefix}_{time_interval}M_{direction}_amt_sum'] - self.min_value))
                df_res = df_res.withColumn(f'{rule_prefix}_{time_interval}M_{direction}_cnt_sum_chain_rate',
                                           df_res[f'{rule_prefix}_{time_interval}M_{direction}_cnt_sum'] / (df_res[
                                                                                                                f'{rule_prefix}_{time_interval * 2}M_{direction}_cnt_sum'] -
                                                                                                            df_res[
                                                                                                                f'{rule_prefix}_{time_interval}M_{direction}_cnt_sum'] - self.min_value))

            df_res = df_res.withColumn(f'{rule_prefix}_{time_interval}M_{direction}_amt_sum_div1y',
                                       df_res[f'{rule_prefix}_{time_interval}M_{direction}_amt_sum'] / (
                                                   df_res[f'{rule_prefix}_12M_{direction}_amt_sum'] - self.min_value))
            df_res = df_res.withColumn(f'{rule_prefix}_{time_interval}M_{direction}_cnt_sum_div1y',
                                       df_res[f'{rule_prefix}_{time_interval}M_{direction}_cnt_sum'] / (
                                                   df_res[f'{rule_prefix}_12M_{direction}_cnt_sum'] - self.min_value))

        return df_res

    def cal_indexs(self):
        for filter_rule in range(len(self.conf.get('filter_rules'))):
            df = self.datas_aggs[filter_rule]
            res = self.cal_index(data=df, rule_prefix=f'R{filter_rule}')
            self.df_res = self.df_res.join(res, how='left', on='uuid')
            print(f'Rule {filter_rule + 1} Done! With {len(res.columns)} Columns!')
        print(f'ALL {len(self.df_res.columns)} Columns!')

    def _save_config(self):
        Pk.save(self.conf.get('config_file_name.pk'))

    def _load_config(self, conf):
        return Pk.load(conf)

    def _set_filter_rules(self, filter_rules):
        self.conf['filter_rules'] = filter_rules

    def _set_agg_type(self, agg_type):
        self.conf['agg_type'] = agg_type

