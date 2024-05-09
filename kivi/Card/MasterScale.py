

from .utils import *


class MasterScale(BetaDistribution):

    def __init__(self, current_rank_rate: list, target_level: int, samples: int = 1e6):
        """
        初始化
        :param current_rank_rate: 目前评级分布，即目前每一个评级的占比
        :param target_level: 目标细分评级等级数
        :param samples: 随机数模拟 Beta 分布样本数
        """
        super(MasterScale).__init__()
        self.samples = samples
        self.current_rank_rate = current_rank_rate
        self.target_level = target_level
        self.grades = np.arange(1, self.target_level + 1e-6)

        # 计算目前评级分布的 Beta 分布参数
        self.__cal_beta_params()

    def __generate_random(self, ):
        """
        生成模拟Beta分布的随机数样本
            1. [0, 1] 内划分 current_rank_rate 个间断
            2. 在间断点内按照相应比例生成均匀分布随机数
        :return: 随机数序列
        """
        arange = np.arange(0, 1 + 1e-6, 1 / len(self.current_rank_rate))
        random_nums = np.array([])
        for i, level_rate in enumerate(self.current_rank_rate):
            level_random = np.random.uniform(
                low=arange[i],
                high=arange[i + 1],
                size=int(level_rate * self.samples)
            )
            random_nums = np.hstack((random_nums, level_random))
        return random_nums

    def __cal_beta_params(self, ):
        """
        计算 Beta 分布的分布参数
        :return: None
        """
        # 生成模拟随机数
        random_nums = self.__generate_random()
        # 计算分布参数
        self.Alpha, self.Beta, lower, upper = beta.fit(random_nums, floc=0, fscale=1)

    def cal_quantile(self, ranking: np.array, target_grade: int):
        """
        计算真实 PD 或 Score 排序下的新主标尺分布
        :param ranking: 真实排序 PD or Score
        :param target_grade: 目标主标尺总等级
        :return:
        """
        target_grade_rate, CDF = self.grade_rate(target_grade)
        # 计算 Beta 分布下分位点的 PD 或 Score 值
        quantile = [np.quantile(ranking, cdf) for cdf in CDF]
        # 新主标尺评级等级
        levels = np.empty_like(ranking)
        # 评级赋值
        for level in range(target_grade):
            if level == 0:
                levels[ranking <= quantile[level]] = level
            else:
                levels[np.logical_and(ranking <= quantile[level], ranking > quantile[level - 1])] = level

    def fit_grade_df(self, grade: np.array, df: np.array, log_df=True):
        """
        线性拟合
        :param grade: 等级
        :param df: 等级对应的 Default rate
        :param log_df: 是否对 Default rate 取对数，默认为 True
        :return: None
        """
        import statsmodels.api as sm
        X = sm.add_constant(grade)
        if log_df:
            self.OLS_model = sm.OLS(np.log(df), X).fit(disp=False)
        else:
            self.OLS_model = sm.OLS(df, X).fit(disp=False)
        self.intercept, self.coef = self.OLS_model.params.tolist()

        # 添加常数项
        pre_X = sm.add_constant(self.grades)
        self.grade_df = np.e**(self.OLS_model.predict(pre_X, 1))

    def confirm_master_scale(self, grade_df=None):
        """
        确认评级等级的PD，即评级等级PD的上下界
        :return: 结果在 class.master_scale
        """
        if grade_df:
            grade_df_mean = (grade_df[1:] + grade_df[:-1]) / 2
        else:
            grade_df_mean = (self.grade_df[1:] + self.grade_df[:-1]) / 2
        grade_df_min = np.hstack((np.array([0]), grade_df_mean))
        grade_df_max = np.hstack((grade_df_mean, np.array([1])))
        self.master_scale = pd.DataFrame({
            'grades': self.grades,
            'grade_df_min': grade_df_min,
            'grade_df': self.grade_df,
            'grade_df_max': grade_df_max,
        })

    def plot_grade_rate(self, grades: int):
        """
        根据 Beta 分布绘制 hist
        :param grades: hist nums
        :return: plt.show()
        """
        target_grade_rate, cdf = self.grade_rate(grades)
        plt.figure(figsize=(8, 4), dpi=200)
        plt.bar(range(1, len(target_grade_rate) + 1), target_grade_rate)
        for x, y in zip(range(1, len(target_grade_rate) + 1), target_grade_rate):
            plt.text(x - 0.5, y + 0.001, f'{y * 100: .1f}%', fontsize=6)
        return plt.show()
