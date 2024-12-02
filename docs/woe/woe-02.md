# 样本加权分箱分析

## 加权分箱的基本思想

> 模型迭代导致的一些问题：

1. **模型迭代导致样本有偏**。在模型的迭代过程中，业务上会不断拒绝综合决策不通过的客户，导致随着信贷业务的开展后续的入模样本是有偏的（缺失了拒绝客户的信贷表现）。
2. **有偏样本导致分箱失准**。在有偏的样本上进行分箱的分析，可能会导致分箱的截断点有偏，严重时可能会导致之前有效指标的失效。

> 加权分箱的基本思想：

1. 在`KGB样本`中加入`IGB样本`，但是在具体计算分箱截断点时，分别考虑两类样本的权重。
2. 在计算分箱的`WOE`时，需要统计各个分箱的好坏客户量，这时也分别考虑两类样本对于好坏客户量的贡献。
3. 总体来说，加权分箱方法考虑了`IGB样本`一定的数据分布特性，补充在`KGB样本`上，从一定程度上降低了样本的偏离程度，复原了样本的总体情况，从而使得分箱更具鲁棒性。

*注：`KGB`指的是已知标签的样本，即放款的客群。`IGB`为未知标签的客群，即未放款的客群。*

## 加权分箱的基本做法

> 依据拒绝客户进行加权分箱，步骤如下：

- `Step 1`: 在**KGB样本**上进行自动化决策树分箱，依据分箱转换指标值为`WOE`值，并依据`WOE`值做一个`logistic`模型。
- `Step 2`: 在**IGB样本**上使用`Step 1`模型进行`PD`计算，以`PD`值为**IGB样本**的权重；复制一份**IGB样本**并以`1 - PD`为权重。
- `Step 3`: 在**KGB样本**以`1`为样本权重，并组合两个**IGB样本**与一个**KGB样本**，共同构成新的样本。
- `Stpe 4`: 在新样本上，进行样本加权决策树分类，得到分箱的截断点。
- `Step 5`: 在`Stpe 4`的分箱截断点的基础上，进行`WOE/IV`的计算。其中好客户、坏客户的计算以加权求和方式进行。

$$
\sum_{bucket} good = \sum_{bucket} weight_i \times good_i
$$

$$
\sum_{bucket} bad = \sum_{bucket} weight_i \times bad_i
$$

## 实现

### Step 1: 样本的划分

```python
import numpy as np
import pandas as pd
from kivi.woe import *
from kivi.datasets import *
from kivi.utils.operator import *

# 个人信贷违约数据集
df_bank = Dataset.bank_data()

# 样本量划分
good = (df_bank.target.count() - df_bank.target.sum())
bad = df_bank.target.sum()
n_good = int(good * 0.7)
n_bad = int(bad * 0.7)

# KGB 通过决策的样本，好客户占总量 70% 坏客户占总量的 30%
df_kgb_good = df_bank[df_bank.target == 0][: n_good]
df_kgb_bad = df_bank[df_bank.target == 1][n_bad: ]
df_kgb = df_kgb_good.append(df_kgb_bad)

# IGB 未通过决策的样本，好客户占总量 30% 坏客户占总量的 70%
df_rej_good = df_bank[df_bank.target == 0][n_good: ]
df_rej_bad = df_bank[df_bank.target == 1][: n_bad]
df_rej = df_rej_good.append(df_rej_bad)

print(f'已通过样本：{df_kgb.shape} 违约率：{df_kgb.target.mean():.3f}')
print(f'未通过样本：{df_rej.shape} 违约率：{df_rej.target.mean():.3f}')

# 选择数值型变量
columns = ['campaign', 'duration', 'previous', 'age', 'balance']
df_kgb['uuid'] = np.arange(0, len(df_kgb))
df_kgb = df_kgb[columns + ['target', 'uuid']].copy()
df_rej['uuid'] = np.arange(1e4, 1e4+len(df_rej))
df_rej = df_rej[columns + ['target', 'uuid']].copy()
```

*输出*

```text
已通过样本：(2957, 17) 违约率：0.053
未通过样本：(1564, 17) 违约率：0.233
```

### Step 2: 在`KGB`上进行分箱，并进行`KGB`模型拟合

```python
# 在`KGB`上进行分箱，并将数据转换为指标分数
batch = WOEBatch(df_kgb, max_bin=5, min_bin=2)
df_woe = batch.woe_batch_with_rebin()

woe_score = WOEScore(df=df_kgb, df_woe=df_woe, batch_size=3, verbose=False)
df_woeval = woe_score.batch_run()

# `KGB`模型拟合
model = StatsLogit(df_woeval[columns], df_woeval.target)
metrics = RocAucKs(df_woeval.target, model.predict())
print(f"KS = {metrics.get('ks'): .3f}, AUC = {metrics.get('auc'): .3f}")
```

