import pandas as pd
from tqdm import tqdm
from ..utils.operator import StatsLogit
from ..ModelEval import RocAucKs
import statsmodels.api as sm


def param_to_weight(model, ret_info, params):
    """"""
    #### 拟合权重
    df_param = pd.DataFrame(model.params.drop('const'), columns=['param'])
    df_param['weight'] = df_param.param * 100 / df_param.param.sum()
    ret_info.update({
        'df_param': df_param,
    })
    return df_param

def eval_model(df_woeval, columns, model):
    """

    :param df_woeval:
    :param columns:
    :param model:
    :return:
    """
    df_endog = sm.add_constant(df_woeval[columns])
    predict = model.predict(df_endog)
    metrics = RocAucKs(df_woeval.target, predict)
    return metrics


def eval_model_train_oot(
        df_woeval_train, df_woeval_oot,
        columns, module, path='', ret=['model', 'df_param'], oot=False, disp=True):
    """

    :param columns:
    :param module:
    :param path:
    :param ret:
    :param oot:
    :param disp:
    :return:
    """
    ret_info = dict()

    #### 训练集评估

    model = StatsLogit(X=df_woeval_train[columns], y=df_woeval_train.target)
    metrics_train = eval_model(df_woeval_train, columns=columns, model=model)
    ret_info.update({
        'model': model,
        'shape_train': df_woeval_train.shape,
        'ks_train': metrics_train.get('ks_train'),
        'auc_train': metrics_train.get('auc_train'),
    })


    metrics_oot = eval_model(df_woeval_oot, columns=columns, model=model)
    ret_info.update({
        'shape_oot': df_woeval_oot.shape,
        'ks_oot': metrics_oot.get('ks_oot'),
        'auc_oot': metrics_oot.get('auc_oot'),
    })



    if disp:
        print(f'指标数量: {len(columns)}')
        print(f"Train dataset: {df_woeval_train.shape}, ks={metrics_train.get('ks_train'):.3f}, auc={metrics_train.get('auc_train'):.3f}")
        if oot: print(f"OOT dataset: {df_woeval_oot.shape}, ks={metrics_oot.get('ks_oot'):.3f}, auc={metrics_oot.get('auc_oot'):.3f}")
        print(model.summary())

    return [ret_info.get(item) for item in ret]

def one_step(model_features, columns, disp=False):
    """
    描述：逐步回归法，要求：
        1. 回归系数同一
        2.

    :param columns:
    :return:
    """
    model_metrics = []
    ret = ['model', 'df_param', 'ks_train', 'auc_train', 'ks_oot', 'auc_oot']

    for col in tqdm(columns):
        if col not in model_features:
            try:
                model_features_new = model_features + [col]
                model, df_param, ks_train, auc_train, ks_oot, auc_oot = eval_model(
                    model_features_new, module, path='', disp=False, ret=ret,
                )
                # 删除系数不统一的
                drop_cols = df_param[df_param.param > 0].index.tolist()

                if len(drop_cols) > 0:
                    model_features_new = list(set(model_features_new) - set(drop_cols))
                    model, df_param, ks_train, auc_train, ks_oot, auc_oot = eval_model(
                        model_features_new, module, path='', disp=False, ret=ret,
                    )
                else:
                    pass

                model_metrics.append({
                    'feature': col,
                    'ks_train': ks_train,
                    'auc_train': auc_train,
                    'ks_oot': ks_oot,
                    'auc_oot': auc_oot,
                })
            except Exception as e:
                if disp:
                    print(f'{col:30}: {e}')
        else:
            pass
    return pd.DataFrame(model_metrics)

def stepwise():
    """"""

    return None

