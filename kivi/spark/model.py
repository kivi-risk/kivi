from pyspark.sql import functions as F


def ModelResultSpark(df_match, score_shceme='sigmod'):
    """
    描述：使用spark计算模块结果，计算模型结果

    参数：
    :param df_match: 匹配分数表
    :param score_shceme: 分数计算方案 `simode`, `linear`
    :return pyspark DataFrame 模型结果表

    示例：
    >>>
    """
    if score_shceme == 'simode':
        weight_type = 'coef'
    elif score_shceme == 'linear':
        weight_type = 'wight'

    df_module = df_match.groupBy('load_date', 'uuid', 'module_name').agg(
        (-(F.sum(F.col('woe') * F.col(f'var_{weight_type}')) + F.first('var_intercept'))).alias('module_ln_odds'),
        (1 / (1 + F.exp(-(F.sum(F.col('woe') * F.col(f'var_{weight_type}')) + F.first('var_intercept'))))).alias(
            'module_pd'),
        F.first('k').alias('k'),
        F.first(f'module_{weight_type}').alias(f'module_{weight_type}'),
        F.first('module_intercept').alias('module_intercept'),
        F.first('module_min_pd').alias('module_min_pd'),
        F.first('module_max_pd').alias('module_max_pd'), )

    df_module = df_module.withColumn('sig', F.when(F.col('module_coef') > 0, 1).otherwise(-1)) \
        .withColumn('module_score', ((F.col('sig') * F.lit(100) / (F.col('module_max_pd') - F.col('module_min_pd'))) * (
                F.col('module_pd') - F.col('module_min_pd'))))

    df_model = df_module.groupBy('load_date', 'uuid').agg(
        (-(F.sum(F.col('module_score') * F.col(f'module_{weight_type}')) + F.first('module_intercept'))).alias(
            'modle_ln_odds'),
        (1 / (1 + F.first('k') * F.exp(
            -(F.sum(F.col('module_score') * F.col(f'module_{weight_type}')) + F.first('module_intercept'))))).alias(
            'modle_pd'),
    )
    df_model_result = df_module.join(df_model, on=['load_date', 'uuid'], how='left')

    return df_model_result
