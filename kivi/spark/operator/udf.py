from hashlib import md5
try:
    from pyspark.sql import functions as F
    from pyspark.sql.types import StringType
except ImportError:
    print("pyspark not installed, please install it first. < pip install pyspark >")


__all__ = [
    "md5", "md5_udf",
]


def md5(x):
    """MD5生成器"""
    return md5(str(x).encode("utf8")).hexdigest()


md5_udf = F.udf(f=md5, returnType=StringType())
