

from pyspark.sql import functions as F
from pyspark.sql.types import StringType
from hashlib import md5

@F.udf(returnType=StringType())
def MD5(x):
    """MD5生成器"""
    return md5(str(x).encode("utf8")).hexdigest()

# @F.udf(returnType=StringType())
def get_boundary(base_value, e=1):
    """
    描述：数值的区间脱敏，将数据转化为区间。

    参数：
    :param base_value: 区间脱敏
    :param e: 脱敏幂次

    示例：
    >>> df_sample = df_sample.withColumn('income', get_boundary(1000)(df_sample.income))
    1000为最低区分区间。
    """

    def f(value):
        try:
            value = float(value)
        except:
            return None

        if 'inf' in str(value):
            return str(value)

        # 正负值掩码
        mask = 1 if value >= 0 else -1

        # base_value 以内不进行分段区分
        value = value * mask
        if value < base_value and mask > 0:
            return f'[0, {base_value})'
        if value < base_value and mask < 0:
            return f'[-{base_value}, 0)'

        p = len(str(int(value))) - e

        low = int(value / float(f'1e{p}'))
        if mask >= 0:
            res = '[{}, {})'.format(str(int(mask * float(f'{low}e{p}'))), str(int(mask * float(f'{low + 1}e{p}'))))
        else:
            if value == float(f'{low}e{p}'):
                res = '[{1}, {0})'.format(str(int(mask * float(f'{low - 1}e{p}'))),
                                          str(int(mask * float(f'{low}e{p}'))))
            else:
                res = '[{1}, {0})'.format(str(int(mask * float(f'{low}e{p}'))),
                                          str(int(mask * float(f'{low + 1}e{p}'))))
        return res

    udf_fun = F.udf(f, returnType=StringType())
    return udf_fun

