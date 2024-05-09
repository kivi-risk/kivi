import pandas as pd
from ..Utils import sortColumns

class AnalysisCategory:

    def __init__(self, cateData, target='target'):
        """
        分析离散型数据:
            - 在有 target 参数的情况下详细分析，category data 的出现频率与相应的 target 表现。
            - 在无 target 参数的情况下返回 category 的出现频率信息。
        :param cateData: 离散数据 DataFrame
        """
        self.cateData = cateData
        self.target = target

    def CategoryInfo(self, ):

        """

        :return: 返回分析结果 cateInfo
        """

        cateDataCol = self.cateData.columns
        cateInfo = pd.DataFrame()

        if self.target in cateDataCol:
            totalDefault = self.cateData['target'].sum()
            for col in cateDataCol:
                if col != self.target:
                    # Sample Group and Group Rate
                    _df = pd.DataFrame(self.cateData[col].value_counts(sort=False))
                    _df.rename(columns={col: col + '_' + 'count'}, inplace=True)
                    _df[col + '_count_' + 'rate'] = _df[col + '_' + 'count'] / len(self.cateData)

                    # col name for Default analysis
                    _tempCols = [col, self.target]
                    _df[col + '_default_count'] = self.cateData[_tempCols].groupby(col).sum()[self.target]
                    _df[col + '_default_rate'] = _df[col + '_default_count'] / totalDefault
                    _df[col] = _df.index
                    _df.reset_index(drop=True, inplace=True)
                    if len(cateInfo) == 0:
                        cateInfo = _df
                    else:
                        cateInfo = pd.merge(cateInfo, _df, left_index=True, right_index=True, how='outer')

            newCols = sortColumns(cateInfo.count())
            cateInfo = cateInfo[newCols]
            cateInfo.dropna(axis=1, how='all', inplace=True)

            return cateInfo

        else:

            cateInfo = {}
            maxLength = 0

            for col in cateDataCol:
                _s = self.cateData[col].value_counts(dropna=True)
                cateInfo[col] = _s.index.to_list()
                cateInfo[col + '_' + 'Count'] = _s.to_list()
                cateInfo[col + '_' + 'rate'] = [item / _s.sum() for item in _s]

                if len(_s) >= maxLength:
                    maxLength = len(_s)

            for key in cateInfo.keys():
                if maxLength > len(cateInfo.get(key)):
                    cateInfo[key] = cateInfo[key] + [None] * (maxLength - len(cateInfo.get(key)))

            return pd.DataFrame(cateInfo)

