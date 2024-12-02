# 模型评估

## 1. 模型评估概述

> 基本评估工具 

| **中文**      | **英文**                                 |
|--------------|------------------------------------------|
| 混淆矩阵      | Confusion Matrix                       |
| 受试工作特征曲线 | Receiver Operating Charateristic Curve |
| 曲线下面积    | Area Under Curve                       |  
| 洛伦兹曲线    | Kolmogorov-Smirnov Curve               |
| 基尼系数     | Gini Coefficient                        |
| 增益图       | Gain Chart                              |
| 提升图       | Lift Chart                              |
| 标准误差      | Root Mean Squared Error                |
| 群体稳定性指标 | Population Stability Index               |
| 特征稳定性指标 |Characteristic Stability Index            | 

### 1.1 混淆矩阵

> 混淆矩阵

**混淆矩阵是ROC曲线绘制的基础，同时它也是衡量分类型模型准确度中最基本，最直观，计算最简单的方法。**

<img src="./img/confusion_matrix.png">

> 混淆矩阵二级指标

**准确率 ACC**: 分类模型所有判断正确的结果占总观测值的比重

$$
Accuracy = \frac{TP+TN}{TP+TN+FP+FN}
$$

**精确率 PPV Precision**: 在模型预测是Positive的所有结果中，模型预测对的比重

$$
Precision = PPV = \frac{TP}{TP+FP}
$$

**灵敏度 真阳率（正确） TPR Sensitivity Recall**: 在真实值为Positive的所有结果中，模型预测对的比重

$$
TPR=\frac{TP}{Positive}=\frac{TP}{TP+FN}
$$

**特异度 TNR**: 在真实值是Negative的所有结果中，模型预测对的比重

$$
Specificity = \frac{TN}{TN+FP}
$$

> 阴性预测值 NPV: 可以理解为负样本的查准率，阴性预测值被预测准确的比例
$$
NPV = \frac{TN}{FN+TN}
$$

- 假阳率（错误）

$$
FPR=\frac{FP}{Negative}=\frac{FP}{FP+TN}
$$

$$
Sensitivity = Recall = TPR = \frac{FP}{TP+FN}
$$

$$
Specificity = \frac{TN}{TN+FP}
$$

$$
PPositive = P/ALL
$$

> BEP 平衡点

查准率Precision=查全率的点Recall，
过了这个点，查全率将增加，查准率将降低。
如下图，蓝色和橘黄色的交叉点就是“平衡点”BEP。

<img src="./img/BEP.png">

> 混淆矩阵三级指标

> F1 Score - 查准率和查全率的加权调和平均数

- 当认为查准率和查全率一样重要时，权重相同时:
```latex
F1\ Score = \frac{1}{\frac{1}{Recall}+\frac{1}{Precision}} = \frac{2PR}{P+R}
```
    - 其中，`P`代表`Precision`，`R`代表`Recall`。
    - `F1-Score`指标综合了`Precision`与`Recall`的产出的结果。
    - `F1-Score`的取值范围从`0`到`1`的，`1`代表模型的输出最好，`0`代表模型的输出结果最差。
- 当查准率查全率的重要性不同时，即权重不同时:
```latex
F_\beta = \frac{(1+\beta^2)\times P \times R}{\beta^2 \times P + R}
```

假设: 
```latex
\beta^2 = \frac{Weight_R}{Weight_P},\ Weight_R + Weight_P = 1\\
\ \\
1+\beta^2=\frac{1}{Weight_P}\\
\ \\
\frac{1}{F_\beta} = \frac{1}{\frac{W_P}{P}+\frac{W_R}{R}}\\
\ \\ 
F_\beta = \frac{(1+\beta^2)\times P \times R}{\beta^2 \times P + R}\\
```

因此: 

1. β=1，查全率的权重=查准率的权重，就是F1
2. β>1，查全率的权重>查准率的权重
3. β<1，查全率的权重<查准率的权重

> 多个二分类混淆矩阵

e.g.
- 多次训练/测试，多个数据集上进行训练/测试，
- 多分类任务的两两类别组合等。

**宏F1: 设有n个混淆矩阵，计算出查全率和查准率的平均值，再计算F1即可。**
```latex
P_{macro} = \frac{1}{n}\sum_{i=1}^{n}P_{i} \\
\ \\ 
R_{macro} = \frac{1}{n}\sum_{i=1}^{n}R_{i} \\
\ \\
F1_{macro} = \frac{2\times P_{macro} \times R_{macro}}{P_{macro} + R_{macro}}
```
这种做法认为每一次的混淆矩阵（训练）是同等权重的。

**微F1 设有n个混淆矩阵，计算出混淆矩阵对应元素（TP，FP，FN，TN）的平均值，再计算查全率、查准率。**
$$
P_{micro} = \frac{\overline{TP}}{\overline{TP}+\overline{FP}} \\
$$

$$
R_{micro} = \frac{\overline{TP}}{\overline{TP}+\overline{TN}} \\
$$

