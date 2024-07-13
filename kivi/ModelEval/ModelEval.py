import numpy as np
import pandas as pd
from ..utils.operator import StatsLogit, NumRange
import statsmodels.api as sm
from ..BucketsAnalysis import psi

import matplotlib.pyplot as plt
from sklearn.metrics import roc_auc_score, roc_curve, recall_score, precision_recall_curve


__all__ = [
    "RocAucKs"
]


def RocAucKs(true, predict, predict_binary=None):
    """
    描述：输出预测值与真实值的 AUC KS
    :param true: 真实值
    :param predict: 预测值（概率）
    :param predict_binary: 预测值（二分类）
    :return:
    """
    metrics_info = dict()
    fpr, tpr, _ = roc_curve(true, predict)
    ks = abs(fpr - tpr).max()

    metrics_info.update({
        'fpr': fpr,
        'tpr': tpr,
        'auc': roc_auc_score(true, predict),
        'ks': ks,
    })

    if predict_binary:
        metrics_info.update({
            'recall': recall_score(true, predict_binary)})
    return metrics_info

def PlotAucRocKS(y_true, y_pre, title=None, lw=2):
    """
    描述: 绘制 Roc 图，并标注 auc 和 ks
    :param y_true: 真实值
    :param y_pre: 预测值
    :param title: 图片的标题
    :param lw: 线条宽度
    :return: None
    """
    auc_area = roc_auc_score(y_true, y_pre)
    fpr, tpr, thresholds = roc_curve(y_true, y_pre)

    plt.plot(
        fpr, tpr, color='darkorange', lw=lw,
        label=f'ROC curve (area = {auc_area:.4f}, ks = {max(abs(fpr-tpr)):.4f})')

    plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    if title is None:
        plt.title('Receiver operating characteristic')
    else:
        plt.title(title)
    plt.legend(loc="lower right")
    plt.show()

def lift(df_score, bins=20, border=None, score_name='score', target_name='target'):
    """
    描述：计算模型结果的lift

    :param df_score: DataFrame 评分、PD 结果文件。
    :param bins: 分箱数量。
    :param border: 分数的最大最小边界， [min, max]。
    :param score_name: 分数字段名称。
    :param target_name: 目标变量名称。
    :return:
    """
    df_score = df_score[[score_name, target_name]].copy()
    if border is None:
        bins = np.linspace(df_score[score_name].min(), df_score[score_name].max(), bins + 1)
    else:
        bins = np.linspace(*border, bins + 1)
    df_score["buckets"] = pd.cut(df_score[score_name], bins=bins, include_lowest=True)

    df_buckets = df_score.groupby('buckets').agg({target_name: ['count', 'sum']})
    df_buckets.columns = ['total', 'bad']
    df_buckets['good'] = df_buckets.total - df_buckets.bad
    df_buckets['bad_rate'] = df_buckets.bad / df_buckets.total

    df_buckets['cum_total'] = df_buckets.total.cumsum() / df_buckets.total.sum()
    df_buckets['cum_bad'] = df_buckets.bad.cumsum() / df_buckets.bad.sum()
    df_buckets['cum_good'] = df_buckets.good.cumsum() / df_buckets.good.sum()
    df_buckets['ks'] = df_buckets.cum_bad - df_buckets.cum_good
    df_buckets['lift'] = df_buckets.cum_bad / df_buckets.cum_total
    return df_buckets

def lift_compare(df_train, df_oot, columns=None, bins=20, border=None, score_name='score', psi_val=True, target_name='target'):
    """

    :param df_train: 训练集分数。
    :param df_oot: 测试集分数。
    :param columns: 字段名称。
    :param bins: 分箱数量。
    :param border: 分数的最大最小边界， [min, max]。
    :param score_name: 分数字段名称。
    :param psi_val: 是否评估训练集和测试集的PSI。
    :param target_name: 目标变量名称。
    :return:
    """
    if columns is None:
        columns = ['total', 'bad', 'bad_rate', 'ks', 'lift',]

    df_lift_train = lift(df_train, bins=bins, border=border, score_name=score_name, target_name=target_name)
    df_lift_train = df_lift_train[columns]
    df_lift_train.columns = [f'{col}-train' for col in df_lift_train.columns.tolist()]

    df_lift_oot = lift(df_oot, bins=bins, border=border, score_name=score_name, target_name=target_name)
    df_lift_oot = df_lift_oot[columns]
    df_lift_oot.columns = [f'{col}-oot' for col in df_lift_oot.columns.tolist()]

    df_lift = df_lift_train.join(df_lift_oot, how='outer')

    if psi_val:
        df_lift = psi(df_lift, ex_name='total-train', ac_name='total-oot', )

    return df_lift[[
        'total-train', 'bad-train', 'bad_rate-train', 'ks-train', 'lift-train',
        'total-oot', 'bad-oot', 'bad_rate-oot', 'ks-oot', 'lift-oot', 'psi_val', 'psi']]

