# 共线性与VIF

## 共线性问题

### 方差分析

> `VIF` 检测

从统计学的角度来看共线性。可以证明参数$\theta$的协方差矩阵为

$$
Var(\hat{\theta}) = Var(\hat{\theta} - \theta) = Var[(X^TX)^{-1}X^T \varepsilon]
$$

又对任意的常数矩阵A和随机变量x有

$$
Var(Ax) = A \cdot Var(x) \cdot A^T
$$

代入上式即可得

$$
Var(\hat{\theta}) = \sigma^2(X^TX)^{-1}
$$

具体到每个参数，有：

$$
Var(\hat{\theta}_i) = \frac{\sigma^2}{(n-1)Var(x_j)} \cdot \frac{1}{1-R_i^2}
$$

其中$Ri2$是将第i个变量$x_i$作为因变量，其他$k-1$个变量作为自变量进行线性回归获得的$R^2$，且令

$$
VIF_i = \frac{1}{1-R_i^2}
$$

为方差膨胀因子(`variance inflation factor，VIF`)。当$R_i^2 \sim 1$时，即当第$i$个变量和其他变量之间存在线性关系时，`VIF`趋于无穷大。所以`VIF`的大小反应了变量的共线性程度。一般地，当`VIF`大于`5`或`10`时，认为模型存在严重的共线性问题。

### 共线性的影响

同时考虑参数显著性检验的`t`统计量：

$$
t = \frac{\hat{\theta}_i}{std(\hat{\theta}_i)} \sim t(n-k-1)
$$

当存在共线性时，参数的标准差偏大，相应的`t 统计量`会偏小，
这样容易淘汰一些不应淘汰的解释变量，使统计检验的结果失去可靠性。

另外考虑线性回归的残差

$$
\hat{\varepsilon} = y - X\hat{\theta} = M\varepsilon
$$

其中$M$是一个投影矩阵，且满足

$$
M = I - X(X^TX)^{-1}X^T
$$

易证明

$$
||\hat{\varepsilon}||^2_2 = \varepsilon^T M \varepsilon \le ||M||_F^2 \cdot ||\varepsilon||_2^2 = (n-k) ||\varepsilon||^2_2
$$

而矩阵$M$的范数与$X$的条件数毫无关系，于是可以得出共线性并不影响模型的训练精度。但是对于泛化精度，由于参数的估计已经不准确啦，所以泛化误差肯定要差些，具体差多少，很难用公式表示出来。

共线性问题对线性回归模型有如下影响：
- 参数的方差增大；
- 难以区分每个解释变量的单独影响；
- 变量的显著性检验失去意义；
- 回归模型缺乏稳定性。样本的微小扰动都可能带来参数很大的变化；
- 影响模型的泛化误差。

## 共线性测度

> 这里介绍两种共线性测度方式：扰动分析、VIF方差膨胀因子

### 扰动分析

> **扰动分析**: 对于一个方程或者系统而言，当输入有一个非常微小的扰动时，希望方程或系统的输出变化也非常微小，如果输出的变化非常大，且不能被控制，那这个系统的预测就无效了。在矩阵计算中，这叫做扰动分析。

**【扰动分析定理】** 
设非奇异方阵$A$满足方程
$$
Ax = y
$$
它的精确解为 $x^\*$，当$A$存在一个小扰动时，假设$\hat{x}$是新方程的解：
$$
(A+\delta A)\hat{x} = y
$$
可以证明$x^*$的扰动满足：
$$
\frac{||\delta x||}{||\hat{x}||} \le k(A) \frac{||\delta A||}{||A||}
$$
其中$k(A) = ||A^{-1}|| \cdot ||A||$
是非奇异方阵的条件数，且此时矩阵范数等价于矩阵最大的奇异值，
即矩阵的条件数等价于`最大奇异值/最小奇异值`。

可以看到矩阵的条件数越大，扰动就越大，即$x$的求解值会变得非常不准确。
回到上面讲的线性回归问题，容易证明最小二乘法的解满足下面的正定方程：
$$
X^TX\hat{\theta} = X^T y
$$

此时

$$
k(X^TX) = \frac{\lambda_max(X^T X)}{\lambda_max(X^T X)} = \frac{\sigma_{max}^2(X)}{\sigma_{min}^2(X)}
$$

当方程有共线性问题时，$X$的最小特征值非常小，相应的，
上述的条件数会非常大。也就是说机器学习中的共线性问题实际上就是矩阵计算中的条件数问题。

从实际应用的角度:
- 一般若`K<100`，则认为多重共线性的程度很小
- `100<=K<=1000`，则认为存在一般程度上的多重共线性
- `K>1000`，则就认为存在严重的多重共线性

- 条件数`condition number`

```python
lr.cond_num
```

相关性分析,检验变量之间的相关系数，参考: [相关系数](./descriptive_statistics/descriptive_statistics?id=相关系数示例)

### VIF-API

1. statsmodels `VIF.vif()`            statsmodels VIF
2. statsmodels `VIF.StatsTableVIF()`  statsmodels 计算全表VIF
3. statsmodels `VIF.LowVIFFeatures()` 依据VIF设定阈值，选择最小VIF特征组合
4. PySpark     `VIF.SparkVIF()`       PySpark 计算变量VIF
5. PySpark     `VIF.SparkTableVIF()`  PySpark 计算全表VIF

####  `VIF.vif`

> 参数

- `:param exog:` DataFrame。
- `:param exog_idx:` 需要计算变量`VIF`的`ID`。

```python
import pandas as pd
from kivi.Dataset import *
from kivi.FeatureAnalysis import VIF
```
```python
# 载入 测试数据
df_bank = Dataset.BankData()
df_bank = df_bank.select_dtypes(['int64', 'float64']).copy()
```

```python
VIF.vif(df_bank.values, 0)
```
```bash
>>> output Data:
>>> 5.0928601913135125
```

#### `VIF.StatsTableVIF`

依次计算全表`VIF`

> 参数

- `:param df[pandas.DataFrame]:` 全量需要计算`VIF`的特征`DataFrame`

> 示例

```python
vif_dict = VIF.StatsTableVIF(df_bank)
pd.DataFrame(vif_dict)
```

> 结果

```bash
>>> output Data:
>>>     feature  vif_value
>>> 0       age   5.092860
>>> 1   balance   1.232178
>>> 2       day   4.058272
>>> 3  duration   2.292100
>>> 4  campaign   1.832987
>>> 5     pdays   1.737051
>>> 6  previous   1.663161
>>> 7    target   1.369417
```

#### `VIF.LowVIFFeatures`

依据`VIF`设定阈值，选择最小`VIF`特征组合

> 参数

- `:param df[pandas.DataFrame]:` 特征
- `:param thresh[int]:` `VIF`阈值
- `:return [pandas.DataFrame]:` 指标名称列表，筛选明细

> 示例

```python
df_vif = VIF.LowVIFFeatures(df_bank, 3)
df_vif
```

> 结果

```bash
>>> output Data:
>>>     feature    step_1    step_2
>>> 0       age  5.092860       NaN
>>> 1   balance  1.232178  1.180269
>>> 2       day  4.058272  2.425762
>>> 3  duration  2.292100  2.040717
>>> 4  campaign  1.832987  1.738374
>>> 5     pdays  1.737051  1.704357
>>> 6  previous  1.663161  1.661306
>>> 7    target  1.369417  1.369348
```

#### `VIF.SparkVIF`

PySpark 计算变量`VIF`

#### `VIF.SparkTableVIF`

PySpark 计算全表`VIF`

----
