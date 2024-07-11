import logging
import numpy as np
import pandas as pd


logging.basicConfig(level=logging.INFO,
                    format='%(levelname)s: %(message)s')

from ..utils.utils import sameLength

def IntScore(score):
    """
    将数值分数按 5 取整
    :param score: 浮点型分数
    :return: 按 5 取整分数
    """
    basic_score = np.arange(0, 101, 5)
    return basic_score[np.argmin(np.abs(score - basic_score))]

def DetecMonotony(trend_mask):
    """"""
    if all(trend_mask):
        return '单调上升'
    elif not any(trend_mask):
        return '单调下降'
    else:
        return None

def Montony(values: pd.Series):
    """"""
    diff = values.diff().dropna()
    if len(diff) > 0:
        trend_mask = (diff >= 0).tolist()
        trend = DetecMonotony(trend_mask)
        if trend:
            return trend
        else:
            for mask_id in range(len(trend_mask)):
                top_trend = DetecMonotony(trend_mask[: mask_id])
                end_trend = DetecMonotony(trend_mask[mask_id: ])
                if all([top_trend, end_trend]):
                    trend = f'{top_trend[2:]}{end_trend[2:]}'
                    return trend
            return '未知'
    else:
        return '数据不足'

class WOE:
    """
    WOE Object 为全部 WOE 的基础类函数，其方法被全部其他分箱方式调用
    """
    def data_init(self, variables, target, var_name=None, fill_bin=True, abnormal_vals=[], all_feature=False, weight=None):
        """
        初始化
        :param variables: 待分箱变量
        :param target: 标签
        :param bins: 分箱数量
        :param var_name: 变量名称
        :param fill_bin: 是否在分箱中未包含 1 标签的情况下，全部 1 标签数量自增 1 默认为 False
        :param abnormal_vals: 特殊值分箱，在变量存在特殊值时单独分一箱，如 -1111, -9999。
        :param all_feature: 是否为全变量模式进行分箱，为 Pearson 分箱设计，默认为 False。
        :param weight: 样本权重。
        """
        self.fill_bin = fill_bin
        self.abnormal_vals=abnormal_vals

        # 是否存在变量的名称，存在使用原名，不存在使用变量 var_name
        if hasattr(variables, 'name'):
            self.var_name = variables.name
        else:
            self.var_name = var_name
        # 非全变量模式
        if not all_feature:
            # 检查变量与标签是否为同一长度
            if sameLength(variables, target):
                Exception(ValueError, 'variable and target must be the same length!')
            # 变量名称、分箱数、基础计数
            self.name = variables.name

            self._basic_count(target, weight)
            self.justMiss, notMiss, self.abnormal = self.findMissData(variables, target, weight)

            # 拆分字段中的空箱与数值
            self.variables = notMiss.variables
            self.target = notMiss.target

            if weight is None:
                self.weight = None
            else:
                self.weight = notMiss.weight

    def findMissData(self, variables, target, weight=None):
        """
        拆分空值数据与非空值数据
        :param variables: 分箱变量
        :param taget: 标签
        """
        if weight is None:
            df = pd.DataFrame({"variables": variables, "target": target})
        else:
            df = pd.DataFrame({"variables": variables, "target": target, 'weight': weight})

        # 如果变量为数值型变量，则检查是否存在正负无穷的数值，即是否存在 infinite，
        # 一般在此处去除 infinite 的数据
        if pd.api.types.is_number(df.variables):
            df = df[-np.isinf(df.variables)]

        # 异常值、空值、正常值分离
        if len(self.abnormal_vals) > 0:
            cond_abnormal = df.variables.isin(self.abnormal_vals)
            abnormal = df[cond_abnormal]
            justMiss = df[df.variables.isna() & ~cond_abnormal]
            notMiss = df[df.variables.notna() & ~cond_abnormal]
        else:
            abnormal = pd.DataFrame()
            justMiss = df[df.variables.isna()]
            notMiss = df[df.variables.notna()]
        # 返回纯空值数据，非空值数据
        return justMiss, notMiss, abnormal

    def _basic_count(self, target, weight=None):
        """
        基础统计方法
        :param target: 标签列
        :return: None
        """
        # 样本长度
        self.sampleLength = len(target)

        if weight is None:
            # 样本量、bad 样本量
            self.total, self.bad = target.count(), target.sum()
            # good 样本量
            self.good = self.total - self.bad
        else:
            self.total = weight.sum()
            self.bad = weight[target == 1].sum()
            self.good = weight[target == 0].sum()

    def __res(self, Bucket, ):
        """
        基本结果表
        :param Bucket: class groupby
        :return: None
        """
        # 非空分箱的结果表
        self.res = pd.DataFrame({
            # min_bin, max_bin 调整为分箱的临界值，而非子分箱的最大最小值
            'min_bin': Bucket.variables.min(),
            'max_bin': Bucket.variables.max(),
            'bad': Bucket.target.sum(),
            'good': Bucket.target.count() - Bucket.target.sum(),
            'total': Bucket.target.count(),
        })
        # 空箱
        self.nan_res = pd.DataFrame()
        if len(self.justMiss) != 0:
            self.nan_res = pd.DataFrame({
                'min_bin': [np.nan],
                'max_bin': [np.nan],
                "bad": self.justMiss.sum().target,
                'good': self.justMiss.count().target - self.justMiss.sum().target,
                'total': self.justMiss.count().target,
            })
        # 异常值
        self.abnormal_res = pd.DataFrame()
        if len(self.abnormal) != 0:
            self.abnormal_res = self.abnormal.groupby('variables').agg({'target': ['sum', 'count']})
            self.abnormal_res.columns = ['bad', 'total']

            self.abnormal_res['min_bin'] = self.abnormal_res.index
            self.abnormal_res['max_bin'] = self.abnormal_res.index
            self.abnormal_res['good'] = self.abnormal_res.total - self.abnormal_res.bad

            self.abnormal_res = self.abnormal_res[[
                'min_bin', 'max_bin', "bad", 'good', 'total',
            ]]
            self.abnormal_res.reset_index(inplace=True, drop=True)

    def get_weighted_buckets(self, value_cut=None, df=None, variables=None, target=None, weight=None):
        """获取加权分组"""

        if df is not None:
            variables = df.variables
            target = df.target
            weight = df.weight
        else:
            pass

        weight_good = weight.copy()
        weight_bad = weight.copy()

        weight_good[target == 1] = 0
        weight_bad[target == 0] = 0

        if value_cut is not None:
            Bucket = pd.DataFrame({
                'variables': variables,
                'target': target,
                'weight': weight,
                'weight_good': weight_good,
                'weight_bad': weight_bad,
                'Bucket': value_cut,
            }).groupby('Bucket', as_index=True)
        else:
            Bucket = pd.DataFrame({
                'variables': variables,
                'target': target,
                'weight': weight,
                'weight_good': weight_good,
                'weight_bad': weight_bad,
            }).groupby('variables', as_index=True)
        return Bucket

    def weighted_buckets_stats(self, Bucket):
        """weighted good or bad"""
        # 非空分箱的结果表
        self.res = pd.DataFrame({
            # min_bin, max_bin 调整为分箱的临界值，而非子分箱的最大最小值
            'min_bin': Bucket.variables.min(),
            'max_bin': Bucket.variables.max(),
            'bad': Bucket.weight_bad.sum(),
            'good': Bucket.weight_good.sum(),
            'total': Bucket.weight.sum(),
        })
        # 空箱
        self.nan_res = pd.DataFrame()
        if len(self.justMiss) != 0:
            self.nan_res = pd.DataFrame({
                'min_bin': [np.nan],
                'max_bin': [np.nan],
                "bad": self.justMiss.weight[self.justMiss.target == 1].sum(),
                'good': self.justMiss.weight[self.justMiss.target == 0].sum(),
                'total': self.justMiss.weight.sum(),
            })
        # 异常值
        self.abnormal_res = pd.DataFrame()
        if len(self.abnormal) != 0:
            abnormal_bucket = self.get_weighted_buckets(df=self.abnormal)

            self.abnormal_res = pd.DataFrame({
                'min_bin': abnormal_bucket.target.min().index,
                'max_bin': abnormal_bucket.target.max().index,
                'bad': abnormal_bucket.weight_bad.sum(),
                'good': abnormal_bucket.weight_good.sum(),
                'total': abnormal_bucket.weight.sum(),
            })

    def calculate_woe(self, res):
        """
        依据结果表，计算woe
        :param res: res 结果表
        :return: res 结果表
        """
        # 如果存在 fill_bin==True, 则需要对分箱中未包含 1 标签的情况下，全部 1 标签数量自增 0.5
        if self.fill_bin and (0 in res.bad.tolist()):
            res.bad = res.bad + 0.5
        elif  self.fill_bin and (0 in res.good.tolist()):
            res.good = res.good + 0.5
        # 每个箱中坏样本所占总样本数的比例
        res['bad_rate'] = res['bad'] / res['total']
        # 每个箱中坏样本所占坏样本总数的比例
        res['badattr'] = res['bad'] / self.bad
        # 每个箱中好样本所占好样本总数的比例
        res['goodattr'] = res['good'] / self.good
        # 计算每个箱体的woe值
        res['woe'] = np.log(res['badattr'] / res['goodattr'])
        res['iv'] = (res['badattr'] - res['goodattr']) * res['woe']
        # 对箱体从大到小进行排序
        res = (res.sort_values(by='min_bin')).reset_index(drop=True)
        return res

    def woe_iv_res(self, Bucket, score=True, origin_border=False, order=True):
        """
        描述：计算 woe 结果。

        :param Bucket:
        :param score: 是否增加 WOE score。
        :param origin_border: 是否增加 分箱中的最大值与最小值。
        :return: DataFrame
        """
        # 初始化 res 表
        if not hasattr(self, 'weight') or self.weight is None:
            self.__res(Bucket=Bucket)
        else:
            self.weighted_buckets_stats(Bucket=Bucket)

        # 计算 woe 值
        self.res = self.calculate_woe(self.res)
        # 计算字段的缺失率
        missing_rate = 1 - (self.res.total.sum() / self.sampleLength)
        self.res['bin_type'] = 0

        # 如果变量存在空值
        if len(self.justMiss) != 0:
            # 计算空值结果表
            self.nan_res = self.calculate_woe(self.nan_res)
            self.nan_res['bin_type'] = 1
            # 汇总空值与非空的值的计算结果表
            self.res = self.res.append(self.nan_res)

        # 如果变量存在异常值
        if len(self.abnormal) != 0:
            # 计算空值结果表
            self.abnormal_res = self.calculate_woe(self.abnormal_res)
            self.abnormal_res['bin_type'] = 2
            # 汇总空值与非空的值的计算结果表
            self.res = pd.concat([self.res, self.abnormal_res], axis=0)

        # 计算分箱的 iv 值
        self.res['iv_value'] = self.res.iv[-np.isinf(self.res.iv)].sum()
        self.res['missing_rate'] = missing_rate

        # 给定变量名称
        self.res['var_name'] = self.var_name

        # 重置结果表 index
        self.res.reset_index(drop=True, inplace=True)

        columns = [
            'var_name', 'missing_rate', 'min_bin', 'max_bin', 'total',
            'bad', 'bad_rate', 'woe', 'iv', 'iv_value', ]

        if order:
            columns.append('order')
            woe_notna = self.res.loc[~self.res.min_bin.isna(), 'woe']
            order = Montony(woe_notna)
            self.res['order'] = order

        if score:
            columns.append('score')
            neg_woe = - self.res.woe
            woe_score = (neg_woe - neg_woe.min()) * 100 / (neg_woe.max() - neg_woe.min())
            self.res['score'] = list(map(IntScore, woe_score))

        try:

            try:
                self.res['min_bin'] = self.res['min_bin'].astype(float)
                self.res['max_bin'] = self.res['max_bin'].astype(float)
                var_type = 'float'
            except:
                var_type = 'object'

            if var_type == 'float':
                self.res['min_bin_val'] = self.res['min_bin']
                self.res['max_bin_val'] = self.res['max_bin']

                self.res.loc[self.res.max_bin[self.res.bin_type == 0].idxmax(), 'max_bin'] = np.inf
                self.res.loc[(self.res.bin_type == 0), 'min_bin'] = [-np.inf] + self.res[self.res.bin_type == 0].max_bin[: -1].tolist()

            if len(self.justMiss) > 0:
                self.res.loc[(self.res.bin_type == 1), 'min_bin'] = np.nan
                self.res.loc[(self.res.bin_type == 1), 'max_bin'] = np.nan

            if origin_border:
                columns += ['min_bin_val', 'max_bin_val']
        except Exception as e:
            print('kivi tips:', self.variables.name, e)

        self.res = self.res[columns]

        