def PlotPrecisionRecall(y_true, y_pre):
    '''
    描述: 绘制 P-R 曲线；
    :param y_true: 真实值
    :param y_pre: 预测值
    :return: None
    '''
    precision, recall, thresholds = precision_recall_curve(y_true, y_pre)
    plt.figure("P-R Curve")
    plt.title('Precision/Recall Curve')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.plot(recall, precision)
    plt.show()


def eval_module(columns, df_woeval_train, df_woeval_oot, target='target', disp_summary=True, bins=10, border=[0, 100]):
    """
    描述：依据指标，进行模型的拟合与评估。输出模型、训练集分数、测试集分数、lift分数分段表、指标权重。

    参数：
    :param columns: 选取构建模型的字段。
    :param df_woeval_train: 训练集通过分箱配置表转换的分数值或WOE值。
    :param df_woeval_oot: 测试集/OOT通过分箱配置表转换的分数值或WOE值。
    :param target: 目标变量名称
    :param disp_summary: 是否展示模型Summary。
    :param bins: 分箱对比分数差异。
    :param border: 分数值的值域。
    :return:
        - model: 模型
        - df_train_score: 训练集分数
        - df_oot_score: 测试集分数
        - df_lift: lift分数分段表
        - df_param: 指标权重

    示例：
    >>> columns = ['campaign', 'duration', 'previous',]
    >>> model, df_train_score, df_oot_score, df_lift, df_param = eval_module(
    >>>     columns, df_woeval_train=df_val, df_woeval_oot=df_val, target='target',)
    """
    print(f"指标数量: {len(columns)}")

    # 训练集拟合
    df_woeval_train = df_woeval_train[columns + [target]]
    model = StatsLogit(X=df_woeval_train.drop('target', axis=1), y=df_woeval_train.target)
    metrics = RocAucKs(model.model.endog, model.predict())
    print(f"Train dataset: {df_woeval_train.shape}, KS = {metrics.get('ks'): .3f}, AUC = {metrics.get('auc'): .3f}")

    # oot data
    df_woeval_oot = df_woeval_oot[columns + [target]]
    df_oot_data = sm.add_constant(df_woeval_oot.drop('target', axis=1).astype(float))
    # oot predict
    predict_oot = model.predict(df_oot_data)
    metrics = RocAucKs(df_woeval_oot.target, predict_oot)
    print(f"OOT dataset: {df_woeval_oot.shape}, KS = {metrics.get('ks'): .3f}, AUC = {metrics.get('auc'): .3f}")

    if disp_summary: print(model.summary())

    df_param = pd.DataFrame(model.params.drop('const'), columns=['param'])
    # 百分制权重
    df_param['weight'] = df_param['param'] * 100 / df_param['param'].sum()

    # 计算模型分数
    df_train_score = model_score(df_woeval_train, df_param.param)
    df_oot_score = model_score(df_woeval_oot, df_param.param)

    # Train - OOT lift Eval
    df_lift = lift_compare(df_train_score, df_oot_score, bins=bins, border=border)
    return model, df_train_score, df_oot_score, df_lift, df_param


def model_score(
        df_woeval, df_param, weight_name='weight',
        feature_name='var_name', target_name='target',
        reset_index=True, score_border=None, decimal=2):
    """
    描述：计算模型的分数

    :param df_woeval:
    :param df_param:
    :param weight_name:
    :param feature_name:
    :param target_name:
    :param reset_index:
    :param score_border:
    :param decimal:
    :return:

    示例：
    >>> df_train_score = model_score(df_woeval_train, df_param.param)
    >>> df_oot_score = model_score(df_woeval_oot, df_param.param)
    """
    df_score = pd.DataFrame()

    if isinstance(df_param, pd.DataFrame):
        weight = np.array(df_param[weight_name].tolist())
        columns = df_param[feature_name].tolist()

    elif isinstance(df_param, pd.Series):
        weight = np.array(df_param.tolist())
        columns = df_param.index.tolist()

    weight = weight / weight.sum()
    score = df_woeval[columns].dot(weight)

    if score_border:
        a, b = score_border
        X_min, X_max = score.min(), score.max()
        df_score['score'] = NumRange(a, b, X_min, X_max, score)
    else:
        df_score['score'] = score

    if target_name is not None:
        df_score[target_name] = df_woeval[target_name]

    if reset_index:
        df_score.reset_index(drop=False, inplace=True)

    if decimal and isinstance(decimal, int):
        df_score['score'] = df_score['score'].apply(lambda x: round(x, decimal))

    return df_score

