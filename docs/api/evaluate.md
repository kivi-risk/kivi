# Evaluate

> KIVI 中的模型评估

**前置代码**

```python
from kivi.woe import *
from kivi.evaluate import *
from kivi.datasets import MakeData

make_data = MakeData()
train, test = make_data.sample()

# WOE
batch = WOEBatch(train, verbose=False)
df_woe = batch.woe_batch()
woe_score = WOEScore(df=train, df_woe=df_woe, batch_size=2, verbose=False)
train = woe_score.batch_run()
woe_score = WOEScore(df=test, df_woe=df_woe, batch_size=2, verbose=False)
test = woe_score.batch_run()
samples = [train, test]

model_eval = ModelEvaluate(samples=samples, bins=10, verbose=False)
model_eval.evaluate()

df_score = model_eval.scores[0]
target = df_score.target
proba = df_score.proba
score = df_score.score
prediction = df_score.prediction
```

*以下以训练集的分数、违约概率、预测值为例*

## BinaryMetrics

**用于分析评估模型预测的违约概率、分数的效果**

> 参数

- `:param target`: 真实标签
- `:param proba`: 预测概率
- `:param prediction`: 预测标签
- `:param score`: 预测得分
- `:param kwargs`: 其他参数

> 示例

```python
binary_metrics = BinaryMetrics(target, proba, prediction, score=score)
metrics = binary_metrics.evaluate()

# 基础评估指标
metrics.show()
```

```text
ks: 0.6742
auc: 0.9088
recall: 0.8423
lift: 1.6605
precision: 0.8291
f1_score: 0.8357
```

```python
# 混淆矩阵
binary_metrics.plot_confusion_matrix()
```

<center>
<img src="img/evaluate/confusion_metrix.png" width="420px">
</center>

```python
# KS 曲线
binary_metrics.plot_ks()
```

<center>
<img src="img/evaluate/ks.png" width="420px">
</center>

```python
# PR 曲线
binary_metrics.plot_pr()
```

<center>
<img src="img/evaluate/pr.png" width="420px">
</center>

```python
# ROC 曲线
binary_metrics.plot_roc()
```

<center>
<img src="img/evaluate/roc.png" width="420px">
</center>

```python
# 分数分布
binary_metrics.plot_score()
```

<center>
<img src="img/evaluate/score_dist.png" width="420px">
</center>

## ModelEvaluate

**模型评估，适用于单样本、多样本上的评估**

> 参数

- `:param samples`: List of DataFrame
- `:param columns`: List of columns to evaluate
- `:param train_sample_idx`: Index of the training sample
- `:param id_name`: Name of the id column
- `:param target_name`: Name of the target column
- `:param score_range`: Range of the score
- `:param decimal`: Number of decimal places
- `:param threshold`: Threshold for bad predictions
- `:param bins`: Number of bins for score
- `:param border`: Border for score
- `:param logger`: Logger
- `:param verbose`: Verbose mode

**前置代码**

```python
from kivi.woe import *
from kivi.evaluate import *
from kivi.datasets import MakeData

make_data = MakeData()
train, test = make_data.sample()

# WOE
batch = WOEBatch(train, verbose=False)
df_woe = batch.woe_batch()
woe_score = WOEScore(df=train, df_woe=df_woe, batch_size=2, verbose=False)
train = woe_score.batch_run()
woe_score = WOEScore(df=test, df_woe=df_woe, batch_size=2, verbose=False)
test = woe_score.batch_run()
samples = [train, test]
```

*`samples`是训练集、测试集的数据合集。*

> 示例

```python
model_eval = ModelEvaluate(samples=samples, bins=10, verbose=True)
model_eval.evaluate()

len(model_eval.scores)
```

*日志*

```text
                           Logit Regression Results                           
==============================================================================
Dep. Variable:                 target   No. Observations:                 7000
Model:                          Logit   Df Residuals:                     6994
Method:                           MLE   Df Model:                            5
Date:                Thu, 25 Jul 2024   Pseudo R-squ.:                  0.4448
Time:                        15:49:04   Log-Likelihood:                -2693.7
converged:                       True   LL-Null:                       -4852.0
Covariance Type:            nonrobust   LLR p-value:                     0.000
==============================================================================
                 coef    std err          z      P>|z|      [0.025      0.975]
------------------------------------------------------------------------------
const          7.1315      0.200     35.604      0.000       6.739       7.524
col_0         -0.0420      0.001    -36.496      0.000      -0.044      -0.040
col_4         -0.0288      0.002    -15.242      0.000      -0.032      -0.025
col_1         -0.0411      0.002    -16.491      0.000      -0.046      -0.036
col_2         -0.0080      0.001     -6.778      0.000      -0.010      -0.006
col_3         -0.0252      0.001    -21.278      0.000      -0.028      -0.023
==============================================================================

[ModelEvaluate] Sample ID 0 Metrics: AUC = 0.91, KS = 0.67, Lift = 1.66, recall = 0.84, precision = 0.83, f1-score = 0.84

[ModelEvaluate] Sample ID 1 Metrics: AUC = 0.91, KS = 0.68, Lift = 1.66, recall = 0.84, precision = 0.83, f1-score = 0.84
```

