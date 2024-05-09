import numpy as np
import pandas as pd


class DefaultAnalysis:
    """
    该方法实现了对于单指标变量的违约分析，并绘制了相应的违约概率图。
    目前该方法支持对于等距等频Woe的分析。
    """

    def __init__(self, woe,
                 col=None,
                 sortBy='bad',
                 title='违约概率分析', subtitle=None,
                 imageName=None, csvName=None,
                 jupyterNoteBook=True,
                 width=None, height=None,
                 _round=4):
        """
        :param woe: 需要分析的 Woe or DataFrame
        :param sortBy: good, bad, sampleRate, badRateInBin, default='bad'
        :param title: 图表的Title
        :param subtitle: 图表的SubTitle
        :param imageName: 图片保存的名称
        :param csvName: Woe表格信息保存的名字
        :param jupyterNoteBook: 是否在返回JupyterNotebook显示对象
        :param width: 图像宽度
        :param height: 图像高度
        :param _round: 小数点位数
        """
        self.woe = woe
        self.sortBy = sortBy

        self.title = title
        self.subtitle = subtitle
        self.imageName = imageName
        self.csvName = csvName
        self.jupyterNoteBook = jupyterNoteBook
        self.width = width
        self.height = height
        self._round = _round

        self.df = woe
        self.col = col

    def __analysisWoe(self, ):
        woe = self.woe
        Samples = self.woe.total.sum()
        woe['sampleRate'] = woe.total / Samples
        woe['badRateInBin'] = woe.bad / woe.total
        woe['center'] = (woe.max_bin + woe.min_bin) / 2
        woe['scaleCenter'] = (woe.center - woe.center.min()) / \
                             (woe.center.max() - woe.center.min())
        woe['Bucket'] = '[' + \
                        woe.min_bin.astype(str) + ', ' + woe.max_bin.astype(str) + ']'
        return woe

    def __analysisCate(self, ):

        samples = len(self.df)
        groupNameList = []
        goodList = []
        badList = []
        sampleRate = []
        badRateInBin = []
        countList = []

        for groupName, group in self.df.groupby(by=self.col):
            count = len(group)
            bad = group.target.sum()
            good = count - bad

            groupNameList.append(groupName)
            goodList.append(int(good))
            badList.append(int(bad))
            sampleRate.append(float(count / samples))
            badRateInBin.append(float(int(bad) / int(count)))
            countList.append(count)

        dfCate = pd.DataFrame(
            {
                'groupName': groupNameList,
                'Count': countList,
                'bad': badList,
                'good': goodList,
                'sampleRate': sampleRate,
                'badRateInBin': badRateInBin,
            }
        )
        dfCate.sort_values(by=self.sortBy, inplace=True)
        return dfCate


    def DefaultFreGraph(self, ) -> Grid:

        woe = self.__analysisWoe()

        xData = woe.Bucket.to_list()
        goodSample = (woe.total - woe.bad).to_list()
        badSample = woe.bad.to_list()
        badRateInBin = (woe.badRateInBin.round(self._round) * 100).to_list()
        sampleRate = (woe.sampleRate.round(self._round) * 100).to_list()

        totalNums = woe.total.sum()
        badNums = woe.bad.sum()
        goodNums = totalNums - badNums
        badRate = np.round(badNums / totalNums, self._round) * 100

    def DefaultCateGraph(self, ) -> Grid:

        dfCate = self.__analysisCate().round(self._round)

        xData = dfCate.groupName.to_list()
        badSample = dfCate.bad.to_list()
        goodSample = dfCate.good.to_list()
        badRateInBin = dfCate.badRateInBin.to_list()
        sampleRate = dfCate.sampleRate.to_list()

        totalNums = dfCate.Count.sum()
        goodNums = dfCate.good.sum()
        badNums = dfCate.bad.sum()
        badRate = round(badNums / totalNums, self._round)


    def DefaultCatePng(self, title='None title', sort_by=None, width=0.35, rotation=30, **kwargs):
        """

        :param title:
        :param sort_by: bad good bad_rate sample_rate
        :param width:
        :return:
        """
        import matplotlib.pyplot as plt

        dfCate = self.__analysisCate().round(self._round)

        xData = dfCate.groupName.to_list()
        badSample = dfCate.bad.to_list()
        goodSample = dfCate.good.to_list()
        badRateInBin = dfCate.badRateInBin.to_list()
        sampleRate = dfCate.sampleRate.to_list()

        totalNums = dfCate.Count.sum()
        goodNums = dfCate.good.sum()
        badNums = dfCate.bad.sum()
        badRate = round(badNums / totalNums, self._round)

        data = pd.DataFrame(
            {
                'labels': xData,
                'bad': badSample,
                'good': goodSample,
                'bad_rate': badRateInBin,
                'sample_rate': sampleRate,
            }
        )

        if sort_by:
            data.sort_values(by=sort_by, inplace=True)

        x = np.arange(len(data.labels))  # the label locations

        fig, ax = plt.subplots(2, 1, figsize=(10, 10), dpi=120)
        rects1 = ax[0].bar(x - width / 2, data.bad, width, label='bad', color='tab:red', alpha=0.7)
        rects2 = ax[0].bar(x + width / 2, data.good, width, label='good', color='tab:green', alpha=0.7)

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax[0].set_ylabel('Samples')
        if kwargs.get('font'):
            ax[0].set_title(title, fontproperties=kwargs.get('font'))
        else:
            ax[0].set_title(title)
        ax[0].set_xticks(x)
        ax[0].set_xticklabels(data.labels)
        ax[0].legend()
        ax[0].xaxis.set_tick_params(rotation=rotation, labelsize=10)

        def autolabel(rects):
            """Attach a text label above each bar in *rects*, displaying its height."""
            for rect in rects:
                height = rect.get_height()
                ax[0].annotate('{}'.format(height),
                               xy=(rect.get_x() + rect.get_width() / 2, height),
                               xytext=(0, 3),  # 3 points vertical offset
                               textcoords="offset points",
                               ha='center', va='bottom')

        line_ax = ax[1]
        _line_ax = line_ax.twinx()
        line1 = line_ax.plot(x, data.bad_rate, label='bad rate in bin', color='tab:red')
        line2 = _line_ax.plot(x, data.sample_rate, label='sample rate', color='tab:green')
        ax[1].set_xticks(x)
        ax[1].set_xticklabels(data.labels)
        ax[1].legend()
        _line_ax.legend()
        ax[1].set_ylabel('rate')
        ax[1].set_xlabel(f'Total sample: {totalNums} Good: {goodNums} Bad: {badNums} Bad rate: {badRate}')
        ax[1].xaxis.set_tick_params(rotation=rotation, labelsize=10)

        autolabel(rects1)
        autolabel(rects2)

        fig.tight_layout()