$$
F1_{micro} = \frac{2\times P_{micro} \times R_{micro}}{P_{micro} + R_{micro}}
$$
                         
这种做法认为每一个样本的权重是一样的

### 1.2 ROC与AUC

**ROC曲线与AUC面积都是评判模型结果的指标，因此属于模型评估的一部分。
此外，ROC曲线与AUC面积均多用于判断分类器（Classifier）的优劣，因此适用于分类型的数据模型，
如分类树（Classification Tree）、逻辑回归（Logistic Regression）、线性判别分析（Linear Discriminant Analysis）等方法。**

> AUC的定义与解读

AUC`(Area Under Curve)`，即ROC曲线下的面积。每一条ROC曲线对应一个AUC值。`AUC`的取值在`0`与`1`之间。

|取值             |含义                                                               |
|----------------|-------------------------------------------------------------------|
|AUC = 1         |代表ROC曲线在纵轴上，预测完全准确。不管Threshold选什么，预测都是100%正确的。|
|0.5 < AUC < 1   |代表ROC曲线在45度线上方，预测优于50/50的猜测。需要选择合适的阈值后，产出模型。|
|AUC = 0.5       |代表ROC曲线在45度线上，预测等于50/50的猜测。|
|0 < AUC < 0.5   |代表ROC曲线在45度线下方，预测不如50/50的猜测。|
|AUC = 0         |代表ROC曲线在横轴上，预测完全不准确。|

### 1.3 Lift 和 Gain图

- `Lift`图衡量的是，与不利用模型相比，模型的预测能力“变好”了多少，`lift`(提升指数)越大，模型的运行效果越好。
- `Gain`图是描述整体精准度的指标。

$$
Lift = \frac{\frac{TP}{TP+FP}}{\frac{P}{P+N}}\\
$$

$$
Gain = \frac{TP}{TP+FP}
$$

## 2. Metrics API

### 2.1 LIFT

> 参数

- `:param df_score:` DataFrame 评分、PD 结果文件。
- `:param bins:` 分箱数量。
- `:param score_name:` 分数字段名称。
- `:param target_name:` 目标变量名称。

> 示例

```python
df_lif = lift(df_score, bins=20, score_name='score', target_name='target')
```

### 2.2 lift_compare

> 描述：**对比统计训练集、测试集的分段分布，计算训练集、测试集的KS、LIFT、PSI。**

> 参数

- `:param df_train:` 训练集分数。
- `:param df_oot:` 测试集分数。
- `:param columns:` 字段名称。
- `:param bins:` 分箱数量。
- `:param border:` 分数的最大最小边界， [min, max]。
- `:param score_name:` 分数字段名称。
- `:param psi_val:` 是否评估训练集和测试集的PSI。
- `:param target_name:` 目标变量名称。

> 示例

```python
df_compare = lift_compare(df_train, df_oot, bins=10, border=[0, 100], psi_val=True)
```

> 结果

- `total-train`: 分段训练集样本。
- `bad-train`: 分段训练集坏样本。
- `bad_rate-train`: 分段训练集违约率。
- `ks-train`: 分段训练集KS。
- `lift-train`: 分段训练集提升度。
- `total-oot`: 分段OOT样本。
- `bad-oot`: 分段OOT坏样本
- `bad_rate-oot`: 分段OOT违约率
- `ks-oot`: 分段OOT-KS。
- `lift-oot`: 分段OOT提升度。
- `psi_val`: 分段OOT-PSI。
- `psi`: PSI累计值。

### 2.3 绘制`ROC`图

> 描述：绘制`ROC`图，并标注`AUC`与`KS`

> 参数

- `:param y_true:` 真实值
- `:param y_pre:` 预测值
- `:param title:` 图片的标题
- `:param lw:` 线条宽度

> 示例

```python
PlotAucRocKS(df_val.target, model.predict())
```

> 结果

<center>
<img src="./img/roc.png">
</center>

### 2.4 `AUC` 和 `KS`

> 描述：输出预测值与真实值的 AUC KS

> 参数

- `:param true:` 真实值
- `:param predict:` 预测值（概率）
- `:param predict_binary:` 预测值（二分类）

> 示例

```python
RocAucKs(true, predict)
```

### 2.5 分数综合评估

> 描述：依据指标，进行模型的拟合与评估。输出模型、训练集分数、测试集分数、lift分数分段表、指标权重。

> 参数

- `:param columns:` 选取构建模型的字段。
- `:param df_woeval_train:` 训练集通过分箱配置表转换的分数值或WOE值。
- `:param df_woeval_oot:` 测试集/OOT通过分箱配置表转换的分数值或WOE值。
- `:param target:` 目标变量名称
- `:param disp_summary:` 是否展示模型Summary。
- `:param bins:` 分箱对比分数差异。
- `:param border:` 分数值的值域。
- `:return:`
    - `model`: 模型
    - `df_train_score`: 训练集分数
    - `df_oot_score`: 测试集分数
    - `df_lift`: lift分数分段表
    - `df_param`: 指标权重

> 示例

