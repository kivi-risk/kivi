# PSI

> PSI (Population Stability Index)

## 理论分析

- PSI 反映了验证样本在各分数段的分布与建模样本分布的稳定性。在建模中，我们常用来筛选特征变量、评估模型稳定性。
- 预期分布: 在建模时通常以训练样本（In the Sample, INS）作为预期分布，
- 实际分布: 验证样本通常作为实际分布; 包括样本外（Out of Sample，OOS）和跨时间样本（Out of Time，OOT）。
- 业务含义：PSI数值越小，两个分布之间的差异就越小，代表越稳定。

|PSI 范围|稳定性|建议事项|
|:----:|:----:|:----:|
|0 - 0.1|好| 没有变化或很少变化|
|0.1 - 0.25|略不稳定|有变化，继续监控后续变化|
|大于 0.25|不稳定|发生很大变化，进行特征项分析|

$$
psi = \sum^{n}_{i=1}(Actucal\\% - Expected\\%) \times ln(\frac{Actucal\\%}{Expected\\%})
$$

**虽然PSI可以用来衡量分数分布的变化，但是不能反映分数分布变化的走向（整体往高分段偏移还是往低分段偏移）**

> 相对熵散度 KL(Kullback-Leibler divergence)

- 相对熵可以衡量两个随机分布之间的"距离“。
  - 1）当两个随机分布相同时，它们的相对熵为零；当两个随机分布的差别增大时，它们的相对熵也会增大。
  - 2）注意⚠️：相对熵是一个从信息论角度量化距离的指标，与数学概念上的距离有所差异。数学上的距离需要满足：非负性、对称性、同一性、传递性等；而相对熵不满足对称性。

$$
KL(P||Q) = - \sum_{x \in X} P(X) log\frac{1}{P(X)} + \sum_{x \in X} P(x) log\frac{1}{Q(x)}\\ 
$$
$$
KL(P||Q) = \sum_{x \in X} P(X) log\frac{P(x)}{Q(X)}
$$

> KL 与 PSI

$$
psi = \sum_{i=1}^{n}(A_i - E_i) \times ln\frac{A_i}{E_i}
$$
$$
psi = \sum_{i=1}^{n}A_i \times ln\frac{A_i}{E_i} + \sum^{n}_{i=1}E_i \times ln\frac{E_i}{A_i}
$$
$$
psi = KL(A||E) + KL(E||A)
$$

## KIVI-PSI

```python
from kivi.evaluate.psi import PSI
```

> 参数

- `:param expected:` 期望数据。
- `:param bins:` 分箱数目。
- `:param bins:` 分箱数目或分箱截断点
- `:param cut:` 分箱类型 等距`cut` 或 等频`qcut`
- `:param _min`: 最小值
- `:param _max`: 最大值
- `:param abnormal_vals`: 异常值
- `:param return_columns`: 返回列名
- `:param decimal`: 保留小数位数

### 等频示例

```python
import numpy as np
import pandas as pd
from kivi.evaluate.psi import PSI

psi = PSI(
    pd.Series(np.random.randint(0, 100, size=1000)),
    pd.Series(np.random.randint(0, 100, size=1000)),
    cut_type="qcut", bin=5,
)
df_psi = psi.fit()
print(df_psi.to_markdown())
```

*输出*

```text
|              |   min_bin |   max_bin |   Expected |   Actual |   Expected_percentage |   Actual_percentage |   psi_val |      psi |
|:-------------|----------:|----------:|-----------:|---------:|----------------------:|--------------------:|----------:|---------:|
| (-inf, 19.8] |    -inf   |      19.8 |        189 |      206 |                 0.189 |               0.206 |  0.001464 | 0.007978 |
| (19.8, 39.6] |      19.8 |      39.6 |        189 |      210 |                 0.189 |               0.21  |  0.002213 | 0.007978 |
| (39.6, 59.4] |      39.6 |      59.4 |        204 |      190 |                 0.204 |               0.19  |  0.000995 | 0.007978 |
| (59.4, 79.2] |      59.4 |      79.2 |        219 |      193 |                 0.219 |               0.193 |  0.003286 | 0.007978 |
| (79.2, inf]  |      79.2 |     inf   |        199 |      201 |                 0.199 |               0.201 |  2e-05    | 0.007978 |
```

*备注：`psi_val`指的是单个分箱`psi`贡献*

### 等距示例

```python
import numpy as np
import pandas as pd
from kivi.evaluate.psi import PSI

psi = PSI(
    pd.Series(np.random.randint(0, 100, size=1000)),
    pd.Series(np.random.randint(0, 100, size=1000)),
    cut_type="cut", bins=5, _max=100, _min=0
)
df_psi = psi.fit()
print(df_psi.to_markdown())
```

*输出*

```text
|              |   min_bin |   max_bin |   Expected |   Actual |   Expected_percentage |   Actual_percentage |   psi_val |      psi |
|:-------------|----------:|----------:|-----------:|---------:|----------------------:|--------------------:|----------:|---------:|
| (-inf, 20.0] |      -inf |        20 |        223 |      199 |                 0.223 |               0.199 |  0.002733 | 0.012677 |
| (20.0, 40.0] |        20 |        40 |        218 |      199 |                 0.218 |               0.199 |  0.001733 | 0.012677 |
| (40.0, 60.0] |        40 |        60 |        180 |      219 |                 0.18  |               0.219 |  0.007648 | 0.012677 |
| (60.0, 80.0] |        60 |        80 |        197 |      192 |                 0.197 |               0.192 |  0.000129 | 0.012677 |
| (80.0, inf]  |        80 |       inf |        182 |      191 |                 0.182 |               0.191 |  0.000434 | 0.012677 |
```

