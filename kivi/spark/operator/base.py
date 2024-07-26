from typing import Callable
from pydantic import Field, BaseModel, ConfigDict
try:
    from pyspark.sql import functions as F
except ImportError:
    print("pyspark not installed, please install it first. < pip install pyspark >")


__all__ = [
    "SparkBaseOperator",
    "spark_base_operator",
]


class SparkBaseOperator(BaseModel):
    """base operator class for spark"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    sum: Callable = Field(default=F.sum)
    avg: Callable = Field(default=F.avg)
    mean: Callable = Field(default=F.mean)
    count: Callable = Field(default=F.count)
    count_distinct: Callable = Field(default=F.countDistinct)
    sum_distinct: Callable = Field(default=F.sumDistinct)
    min: Callable = Field(default=F.min)
    max: Callable = Field(default=F.max)
    first: Callable = Field(default=F.first)
    last: Callable = Field(default=F.last)
    skewness: Callable = Field(default=F.skewness)
    kurtosis: Callable = Field(default=F.kurtosis)
    collect_set: Callable = Field(default=F.collect_set)
    collect_list: Callable = Field(default=F.collect_list)
    approx_count_distinct: Callable = Field(default=F.approx_count_distinct)
    stddev: Callable = Field(default=F.stddev)
    stddev_samp: Callable = Field(default=F.stddev_samp)
    stddev_pop: Callable = Field(default=F.stddev_pop)
    variance: Callable = Field(default=F.variance)
    var_pop: Callable = Field(default=F.var_pop)
    var_samp: Callable = Field(default=F.var_samp)


spark_base_operator = SparkBaseOperator()