*输出*

```text
KS =  0.629, AUC =  0.870
```

### Step 3: 样本权重计算，以及拼接样本

```python
# 在`KGB`样本上，样本权重都是 1
df_kgb['pd'] = 1

# 使用上面拟合的 `KGB` 模型对 `IGB` 样本进行 `PD` 拟合
score = WOEScore(df=df_rej, df_woe=df_woe, batch_size=3, verbose=False)
df_woeval_rej = score.batch_run()
rej_predict = model.predict(sm.add_constant(df_woeval_rej[columns]))
df_rej['pd'] = rej_predict.tolist()

# 权重为 1-PD 的 `IGB` 样本
df_rej_a = df_rej.copy()
df_rej_b = df_rej.copy()
df_rej_a.target = 1
df_rej_b.target = 0
df_rej_b.pd = 1 - df_rej_b.pd
df_rej_b.uuid = df_rej_b.uuid + 3e4

# 组合 `IGB` 和 `KGB` 成为新的有权重的样本
df_rej_new = df_rej_a.append(df_rej_b)
df_data = df_rej_new.append(df_kgb)
df_data.reset_index(drop=True, inplace=True)
```

### Step 4: 进行加权分箱

```python
# 加权分箱
batch = WOEBatch(
    df_data, max_bin=5, min_bin=2, 
    protect_columns=['uuid', 'target', 'pd'],
    dtc_weight=df_data.pd, weight=df_data.pd
)
df_woe = batch.woe_batch_with_rebin()

# 使用加权分箱，将 KGB 样本指标转换为指标分数
woe_score = WOEScore(df=df_kgb, df_woe=df_woe, batch_size=3, verbose=False)
df_woeval = woe_score.batch_run()
```

### Step 5: 模型拟合，效果评估

```python
# 新的 KGB 样本模型拟合
model = StatsLogit(df_woeval[columns], df_woeval.target)

# 模型评估
metrics = RocAucKs(df_woeval.target, model.predict())
print(f"KS = {metrics.get('ks'): .3f}, AUC = {metrics.get('auc'): .3f}")
```

*输出*

```text
KS =  0.629, AUC =  0.871
```

## 加权分箱的结果对比

> 分箱结果对比

*在 `KGB样本` 上拟合截断点，在全量样本上分箱评估对比：指标`IV`由`KGB`样本的`1.820`到全量样本`1.833`。*

<img src="./img/woe_dtc_weight_0.png">

*在 `KGB样本` 上拟合截断点，并进行权重修正，然后在全量样本上分箱评估对比：指标`IV`由权重修正的`1.803`提升到全量样本`1.839`。*

<img src="./img/woe_dtc_weight_1.png">

**可以看到，在样本上，修正后的样本`IV`低于权重修正前，但是在全量样本上，修正后`IV`会更高。**

> 模型结果对比

1. 加权修正前：KS = 0.629, AUC = 0.870
2. 加权修正后：KS = 0.629, AUC = 0.871
3. 上面的过程只是个示例，实际上上述的样本`IGB样本` 与 `KGB样本`源于同一个样本且数据量相对较少，可以看到加权修正后，模型略有提升。
4. 可以预期，在`IGB样本` 与 `KGB样本`差异更大在的大样本上，修正后的分箱截断点更接近全量样本的分箱截断点，从而使得稳定性和有效性略优于权重优化前。

> 成因分析

**如下图，在值域较大的`bucket`中，权重修正后有更高的违约率，也就一定程度上提高了指标的区分能力。**

```python
(df_woe_wt.bad_rate - df_woe_wt_origin.bad_rate).abs().plot(label='wt')
(df_woe_kgb.bad_rate - df_woe_kgb_origin.bad_rate).abs().plot(label='kgb')
plt.legend()
```

<img src="./img/woe_weight_compare.png">

> 建议的建模一般操作

1. 按照通常步骤选择指标建模。
2. 按照上述操作重新优化指标的分箱截断点。
3. 重新拟合模型参数。

*注意：在实际业务开展过程中，应保存未通过客户的各类信息，用以复原`IGB样本`。*

----

> 📚 Reference

- [1] [风控模型—群体稳定性指标(PSI)深入理解应用](https://zhuanlan.zhihu.com/p/79682292)
- [2] [评分卡模型监控（一）PSI & CSI](https://zhuanlan.zhihu.com/p/94619990)
- [3] [Scorecard-Bundle](https://github.com/Lantianzz/Scorecard-Bundle)
- [4] [从论文分析，告诉你什么叫 “卡方分箱”？](https://toutiao.io/posts/q7i3ki/preview)
- [5] [ChiMerge: Discretization of Numeric Attributes](https://www.aaai.org/Papers/AAAI/1992/AAAI92-019.pdf)