def plot_bin(
        df,
        title='None title',
        sort_by=None,
        width=0.35,
        rotation=30,
        _round=4,
        **kwargs
    ):
    """

    :param title:
    :param sort_by: bad good bad_rate sample_rate
    :param width:
    :return:
    """
    labels = df.min_bin.astype(str) + '_' + df.max_bin.astype(str)
    badSample = df.bad
    goodSample = df.total - df.bad
    badRateInBin = df.bad_rate
    sampleRate = df.total/df.total.sum()
    totalNums = df.total.sum()
    goodNums = goodSample.sum()
    badNums = df.bad.sum()
    badRate = round(badNums / totalNums, _round)

    import matplotlib.pyplot as plt

    data = pd.DataFrame(
        {
            'labels': labels,
            'bad': badSample,
            'good': goodSample,
            'bad_rate': badRateInBin,
            'sample_rate': sampleRate,
        }
    )

    if sort_by:
        data.sort_values(by=sort_by, inplace=True)

    x = np.arange(len(data.labels))  # the label locations

    fig, ax = plt.subplots(2, 1, figsize=(10, 10), dpi=120)
    rects1 = ax[0].bar(x - width / 2, data.bad, width, label='bad', color='tab:red', alpha=0.7)
    rects2 = ax[0].bar(x + width / 2, data.good, width, label='good', color='tab:green', alpha=0.7)

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax[0].set_ylabel('Samples')
    if kwargs.get('font'):
        ax[0].set_title(title, fontproperties=kwargs.get('font'))
    else:
        ax[0].set_title(title)
    ax[0].set_xticks(x)
    ax[0].set_xticklabels(data.labels)
    ax[0].legend()
    ax[0].xaxis.set_tick_params(rotation=rotation, labelsize=10)

    def autolabel(rects):
        """Attach a text label above each bar in *rects*, displaying its height."""
        for rect in rects:
            height = rect.get_height()
            ax[0].annotate('{}'.format(height),
                           xy=(rect.get_x() + rect.get_width() / 2, height),
                           xytext=(0, 3),  # 3 points vertical offset
                           textcoords="offset points",
                           ha='center', va='bottom')

    line_ax = ax[1]
    _line_ax = line_ax.twinx()
    line1 = line_ax.plot(x, data.bad_rate, label='bad rate in bin', color='tab:red')
    line2 = _line_ax.plot(x, data.sample_rate, label='sample rate', color='tab:green')
    ax[1].set_xticks(x)
    ax[1].set_xticklabels(data.labels)
    ax[1].legend()
    _line_ax.legend()
    ax[1].set_ylabel('rate')
    ax[1].set_xlabel(f'Total sample: {totalNums} Good: {goodNums} Bad: {badNums} Bad rate: {badRate}')
    ax[1].xaxis.set_tick_params(rotation=rotation, labelsize=10)

    autolabel(rects1)
    autolabel(rects2)

    fig.tight_layout()
    return None
