import inspect
import numpy as np
import pandas as pd
from scipy.stats import chi2
from pandas import DataFrame, Series
from typing import Any, List, Union, Optional
from kivi.woe.base import WOEMixin


__all__ = [
    "Chi2Bins"
]


def chi2_square(freq):
    """计算卡方值以检测目标类的频率在给定区间内是否存在显着差异。
    参考: "ChiMerge: DIscretization of Numerical Attributes"

    参数:
    :param freq: 分组与分箱的列联表（频数）。
    :returns: chi2 卡方统计量

    示例：
    >>> freq = np.array([[100, 9], [101, 8]])
    >>> # 计算卡方统计量
    >>> chi2_square(freq)
    """
    R = freq.sum(axis=1).reshape(1, -1)  # 每一个分组的样本数
    C = freq.sum(axis=0).reshape(1, -1).T  # 每一个类别的样本数
    # 期望频率 (加 0.5 避免小数)
    E = np.dot(C, R) / C.sum() + 0.5
    chi2_value = (np.square(freq.T - E) / E).sum()  # 卡方值
    return chi2_value


def BinsChiTest(m, pt_value, pt_column, pt_index):
    """
    对每对 m 个相邻区间执行卡方检验，使用第 i 个区间的索引作为区间对的索引
    """

    adjacent_list = (pt_value[i:i + m, :] for i in range(len(pt_value) - m + 1))
    adjacent_index = np.array([pt_index[i:i + m] for i in range(len(pt_value) - m + 1)])
    chi2_array = np.array([chi2_square(adj) for adj in adjacent_list])
    return adjacent_index, chi2_array


def pivot_table(index, column):
    """ """
    df_pivot = pd.DataFrame(np.vstack([index, column]).T, columns=['index', 'column'])
    df_pivot['cnt'] = 1

    if 'sort' in inspect.getfullargspec(pd.DataFrame.pivot_table).args:
        df_pivot = df_pivot.pivot_table(columns='column', index='index', aggfunc='count', sort=True)
    else:
        df_pivot = df_pivot.pivot_table(columns='column', index='index', aggfunc='count')

    df_pivot.fillna(0, inplace=True)

    pivot_table = df_pivot.values
    column_unique = df_pivot.columns.to_numpy()
    index_unique = df_pivot.index.to_numpy()
    return pivot_table, column_unique, index_unique


def assign_interval_unique(x, boundaries):
    """为 x 中的每个值分配一个距边界的间隔

    Parameters
    ----------
    x: 需要离散化的数据列。

    boundaries: 离散化目标 x 的区间边界值。

    Returns
    -------
    intervals: numpy.ndarray, shape (number of examples,2)
        向右闭合的区间数组。数组的左列和右列分别是左右边界。

    unique_intervals: numpy.ndarray, shape (number of unique intervals,2)
        向右闭合的唯一区间。数组的左列和右列分别是左右边界。
    """
    # Add -inf and inf to the start and end of boundaries
    max_value = max(x)
    boundaries = np.unique(np.concatenate((np.array([-float('inf')]), boundaries, np.array([float('inf')])), axis=0))

    # The max boundary that is smaller than x_i is its lower boundary.
    # The min boundary that is >= than x_i is its upper boundary.
    # Adding equal is because all intervals here are closed to the right.
    boundaries_diff_boolean = x.reshape(1, -1).T > boundaries.reshape(1, -1)
    lowers = np.array([boundaries[b].max() for b in boundaries_diff_boolean])
    uppers = np.array([boundaries[b].min() for b in ~boundaries_diff_boolean])

    # Replace the upper value with inf if it is not smaller then the maximum feature value
    n = x.shape[0]
    uppers = np.where(uppers >= max_value, [float('inf')] * n, uppers)
    # Array of intervals that are closed to the right
    intervals = np.stack((lowers, uppers), axis=1)

    unique_intervals = np.unique(intervals, axis=0)
    return intervals, unique_intervals


