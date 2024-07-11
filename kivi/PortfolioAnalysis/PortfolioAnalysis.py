import numpy as np
import pandas as pd
from pyspark.sql import functions as F
from pyspark.sql import Window
from pyspark.sql.types import *


class Vintage():
    """
    计算 Vintage
    """
    def __init__(
            self, df, loan_id='id', loan_period_name='period',
            observe_date='20150228', observe_period=24, spark=None):
        """

        """
        self.df = df
        self.spark = spark
        self.loan_id = loan_id
        self.loan_period_name = loan_period_name
        self.observe_date = observe_date
        self.observe_period = observe_period
        self.df = self.df.withColumn(
            'loan_month',
            F.substring(F.col('loan_date'), 1, 6))
        self.df_month_total_loan = self.df.groupBy('loan_month').agg(
            F.sum(F.col('should_capital')).alias('should_capital'))

    def getObserveMonth(self, ):
        return pd.date_range(
            self.observe_date, periods=self.observe_period, freq='M'
        ).astype(str).str.replace('-', '').tolist()

    def calCapitalInterest(self, df_obs, obs_date):
        """
        1. 将还款时间大于记录时间的记为未还款
            a. 具体将已归零的剩余本息更换为应还本息
        2. 修改还款时间为记录时间
        3. 再将未完全还清本息的还款时间改为记录时间
        """
        df_obs = df_obs.withColumn(
            'surplus_capital',
            F.when(F.col('pay_date') > obs_date, F.col('should_capital')).otherwise(F.col('surplus_capital')))
        df_obs = df_obs.withColumn(
            'surplus_interest',
            F.when(F.col('pay_date') > obs_date, F.col('should_interest')).otherwise(F.col('surplus_interest')))
        return df_obs

    def calOverDue(self, df_obs, obs_date):
        """
        """
        # 计算逾期
        df_obs = df_obs.withColumn(
            'pay_date',
            F.when((F.col('pay_date') > obs_date) | (F.col('surplus_interest') > 0), obs_date).otherwise(
                F.col('pay_date')))
        df_obs = df_obs.withColumn(
            'due_days',
            F.datediff(F.to_timestamp(F.col('pay_date'), 'yyyyMMdd'), F.to_timestamp(F.col('due_date'), 'yyyyMMdd')))
        df_obs = df_obs.withColumn('due_days', F.when(F.col('due_days') < 0, 0).otherwise(F.col('due_days')))

        # 计算剩余本金
        window = Window.partitionBy(self.loan_id).orderBy(F.monotonically_increasing_id())
        df_obs = df_obs.withColumn(
            'paid_capital',
            F.sum(F.col('should_capital') - F.col('surplus_capital')).over(window))
        df_obs = df_obs.withColumn(
            'total_surplus_capital',
            F.col('total_loan') - F.col('paid_capital'))
        return df_obs

    def MOB(self, df_obs):
        @F.udf(returnType=StringType())
        def mob(x):
            if x == 0:
                return 'M0'
            elif x <= 30:
                return 'M1'
            elif x <= 60:
                return 'M2'
            elif x <= 90:
                return 'M3'
            else:
                return 'M4+'

        df_obs = df_obs.withColumn('mob', mob(F.col('due_days')))
        return df_obs

    def oneObserveDate(self, obs_date):
        """
        """
        df_obs = self.df.where(F.col('due_date') <= obs_date)
        df_obs = df_obs.fillna(str(obs_date), subset='pay_date')
        df_obs = self.calCapitalInterest(df_obs, obs_date)
        df_obs = self.calOverDue(df_obs, obs_date)
        df_obs = self.MOB(df_obs)
        # 剩余利息计算至 ID 级
        df_obs = df_obs.withColumn(
            'pay_int',
            F.sum(F.col('surplus_interest')).over(Window.partitionBy(self.loan_id)))
        df_not_pay_int = df_obs.where((F.col('pay_int') > 0) & (F.col('surplus_interest') > 0))
        df_paid_int = df_obs.where(F.col('pay_int') == 0)

        # 1. 有未结清利息，取最早一条
        # 2. 无未结清利息，取最新一条
        df_not_pay_int = df_not_pay_int.withColumn(
            'period_rank',
            F.row_number().over(Window.partitionBy(self.loan_id).orderBy(F.col(self.loan_period_name))))
        df_paid_int = df_paid_int.withColumn(
            'period_rank',
            F.row_number().over(Window.partitionBy(self.loan_id).orderBy(F.col(self.loan_period_name).desc())))

        df_obs = df_not_pay_int.where(F.col('period_rank') == 1).unionAll(
            df_paid_int.where(F.col('period_rank') == 1))

        # 计算坏账
        df_obs = df_obs.withColumn(
            'bad_amt',
            F.when(F.col('mob') == 'M4+', F.col('total_surplus_capital')).otherwise(0))
        df_obs_bad_amt_by_month = df_obs.groupBy('loan_month').agg(
            F.sum('bad_amt').alias('bad_amt'))

        # 账期
        df_obs_bad_amt_by_month = df_obs_bad_amt_by_month.withColumn(
            'book_month',
            F.months_between(
                F.to_date(F.lit(obs_date), 'yyyyMMdd'),
                F.to_date(F.col('loan_month'), 'yyyyMM')).cast(IntegerType()))
        df_obs_bad_amt_by_month = df_obs_bad_amt_by_month.withColumn(
            'observe_date', F.lit(obs_date))
        return df_obs_bad_amt_by_month

    def vintage(self, ):
        """
        """
        df_all_obs = list(map(self.oneObserveDate, self.getObserveMonth()))
        M4Plus = None
        for df_one_obs in df_all_obs:
            if M4Plus is None:
                M4Plus = df_one_obs
            else:
                M4Plus = M4Plus.unionAll(df_one_obs)
        return M4Plus