```python
from td_kivi.ModelEval import *

columns = ['campaign', 'duration', 'previous',]
model, df_train_score, df_oot_score, df_lift, df_param = eval_module(
    columns, df_woeval_train=df_val, df_woeval_oot=df_val, target='target',)

>>> output:
指标数量: 3
Train dataset: (4521, 4), KS =  0.541, AUC =  0.848
OOT dataset: (4521, 4), KS =  0.541, AUC =  0.848
                           Logit Regression Results                           
==============================================================================
Dep. Variable:                 target   No. Observations:                 4521
Model:                          Logit   Df Residuals:                     4517
Method:                           MLE   Df Model:                            3
Date:                Wed, 04 Jan 2023   Pseudo R-squ.:                  0.2488
Time:                        13:57:49   Log-Likelihood:                -1213.6
converged:                       True   LL-Null:                       -1615.5
Covariance Type:            nonrobust   LLR p-value:                6.485e-174
==============================================================================
                 coef    std err          z      P>|z|      [0.025      0.975]
------------------------------------------------------------------------------
const          1.3145      0.146      8.976      0.000       1.027       1.601
campaign      -0.0070      0.003     -2.531      0.011      -0.012      -0.002
duration      -0.0673      0.003    -21.413      0.000      -0.073      -0.061
previous      -0.0139      0.001    -10.715      0.000      -0.016      -0.011
==============================================================================
```

> 指标权重

|          |       param |   weight |
|:---------|------------:|---------:|
| campaign | -0.00696632 |  7.90517 |
| duration | -0.0673024  | 76.3728  |
| previous | -0.0138548  | 15.722   |

> 训练集、测试集分数示例

|    |   uuid |   score |   target |
|---:|-------:|--------:|---------:|
|  0 |      0 | 53.9084 |        0 |
|  1 |      1 | 22.9118 |        0 |
|  2 |      2 | 43.6891 |        0 |
|  3 |      3 | 55.4895 |        0 |
|  4 |      4 | 38.6339 |        0 |

> lift 示例

| buckets        |   total-train |   bad-train |   bad_rate-train |   ks-train |   lift-train |   total-oot |   bad-oot |   bad_rate-oot |    ks-oot |   lift-oot |   psi_val |   psi |
|:---------------|--------------:|------------:|-----------------:|-----------:|-------------:|------------:|----------:|---------------:|----------:|-----------:|----------:|------:|
| (-0.001, 10.0] |            63 |          35 |        0.555556  |  0.0601785 |      4.82086 |          63 |        35 |      0.555556  | 0.0601785 |    4.82086 |         0 |     0 |
| (10.0, 20.0]   |           321 |         147 |        0.457944  |  0.298828  |      4.11279 |         321 |       147 |      0.457944  | 0.298828  |    4.11279 |         0 |     0 |
| (20.0, 30.0]   |           294 |         114 |        0.387755  |  0.472638  |      3.78843 |         294 |       114 |      0.387755  | 0.472638  |    3.78843 |         0 |     0 |
| (30.0, 40.0]   |           965 |         133 |        0.137824  |  0.519917  |      2.26577 |         965 |       133 |      0.137824  | 0.519917  |    2.26577 |         0 |     0 |
| (40.0, 50.0]   |           649 |          49 |        0.0755008 |  0.463966  |      1.80971 |         649 |        49 |      0.0755008 | 0.463966  |    1.80971 |         0 |     0 |
| (50.0, 60.0]   |          1462 |          42 |        0.0287278 |  0.189581  |      1.202   |        1462 |        42 |      0.0287278 | 0.189581  |    1.202   |         0 |     0 |
| (60.0, 70.0]   |            74 |           0 |        0         |  0.171081  |      1.17877 |          74 |         0 |      0         | 0.171081  |    1.17877 |         0 |     0 |
| (70.0, 80.0]   |            49 |           0 |        0         |  0.158831  |      1.16387 |          49 |         0 |      0         | 0.158831  |    1.16387 |         0 |     0 |
| (80.0, 90.0]   |            60 |           1 |        0.0166667 |  0.146     |      1.14834 |          60 |         1 |      0.0166667 | 0.146     |    1.14834 |         0 |     0 |
| (90.0, 100.0]  |           584 |           0 |        0         |  0         |      1       |         584 |         0 |      0         | 0         |    1       |         0 |     0 |

### 2.6 分数计算

> 描述：依据回归系数计算模型分数

> 参数：None

> 示例

```python
df_train_score = model_score(df_val, df_param.param)
df_oot_score = model_score(df_val, df_param.param)
```

> 训练集、测试集分数示例

|    |   uuid |   score |   target |
|---:|-------:|--------:|---------:|
|  0 |      0 | 53.9084 |        0 |
|  1 |      1 | 22.9118 |        0 |
|  2 |      2 | 43.6891 |        0 |
|  3 |      3 | 55.4895 |        0 |
|  4 |      4 | 38.6339 |        0 |

----

> 📚 Reference

[1] [分类模型评判指标](https://blog.csdn.net/Orange_Spotty_Cat/article/details/82425113)