def chi_merge_vector(x, y, m=2, confidence_level=0.9, max_intervals=None,
                     min_intervals=2, initial_intervals=100) -> List[Union[int, float]]:
    """合并相似的相邻 m 个区间，直到所有相邻区间彼此显着不同。

    Parameters
    ----------

    x: numpy.array, shape (number of examples,)
        The array of data that need to be discretized.

    y: numpy.array, shape (number of examples,)
        The target array (or dependent variable).

    m: integer, optional(default=2)
        The number of adjacent intervals to compare during chi-squared test.

    confidence_level: float, optional(default=0.9)
        The confidence level to determine the threshold for intervals to
        be considered as different during the chi-square test.

    max_intervals: int, optional(default=None)
        Specify the maximum number of intervals the discretized array will have.
        Sometimes (like when training a scorecard model) fewer intervals are
        prefered. If do not need this option just set it to None.

    min_intervals: int, optional(default=2)
        Specify the mininum number of intervals the discretized array will have.
        If do not need this option just set it to 2.

    initial_intervals: int, optional(default=100)
        The original Chimerge algorithm starts by putting each unique value
        in an interval and merging through a loop. This can be time-consumming
        when sample size is large.
        Set the initial_intervals option to values other than None (like 10 or 100)
        will make the algorithm start at the number of intervals specified (the
        initial intervals are generated using quantiles). This can greatly shorten
        the run time. If do not need this option just set it to None.

    Return
    ------
    """
    # --------------------
    # 初始化阶段
    # --------------------
    n_j = np.unique(y).shape[0]  # 分类类别的数量
    n_i = np.unique(x).shape[0]  # 变量 x 的不同的值
    if (initial_intervals is not None and initial_intervals < n_i and min_intervals < n_i):
        # 离散分段数量小于 n_i 的值，最小分段数量应小于 n_i
        boundaries = np.unique(np.quantile(x, np.arange(0, 1, 1 / initial_intervals)[1:]))
    else:
        boundaries = np.unique(x)

    intervals, unique_intervals = assign_interval_unique(x, boundaries)

    # 当 unique x <= min_intervals 时，返回 X unique 值作为结果
    if n_i <= min_intervals:
        if n_i == 1:
            boundaries = np.array([float('inf')])
        return boundaries  # output the unique upper boundaries of discretized array

    # --------------------
    # 迭代步骤
    # --------------------
    if max_intervals is None:
        max_intervals = n_i

    threshold = chi2.ppf(confidence_level, n_j - 1)  # chi2 阈值
    # 各个分组的样本计数
    pt_value, pt_column, pt_index = pivot_table(intervals[:, 1], y)

    # 对每对 m 个相邻区间执行卡方检验，使用第 i 个区间的索引作为区间对的索引
    adjacent_index, chi2_array = BinsChiTest(m, pt_value, pt_column, pt_index)

    #### 合并最相近的相邻分箱组
    # 停止条件：unique_intervals.shape[0] <= min_intervals
    # 停止条件：minimum chi2 > threshold 且 the number of unique_intervals <= max_intervals
    while (((chi2_array.min() <= threshold) or (unique_intervals.shape[0] > max_intervals)) and
           (unique_intervals.shape[0] > min_intervals)):
        # 识别具有最小 chi2 分数的相邻对的索引
        index_adjacent_to_merge, = np.where(chi2_array == chi2_array.min())
        # 确定 chi2 分数最小的区间（或区间）
        i_merge = adjacent_index[index_adjacent_to_merge, :]
        # 将每个选定对的区间合并为一个新区间
        new_interval = np.array([(unique_intervals[:, 0][unique_intervals[:, 1] == index[0]][0],
                                  index[1]) for index in i_merge])

        # 删除选定的间隔并添加合并的间隔
        index_delete_merged = np.array(
            [np.where(unique_intervals[:, 1] == e)[0][0] for e in i_merge.reshape(1, -1)[0]])
        unique_intervals = np.vstack((
            np.delete(unique_intervals, index_delete_merged, axis=0), new_interval))
        unique_intervals.sort(axis=0)

        # 使用新的分箱阈值，对值进行重新分配
        intervals, unique_intervals = assign_interval_unique(x, unique_intervals[:, 1])
        pt_value, pt_column, pt_index = pivot_table(intervals[:, 1], y)
        # 对每对 m 个相邻区间执行卡方检验，使用第 i 个区间的索引作为区间对的索引
        adjacent_index, chi2_array = BinsChiTest(m, pt_value, pt_column, pt_index)

    return unique_intervals[:, 1].tolist()


