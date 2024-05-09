class Scale:
    """
    数据的归一化方法：
        1. min-max
        2. Z-Score
    :param df: DataFrame
    """
    @staticmethod
    def MinMax(df):
        df = (df - df.min()) / (df.max() - df.min())
        return df

    @staticmethod
    def MeanMinMax(df):
        df = (df - df.mean()) / (df.max() - df.min())
        return df

    @staticmethod
    def ZScore(df):
        df = (df - df.mean()) / df.std()
        return df