class VintagePd():
    """
    计算 Vintage
    """
    def __init__(
            self, df, loan_id='id', loan_period_name='period', observe_date='20150228',
            observe_period=24, loan_date_name='loan_date', mob='M4+',
            should_capital_name='should_capital'):
        '''
        描述：计算 Vintage 初始化

        参数：
        :param df: 借据表
        :param loan_id: 借据唯一标识
        :param loan_period_name: 期数字段名称
        :param observe_date: 初始观察日期
        :param observe_period: 观察周期

        示例：

        '''
        self.df = df
        self.loan_id = loan_id
        self.loan_period_name = loan_period_name
        self.observe_date = observe_date
        self.observe_period = observe_period
        self.should_capital_name = should_capital_name
        self.mob = mob
        self.df['loan_month'] = self.df[loan_date_name].dt.strftime('%Y%m')
        self.df_month_total_loan = self.df[['loan_month', should_capital_name]].groupby(
            'loan_month').sum()
        self.df_month_total_loan.reset_index(inplace=True)

    def getObserveMonth(self, ):
        return pd.date_range(
            self.observe_date, periods=self.observe_period, freq='M'
        )

    def convert(self, df, obs_date):
        """

        """
        df.fillna({'pay_date': obs_date}, inplace=True)
        df.loc[df['pay_date'] > obs_date, 'surplus_capital'] = df.loc[df['pay_date'] > obs_date, 'should_capital']
        df.loc[df['pay_date'] > obs_date, 'surplus_interest'] = df.loc[df['pay_date'] > obs_date, 'should_interest']
        df['pay_date'] = df['pay_date'].apply(lambda x: obs_date if x > obs_date else x)
        df.loc[df['surplus_interest'] > 0, 'pay_date'] = obs_date

        # 计算逾期天数，并将提前还款的逾期天数修改为0。
        df['due_days'] = (df['pay_date'] - df['due_date']) / np.timedelta64(1, 'D')
        df.loc[df['due_days'] < 0, 'due_days'] = 0

        df['paid_capital'] = df['should_capital'] - df['surplus_capital']
        df['paid_capital'] = df.groupby(self.loan_id)['paid_capital'].transform('cumsum')
        df['total_surplus_capital'] = df['total_loan'] - df['paid_capital']
        return df

    def MOB(self, due_days):
        """

        """
        if due_days == 0:
            return 'M0'
        elif due_days <= 30:
            return 'M1'
        elif due_days <= 60:
            return 'M2'
        elif due_days <= 90:
            return 'M3'
        else:
            return 'M4+'

    def oneObserveDate(self, obs_date):
        """

        """
        df_obs = self.df[self.df['due_date'] <= obs_date].copy()
        df_obs = self.convert(df_obs, obs_date)
        df_obs['mob'] = df_obs['due_days'].apply(self.MOB)

        df_obs['not_pay_int'] = df_obs.groupby(self.loan_id)['surplus_interest'].transform('sum')
        df_obs['period_min'] = df_obs.groupby(self.loan_id)['period'].transform('min')
        df_obs['period_max'] = df_obs.groupby(self.loan_id)['period'].transform('max')

        condition_paid_int = (df_obs.not_pay_int == 0) & (df_obs.period_max == df_obs.period)
        condition_not_pay_int = (df_obs.not_pay_int > 0) & (df_obs.period_min == df_obs.period) & (df_obs.surplus_interest > 0)
        df_obs = df_obs[condition_paid_int | condition_not_pay_int]

        df_obs['bad_amt'] = (df_obs['mob'] == self.mob) * df_obs['total_surplus_capital']

        df_obs_mob = df_obs.groupby('loan_month')[['bad_amt']].sum()
        df_obs_mob.reset_index(inplace=True)

        loan_date = pd.to_datetime(df_obs_mob.loan_month.astype(str) + pd.Series(['01'] * len(df_obs_mob)))
        df_obs_mob['book_month'] = ((obs_date - loan_date) / np.timedelta64(1, 'M')).round().astype(int)
        df_obs_mob['observe_date'] = obs_date
        return df_obs_mob

    def vintage(self, ):
        """
        """
        df_all_obs = list(map(self.oneObserveDate, self.getObserveMonth()))
        self.M4Plus = pd.DataFrame(columns=df_all_obs[0].columns)
        for df_one_obs in df_all_obs:
            self.M4Plus = self.M4Plus.append(df_one_obs)
        self.M4Plus = self.M4Plus.merge(self.df_month_total_loan, on='loan_month')
        self.M4Plus['bad_rate'] = self.M4Plus.bad_amt / self.M4Plus[self.should_capital_name]
        return self.M4Plus

    def vintagePivotTable(self, value):
        """
        :param value: `rate`、`amt`
        """
        if not hasattr(self, 'M4Plus'):
            self.vintage()
        return pd.pivot_table(
            self.M4Plus,
            values=f'bad_{value}',
            index='loan_month',
            columns='book_month',
            aggfunc='sum')
    #
    # def plot(self, ):
    #
    #     for col in LP_12_M4s.columns:
    #         LP_12_M4s[col] = (LP_12_M4s[col] / loan_LP.groupby('loan_month')['应还本金'].sum()).replace(0, np.nan)
    #     LP_12_M4s.iloc[: 12, :].transpose().plot(figsize=(12, 8), title='M4+ vintage')