class Chi2Bins(WOEMixin):
    """ chi2 分箱 """
    bins: Optional[Union[int, List[Union[int, float]]]]

    def __init__(
            self,
            variables: Series,
            target: Series,
            init_bins: Optional[int] = 10,
            min_bins: Optional[int] = 3,
            max_bins: Optional[int] = 5,
            m: Optional[int] = 2,
            abnormal_vals: Optional[List[Union[str, int, float]]] = None,
            fill_bin: Optional[bool] = True,
            confidence_level: Optional[float] = 0.9,
            decimal: Optional[int] = 6,
            weight: Optional[Any] = None,
            *args: Any,
            **kwargs: Any,
    ):
        """
        描述：Chi2Bins 分箱

        :param variables: 待分箱变量
        :param target: 目标标签变量
        :param init_bins: 初始化分箱数量，在此分箱数量基础上进行等频分箱，再依据卡方检验进行分箱的合并
        :param min_bins: 最小的分箱数量
        :param max_bins: 最大的分箱数量
        :param m: 目标变量类别数
        :param abnormal_vals: 特殊值分箱，在变量存在特殊值时单独分一箱，如 -1111, -9999。
        :param fill_bin: 在各分箱中偶发性会出现 good 或 bad 为 0 的情况，默认 fill_bin 为 True ，为该分箱填充 0.5。
        :param confidence_level: 卡方检验置信度

        Example:
            woe = Chi2Bins(variables, target)
            woe.fit()
        """
        self.variables = variables
        self.target = target
        self.init_bins = init_bins
        self.min_bins = min_bins
        self.max_bins = max_bins
        self.m = m
        self.abnormal_vals = abnormal_vals
        self.fill_bin = fill_bin
        self.confidence_level = confidence_level
        self.decimal = decimal
        self.args = args
        self.kwargs = kwargs
        self.data_prepare(
            variables=variables, target=target, weight=weight)

    def fit(
            self,
            score: Optional[bool] = True,
            origin_border: Optional[bool] = False,
            order: Optional[bool] = True,
            **kwargs: Any,
    ) -> DataFrame:
        """
        :param score: 是否增加 WOEMixin score。
        :param origin_border: 是否增加 分箱中的最大值与最小值。
        :param order: 是否增加单调性判断。
        :return: DataFrame WOEMixin result.
        """
        self.bins = chi_merge_vector(
            self.variables.to_numpy(), self.target.to_numpy(), m=self.m,
            confidence_level=self.confidence_level, max_intervals=self.max_bins,
            min_intervals=self.min_bins, initial_intervals=self.init_bins,)
        self.bins = self.bins
        self.bins.insert(0, -np.inf)
        _bucket, _bins = pd.cut(
            self.df_data.variables, self.bins, include_lowest=True, retbins=True, duplicates="drop")
        bucket = pd.DataFrame({
            'variables': self.df_data.variables,
            'target': self.df_data.target,
            'bucket': _bucket,
        }).groupby('bucket', as_index=True, observed=False)
        self.cal_woe_iv(bucket, score=score, origin_border=origin_border, order=order)
        return self.woe