> 多个样本的LIFT

```python
model_eval.df_lifts
```

```text
| buckets        |   ('score-0', 'total') |   ('score-0', 'bad') |   ('score-0', 'bad_rate') |   ('score-0', 'cum_bad') |   ('score-0', 'ks') |   ('score-0', 'lift') |   ('score-1', 'total') |   ('score-1', 'bad') |   ('score-1', 'bad_rate') |   ('score-1', 'cum_bad') |   ('score-1', 'ks') |   ('score-1', 'lift') |        psi |     psi_val |
|:---------------|-----------------------:|---------------------:|--------------------------:|-------------------------:|--------------------:|----------------------:|-----------------------:|---------------------:|--------------------------:|-------------------------:|--------------------:|----------------------:|-----------:|------------:|
| (-0.001, 10.0] |                     14 |                   11 |                 0.785714  |               0.00314735 |          0.00229143 |               1.57368 |                      4 |                    3 |                 0.75      |               0.00198939 |          0.00131915 |               1.49204 | 0.00487568 | 0.000145396 |
| (10.0, 20.0]   |                    213 |                  196 |                 0.920188  |               0.0592275  |          0.0535213  |               1.8264  |                    105 |                   98 |                 0.933333  |               0.0669761  |          0.0616142  |               1.84338 | 0.00487568 | 0.000669421 |
| (20.0, 30.0]   |                    765 |                  711 |                 0.929412  |               0.262661   |          0.241548   |               1.85345 |                    339 |                  316 |                 0.932153  |               0.276525   |          0.255748   |               1.85173 | 0.00487568 | 0.000122709 |
| (30.0, 40.0]   |                   1332 |                 1182 |                 0.887387  |               0.600858   |          0.53695    |               1.80981 |                    526 |                  470 |                 0.893536  |               0.588196   |          0.529885   |               1.81169 | 0.00487568 | 0.00124471  |
| (40.0, 50.0]   |                   1420 |                  940 |                 0.661972  |               0.869814   |          0.668958   |               1.62625 |                    633 |                  428 |                 0.676145  |               0.872016   |          0.676305   |               1.62791 | 0.00487568 | 0.000306234 |
| (50.0, 60.0]   |                   1118 |                  362 |                 0.323792  |               0.973391   |          0.556843   |               1.40143 |                    493 |                  153 |                 0.310345  |               0.973475   |          0.549882   |               1.39068 | 0.00487568 | 0.000125699 |
| (60.0, 70.0]   |                   1242 |                   86 |                 0.0692432 |               0.997997   |          0.251635   |               1.14449 |                    492 |                   33 |                 0.0670732 |               0.995358   |          0.264125   |               1.15203 | 0.00487568 | 0.00107402  |
| (70.0, 80.0]   |                    764 |                    4 |                 0.0052356 |               0.999142   |          0.0359462  |               1.01834 |                    354 |                    6 |                 0.0169492 |               0.999337   |          0.0348597  |               1.01765 | 0.00487568 | 0.000686518 |
| (80.0, 90.0]   |                    128 |                    3 |                 0.0234375 |               1          |          0.00114123 |               1.00057 |                     54 |                    1 |                 0.0185185 |               1          |          0          |               1       | 0.00487568 | 1.2236e-06  |
| (90.0, 100.0]  |                      4 |                    0 |                 0         |               1          |          0          |               1       |                      0 |                    0 |               nan         |               1          |          0          |               1       | 0.00487568 | 0.000499741 |
```

> SCORE 示例