*备注：在不指定最大值`_max`最小值`_min`的情况下以`Expected`期望数据进行切分。*

### 存在空值的情况

```python
import numpy as np
import pandas as pd
from kivi.evaluate.psi import PSI

psi = PSI(
    pd.Series(np.random.randint(0, 100, size=1000)),
    pd.Series(np.random.randint(0, 20, size=1000)),
    cut_type="cut", bins=5, _max=80, _min=0,
)
df_psi = psi.fit()
print(df_psi.to_markdown())
```

*输出*

```text
|              |   min_bin |   max_bin |   Expected |   Actual |   Expected_percentage |   Actual_percentage |   psi_val |     psi |
|:-------------|----------:|----------:|-----------:|---------:|----------------------:|--------------------:|----------:|--------:|
| (-inf, 16.0] |      -inf |        16 |        166 |    833.5 |                 0.166 |            0.831421 |  1.07209  | 5.11735 |
| (16.0, 32.0] |        16 |        32 |        174 |    167.5 |                 0.174 |            0.167082 |  0.000281 | 5.11735 |
| (32.0, 48.0] |        32 |        48 |        156 |      0.5 |                 0.156 |            0.000499 |  0.893432 | 5.11735 |
| (48.0, 64.0] |        48 |        64 |        181 |      0.5 |                 0.181 |            0.000499 |  1.0639   | 5.11735 |
| (64.0, inf]  |        64 |       inf |        323 |      0.5 |                 0.323 |            0.000499 |  2.08765  | 5.11735 |
```

*以上示例在实际`Actual`中仅有`[0, 20]`的值域范围，因此在实际统计中，`Actual`的分段计数时`+0.5`处理。*

### 异常值示例

```python
import numpy as np
import pandas as pd
from kivi.evaluate.psi import PSI

psi = PSI(
    pd.Series(np.random.randint(0, 100, size=1000)),
    pd.Series(np.random.randint(0, 100, size=1000)),
    cut_type="cut", bins=5, _max=100, _min=0, abnormal_vals=[7, 8]
)
df_psi = psi.fit()
print(df_psi.to_markdown())
```

*输出*

```text
|              |   min_bin |   max_bin |   Expected |   Actual |   Expected_percentage |   Actual_percentage |   psi_val |      psi |
|:-------------|----------:|----------:|-----------:|---------:|----------------------:|--------------------:|----------:|---------:|
| (-inf, 20.0] |      -inf |        20 |        206 |      176 |                 0.206 |               0.176 |  0.004722 | 0.015323 |
| (20.0, 40.0] |        20 |        40 |        179 |      189 |                 0.179 |               0.189 |  0.000544 | 0.015323 |
| (40.0, 60.0] |        40 |        60 |        216 |      221 |                 0.216 |               0.221 |  0.000114 | 0.015323 |
| (60.0, 80.0] |        60 |        80 |        204 |      187 |                 0.204 |               0.187 |  0.001479 | 0.015323 |
| (80.0, inf]  |        80 |       inf |        177 |      211 |                 0.177 |               0.211 |  0.005974 | 0.015323 |
| 0            |         7 |         7 |         10 |        6 |                 0.01  |               0.006 |  0.002043 | 0.015323 |
| 0            |         8 |         8 |          8 |       10 |                 0.008 |               0.01  |  0.000446 | 0.015323 |
```

*以上示例，假设异常值为`[7, 8]`，计算`PSI`时对这两个值进行单独计算。*

### 类别型变量

```python
import numpy as np
import pandas as pd
from kivi.evaluate.psi import PSI

cate = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
psi = PSI(
    pd.Series(np.random.choice(cate, size=1000)),
    pd.Series(np.random.choice(cate, size=1000)),
)
df_psi = psi.fit()
print(df_psi.to_markdown())
```

*输出*

```text
|    | min_bin   | max_bin   |   Expected |   Actual |   Expected_percentage |   Actual_percentage |   psi_val |      psi |
|:---|:----------|:----------|-----------:|---------:|----------------------:|--------------------:|----------:|---------:|
| A  | A         | A         |         97 |       93 |                 0.097 |               0.093 |  0.000168 | 0.033391 |
| B  | B         | B         |        102 |       85 |                 0.102 |               0.085 |  0.003099 | 0.033391 |
| C  | C         | C         |        108 |       99 |                 0.108 |               0.099 |  0.000783 | 0.033391 |
| D  | D         | D         |         82 |      108 |                 0.082 |               0.108 |  0.007161 | 0.033391 |
| E  | E         | E         |        107 |       95 |                 0.107 |               0.095 |  0.001427 | 0.033391 |
| F  | F         | F         |        113 |      103 |                 0.113 |               0.103 |  0.000927 | 0.033391 |
| G  | G         | G         |         83 |      111 |                 0.083 |               0.111 |  0.008139 | 0.033391 |
| H  | H         | H         |        119 |       95 |                 0.119 |               0.095 |  0.005406 | 0.033391 |
| I  | I         | I         |         89 |      114 |                 0.089 |               0.114 |  0.006189 | 0.033391 |
| J  | J         | J         |        100 |       97 |                 0.1   |               0.097 |  9.1e-05  | 0.033391 |
```

---

- [1] [风控模型—群体稳定性指标(PSI)深入理解应用](https://zhuanlan.zhihu.com/p/79682292)
- [2] [评分卡模型监控（一）PSI & CSI](https://zhuanlan.zhihu.com/p/94619990)
