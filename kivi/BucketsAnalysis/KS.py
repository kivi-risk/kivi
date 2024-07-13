import os
import pandas as pd
from pandas import DataFrame, Series
from pandas.api.types import is_string_dtype, is_object_dtype, is_numeric_dtype
from ..utils.utils import saveCsv
from ..utils.Bins import Bins


class KS(Bins):

    def __init__(self, csvName=None, imageName=None, jupyterNotebook=True):
        """
        Des: KS 初始化
        :param csvName: 保存csv计算过程文件
        :param imageName: 保存ks图像
        :param jupyterNotebook 是否显示在JupyterNotebook中
        """
        super(KS, self).__init__()
        self.csvName = csvName
        self.imageName = imageName
        self.jupyterNotebook = jupyterNotebook

    def _ks(self, variables, target, **kwargs):
        """
        Des: KS 方法中的内部核心计算函数
        :param variables:
        :param target:
        :param kwargs:
        :return:
        """

        kwargs.setdefault('category', False)

        from numpy import abs
        total = len(target)
        total_bad = target.sum()

        if kwargs['category']:
            bucket = pd.DataFrame({
                'variables': variables,
                'target': target,
            }).groupby('variables', as_index=True)
        else:
            bucket = pd.DataFrame({
                'variables': variables,
                'target': target,
                'bucket': pd.cut(variables, self.cutoffPoint, include_lowest=True)
            }).groupby('bucket', as_index=True)

        res = pd.DataFrame({
            'min_bin': bucket.variables.min(),
            'max_bin': bucket.variables.max(),
            'bad': bucket.target.sum(),
            'total': bucket.target.count(),
        })

        res['good'] = res['total'] - res['bad']
        res['bad_rate'] = res['bad'] / res['total']  # 每个箱体中好样本所占总样本数的比例
        res['total_rate'] = res['total'] / total
        res['cum_bad_rate'] = res.bad.cumsum() / total_bad
        res['cum_good_rate'] = res.good.cumsum() / (total - total_bad)
        res['ks'] = abs(res.cum_bad_rate - res.cum_good_rate)
        res = res[[
            'min_bin', 'max_bin', 'total',
            'total_rate', 'good', 'bad',
            'bad_rate', 'cum_bad_rate',
            'cum_good_rate', 'ks']]
        return res, res.ks.max()

    def Continue(
            self,
            variables: Series,
            target: Series,
            bins=10,
            binType='distance'):
        """
        Des: 连续变量的KS值计算
        :param variables: 连续变量
        :param target: target
        :param bins: 分箱数目
        :param binType: 分箱方式: 等距'distance', 等频'frequency'
        :return: res, ks
        """

        variables.dropna(inplace=True)
        target.dropna(inplace=True)

        variablesMin = variables.min()
        variablesMax = variables.max()

        if not pd.api.types.is_numeric_dtype(variables):
            raise Exception(TypeError, 'variables must be numeric!')

        if not pd.api.types.is_numeric_dtype(target):
            raise Exception(TypeError, 'target must be numeric!')

        if variablesMax == variablesMin:
            raise Exception()

        if binType == 'distance':
            self.cutoffPoint = self._cutoffPoint(
                bins=bins, min=variablesMin, max=variablesMax)
        if binType == 'frequency':
            self.cutoffPoint = self._cutoffPoint(
                bins=bins, percent=True, expected=variables)

        self.res, self.ks = self._ks(variables, target)

        if self.csvName:
            saveCsv(self.res, self.csvName)
            return self.ks
        else:
            return self.res, self.ks

    def Category(self, variables: Series, target: Series):
        """
        Des: 对于类别型变量的KS值计算
        :param variables: 类别变量
        :param target: target
        :return: res, ks
        """

        variables = variables.dropna()
        target = target.dropna()

        if (not is_string_dtype(variables)) or (not is_object_dtype(variables)):
            raise Exception(TypeError, 'variables must be string or object!')
        if not is_numeric_dtype(target):
            raise Exception(TypeError, 'target must be numeric!')

        self.res, self.ks = self._ks(variables, target, category=True)

        if self.csvName:
            saveCsv(self.res, self.csvName)
            return self.ks
        else:
            return self.res, self.ks

    def KSPlot(self, **kwargs):
        """
        Des: 绘制 KS 曲线
        :param kwargs:
            # 图像样式
            style[str] = 'seaborn',
            # 宽，高
            figsize[tuple] = (9, 5),
            # 分辨率
            dpi[int] = 150,
            # x 轴名称
            x_label[str] = 'bucket',
            # label 字体大小
            labelfontsize[int] = 10,
            # tick 字体大小
            tickfontsize[int] = 8,
            # title 字体大小
            titlefontsize[int] = 12,
        :return: plt.show() or None
        """
        from numpy import argmax

        kwargs.setdefault('style', 'seaborn')
        kwargs.setdefault('figsize', (9, 5))
        kwargs.setdefault('dpi', 150)
        kwargs.setdefault('labelfontsize', 10)
        kwargs.setdefault('tickfontsize', 8)
        kwargs.setdefault('titlefontsize', 12)
        kwargs.setdefault('x_label', 'bucket')

        markLineData = self.res[self.res.ks == self.ks]

        cumGood, cumBad = float(
            markLineData['cum_good_rate']), float(
            markLineData['cum_bad_rate'])

        if isinstance(self.res.min_bin.to_list()[0], int):
            group = self.res.min_bin.astype(
                str) + '-' + self.res.max_bin.astype(str)
            ksBinMin, ksBinMax = int(
                markLineData['min_bin']), int(
                markLineData['max_bin'])

        if isinstance(self.res.min_bin.to_list()[0], float):
            group = self.res.min_bin.round(2).astype(
                str) + '-' + self.res.max_bin.round(2).astype(str)
            ksBinMin, ksBinMax = float(
                markLineData['min_bin'].round(2)), float(
                markLineData['max_bin'].round(2))

        bucket = '[' + str(ksBinMin) + ', ' + str(ksBinMax) + ']'

        import matplotlib.pyplot as plt
        plt.style.use(kwargs.get('style'))
        fig, axs = plt.subplots(
            figsize=kwargs.get('figsize'),
            dpi=kwargs.get('dpi')
        )
        axs.plot(
            group,
            self.res.ks * 100,
            marker='o',
            linewidth=3,
            c='tab:blue')
        axs.plot(
            group,
            self.res.cum_good_rate *
            100,
            marker='o',
            linewidth=3,
            c='tab:green')
        axs.plot(
            group,
            self.res.cum_bad_rate *
            100,
            marker='o',
            linewidth=3,
            c='tab:red')

        # 参考线
        axs.axvline(x=argmax(self.res.ks.to_list()), linestyle='--', c='gray')
        axs.axhline(y=self.ks * 100, linestyle='--', c='tab:blue')
        axs.axhline(y=cumGood * 100, linestyle='--', c='tab:green')
        axs.axhline(y=cumBad * 100, linestyle='--', c='tab:red')

        axs.set_title(
            f'KS = {self.ks * 100: .2f}% at bucket {bucket}',
            fontsize=kwargs.get('titlefontsize'))
        axs.legend(fontsize=kwargs.get('tickfontsize'))

        axs.set_xlabel(
            kwargs.get('x_label'),
            fontsize=kwargs.get('labelfontsize'),
        )
        axs.set_ylabel(
            r'$Rate(\%)$',
            fontsize=kwargs.get('labelfontsize'),)
        axs.tick_params(axis="x", labelsize=kwargs.get('tickfontsize'))
        axs.tick_params(axis="y", labelsize=kwargs.get('tickfontsize'))
        axs.grid(True)
        return plt.show()

    def KSValue(self, variables, target):
        """
        Des: 计算KS值，计算KS-test的P-value
        :param variables:
        :param target:
        :return: ks_value, p_value
        """
        from scipy.stats import ks_2samp
        get_ks = lambda variables, target: ks_2samp(variables[target == 1], variables[target == 0])
        ks_value, p_value = get_ks(variables, target)
        return ks_value, p_value

    def ROCPlot(self, **kwargs):
        """
        Des: 根据KS计算ROC曲线
        :param kwargs: 图像参数['style', 'figsize', 'dpi', 'labelfontsize', title, 'x_label', 'y_label'……]
        :return: None
        """

        kwargs.setdefault('style', 'seaborn')
        kwargs.setdefault('figsize', (9, 5))
        kwargs.setdefault('dpi', 150)
        kwargs.setdefault('labelfontsize', 10)
        kwargs.setdefault('tickfontsize', 8)
        kwargs.setdefault('titlefontsize', 12)
        kwargs.setdefault('x_label', 'False Positive Rate')
        kwargs.setdefault('y_label', 'True Positive Rate')
        kwargs.setdefault('title', 'Receiver operating characteristic')

        import matplotlib.pyplot as plt
        from numpy import abs, argmax
        plt.style.use(kwargs.get('style'))
        fig, axs = plt.subplots(
            figsize=kwargs.get('figsize'),
            dpi=kwargs.get('dpi')
        )

        FPR = self.res.cum_good_rate.tolist()
        TPR = self.res.cum_bad_rate.tolist()
        FPR.insert(0, 0)
        TPR.insert(0, 0)
        axs.plot(FPR, TPR, marker='o',
                 linewidth=3,
                 c='tab:green',
                 label='$ROC\ curve$',
                 )

        axs.plot([0, 1], [0, 1], linestyle='--', c='gray')

        maxIndex = argmax(abs(self.res.cum_bad_rate -
                              self.res.cum_good_rate).tolist())
        axs.scatter(
            self.res.cum_good_rate[maxIndex],
            self.res.cum_bad_rate[maxIndex],
            alpha=0.8,
            marker='*',
            s=100,
            color='tab:red',
            label='$KS\ max\|cum\_bad\_rate-cum\_good\_rate\|$'
        ).set_zorder(10)

        axs.set_title(
            kwargs.get('title'),
            fontsize=kwargs.get('titlefontsize'))
        axs.legend(fontsize=kwargs.get('tickfontsize'))

        axs.set_xlabel(
            kwargs.get('x_label'),
            fontsize=kwargs.get('labelfontsize'),
        )
        axs.set_ylabel(
            kwargs.get('y_label'),
            fontsize=kwargs.get('labelfontsize'),
        )

        if self.imageName:
            if not os.path.exists('img'):
                os.mkdir('img')
            plt.savefig(f'./img/{self.imageName}_roc.png', )
            return None
        else:
            return plt.show()

    def Distribution(self, data: dict, **kwargs):
        """
        Des: 绘制多个样本的分布情况
        :param data: 数据
        :param kwargs: 图像参数['style', 'figsize', 'dpi', 'labelfontsize', title, 'x_label', 'y_label'……]
        :return: plt.plot
        """

        kwargs.setdefault('style', 'seaborn')
        kwargs.setdefault('figsize', (9, 5))
        kwargs.setdefault('dpi', 150)
        kwargs.setdefault('labelfontsize', 10)
        kwargs.setdefault('tickfontsize', 8)
        kwargs.setdefault('titlefontsize', 12)
        kwargs.setdefault('x_label', 'Variable')
        kwargs.setdefault('y_label', 'Frequency')
        kwargs.setdefault('title', 'Distribution')

        import seaborn as sns
        import matplotlib.pyplot as plt

        plt.style.use(kwargs.get('style'))

        fig, axs = plt.subplots(
            figsize=kwargs.get('figsize'),
            dpi=kwargs.get('dpi')
        )

        with sns.color_palette("muted", n_colors=len(data)):
            for name, item in data.items():
                sns.distplot(item, label=name)

        axs.legend()

        axs.set_title(
            kwargs.get('title'),
            fontsize=kwargs.get('titlefontsize'))

        axs.set_xlabel(
            kwargs.get('x_label'),
            fontsize=kwargs.get('labelfontsize'),
        )
        axs.set_ylabel(
            kwargs.get('y_label'),
            fontsize=kwargs.get('labelfontsize'),
        )

        if self.imageName:
            if not os.path.exists('img'):
                os.mkdir('img')
            plt.savefig(f'./img/{self.imageName}_distribution.png', )
            return None
        else:
            return plt.show()