```text
|    |    proba |   score |   prediction |   target | buckets      |
|---:|---------:|--------:|-------------:|---------:|:-------------|
|  0 | 0.546702 |   47.88 |            1 |        0 | (40.0, 50.0] |
|  1 | 0.335947 |   53.87 |            0 |        0 | (50.0, 60.0] |
|  2 | 0.834194 |   38.03 |            1 |        1 | (30.0, 40.0] |
|  3 | 0.730537 |   42.29 |            1 |        1 | (40.0, 50.0] |
|  4 | 0.920399 |   32.29 |            1 |        1 | (30.0, 40.0] |
```

## ScoreEvaluate 

> 参数

- `:param scores`: DataFrame 评分、PD 结果文件。
- `:param score_name`: 分数字段名称。
- `:param target_name`: 目标变量名称。
- `:param bins`: 分数分析分箱数量。
- `:param border`: 分数的最大最小边界， [min, max]。
- `:param keys`: 用于多样本中区分不同样本的lift。
- `:param logger`: 日志记录器。
- `:param verbose`: 是否打印日志。

> 示例

```python
score_eval = ScoreEvaluate(scores=model_eval.scores, bins=10, border=(0, 100))
score_eval.score_evaluate()
print(score_eval.df_lifts.to_markdown())
```

**输出**

```text
| buckets        |   ('score-0', 'total') |   ('score-0', 'bad') |   ('score-0', 'bad_rate') |   ('score-0', 'cum_bad') |   ('score-0', 'ks') |   ('score-0', 'lift') |   ('score-1', 'total') |   ('score-1', 'bad') |   ('score-1', 'bad_rate') |   ('score-1', 'cum_bad') |   ('score-1', 'ks') |   ('score-1', 'lift') |        psi |     psi_val |
|:---------------|-----------------------:|---------------------:|--------------------------:|-------------------------:|--------------------:|----------------------:|-----------------------:|---------------------:|--------------------------:|-------------------------:|--------------------:|----------------------:|-----------:|------------:|
| (-0.001, 10.0] |                     14 |                   11 |                 0.785714  |               0.00314735 |          0.00229143 |               1.57368 |                      4 |                    3 |                 0.75      |               0.00198939 |          0.00131915 |               1.49204 | 0.00487568 | 0.000145396 |
| (10.0, 20.0]   |                    213 |                  196 |                 0.920188  |               0.0592275  |          0.0535213  |               1.8264  |                    105 |                   98 |                 0.933333  |               0.0669761  |          0.0616142  |               1.84338 | 0.00487568 | 0.000669421 |
| (20.0, 30.0]   |                    765 |                  711 |                 0.929412  |               0.262661   |          0.241548   |               1.85345 |                    339 |                  316 |                 0.932153  |               0.276525   |          0.255748   |               1.85173 | 0.00487568 | 0.000122709 |
| (30.0, 40.0]   |                   1332 |                 1182 |                 0.887387  |               0.600858   |          0.53695    |               1.80981 |                    526 |                  470 |                 0.893536  |               0.588196   |          0.529885   |               1.81169 | 0.00487568 | 0.00124471  |
| (40.0, 50.0]   |                   1420 |                  940 |                 0.661972  |               0.869814   |          0.668958   |               1.62625 |                    633 |                  428 |                 0.676145  |               0.872016   |          0.676305   |               1.62791 | 0.00487568 | 0.000306234 |
| (50.0, 60.0]   |                   1118 |                  362 |                 0.323792  |               0.973391   |          0.556843   |               1.40143 |                    493 |                  153 |                 0.310345  |               0.973475   |          0.549882   |               1.39068 | 0.00487568 | 0.000125699 |
| (60.0, 70.0]   |                   1242 |                   86 |                 0.0692432 |               0.997997   |          0.251635   |               1.14449 |                    492 |                   33 |                 0.0670732 |               0.995358   |          0.264125   |               1.15203 | 0.00487568 | 0.00107402  |
| (70.0, 80.0]   |                    764 |                    4 |                 0.0052356 |               0.999142   |          0.0359462  |               1.01834 |                    354 |                    6 |                 0.0169492 |               0.999337   |          0.0348597  |               1.01765 | 0.00487568 | 0.000686518 |
| (80.0, 90.0]   |                    128 |                    3 |                 0.0234375 |               1          |          0.00114123 |               1.00057 |                     54 |                    1 |                 0.0185185 |               1          |          0          |               1       | 0.00487568 | 1.2236e-06  |
| (90.0, 100.0]  |                      4 |                    0 |                 0         |               1          |          0          |               1       |                      0 |                    0 |               nan         |               1          |          0          |               1       | 0.00487568 | 0.000499741 |
```

-----
