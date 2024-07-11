import os
from typing import Optional
try:
    import pyspark
    from pyspark.sql import SparkSession
    from pyspark import SparkService
except ImportError:
    print("pyspark not installed, please install it first. < pip install pyspark >")


__all__ = [
    "enable_arrow",
    "get_spark",
    "kill_app",
]


def enable_arrow(spark: SparkSession, verbose: Optional[bool] = False) -> None:
    """
    描述：启用 Arrow
    """
    spark.conf.set("spark.sql.execution.arrow.enabled", "true")
    if verbose:
        print(f'Enable Arrow: {spark.conf.get("spark.sql.execution.arrow.enabled")}')


def get_spark(
        app_name: Optional[str] = 'test',
        master: Optional[str] = 'yarn',
        executors: Optional[int] = 2
) -> SparkSession:
    """

    :param app_name:
    :param master: 'yarn', 'local[*]'
    :param executors:
    :return:
    """
    if hasattr(pyspark, "SparkService"):
        extra_param = {
            'spark.app.name': app_name,
            'spark.driver.cores': 2,
            'spark.sql.execution.arrow.pyspark.enabled': 'true',
        }
        spark = SparkService.get_yarn_spark(
            executor_instances=executors,
            per_executor_mem='2g',
            driver_mem='1g',
            extra_param=extra_param,
        )
    elif hasattr(pyspark.sql, 'SparkSession'):
        from pyspark.sql import SparkSession
        builder = SparkSession.builder \
            .appName(app_name) \
            .enableHiveSupport() \
            .master(master) \
            .config("spark.dynamicAllocation.maxExecutors", f"{executors}")
        spark = builder.getOrCreate()
    else:
        raise ValueError("Not support for Spark, please check your env.")
    return spark


def kill_app(app_id: str) -> None:
    """
    描述：kill spark application

    :param app_id: spark app id
    :return:
    """
    info = os.popen(f'yarn application --kill {app_id}').readlines()
    print('\n'.join(info))
