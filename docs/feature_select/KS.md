# KS

## KS 方法理论分析

> KS 统计量的定义

- KS（Kolmogorov-Smirnov）统计量由两位苏联数学家A.N. Kolmogorov和N.V. Smirnov提出。
- 在风控中，KS常用于评估模型区分度。区分度越大，说明模型的风险排序能力（ranking ability）越强。
- KS统计量是基于经验累积分布函数（Empirical Cumulative Distribution Function，ECDF)建立的，一般定义为：

```latex
ks = max\{|cum(bad\_rate) - cum(good\_rate)|\}
```

> KS的计算过程及业务分析

- **step 1.** 对变量进行分箱（binning），可以选择等频、等距，或者自定义距离。
- **step 2.** 计算每个分箱区间的好账户数(goods)和坏账户数(bads)。
- **step 3.** 计算每个分箱区间的累计好账户数占总好账户数比率(cum_good_rate)和累计坏账户数占总坏账户数比率(cum_bad_rate)。
- **step 4.** 计算每个分箱区间累计坏账户占比与累计好账户占比差的绝对值，得到KS曲线。即：
```latex 
ks = |cum\_good\_rate - cum\_bad\_rate|
```
- **step 5.** 在这些绝对值中取最大值，得到此变量最终的KS值。

> KS 业务理解

| Bucket           | min\_bin | max\_bin | total | total\_rate | good | bad | bad\_rate | cum\_bad\_rate | cum\_good\_rate | ks     |
|:----------------:|:--------:|:--------:|:-----:|:-----------:|:----:|:---:|:---------:|:--------------:|:---------------:|:------:|
| \(\-0\.1, 0\.1\] | 0        | 0\.091   | 113   | 0\.113      | 4    | 109 | 0\.965    | 0\.219         | 0\.008          | 0\.211 |
| \(0\.1, 0\.2\]   | 0\.101   | 0\.192   | 87    | 0\.087      | 8    | 79  | 0\.908    | 0\.378         | 0\.024          | 0\.354 |
| \(0\.2, 0\.3\]   | 0\.202   | 0\.293   | 106   | 0\.106      | 20   | 86  | 0\.811    | 0\.55          | 0\.064          | 0\.486 |
| \(0\.3, 0\.4\]   | 0\.303   | 0\.394   | 90    | 0\.09       | 40   | 50  | 0\.556    | 0\.651         | 0\.143          | 0\.507 |
| `(0.4, 0.5]`     | `0.404`  | `0.495`  | `94`  | `0.094`     | `42` | `52`| `0.553`   | `0.755`        | `0.227`         | `0.528`|
| \(0\.5, 0\.6\]   | 0\.505   | 0\.596   | 109   | 0\.109      | 59   | 50  | 0\.459    | 0\.855         | 0\.345          | 0\.511 |
| \(0\.6, 0\.7\]   | 0\.606   | 0\.697   | 94    | 0\.094      | 65   | 29  | 0\.309    | 0\.914         | 0\.474          | 0\.44  |
| \(0\.7, 0\.8\]   | 0\.707   | 0\.798   | 104   | 0\.104      | 80   | 24  | 0\.231    | 0\.962         | 0\.633          | 0\.328 |
| \(0\.8, 0\.9\]   | 0\.808   | 0\.899   | 101   | 0\.101      | 88   | 13  | 0\.129    | 0\.988         | 0\.809          | 0\.179 |
| \(0\.9, 1\.1\]   | 0\.909   | 1        | 102   | 0\.102      | 96   | 6   | 0\.059    | 1              | 1               | 0      |

1. 模型分数越高，逾期率越低，代表字段是信用评分。因此，低分段的`bad rate`相对于高分段更高，
`cum_bad_rate`曲线增长速率会比`cum_good_rate`更快，`cum_bad_rate`曲线在`cum_good_rate`上方。
1. 每个分箱里的样本数基本相同，说明是等频分箱。分箱时需要考虑样本量是否满足统计意义。
1. 若我们设定策略`cutoff`为`0.5`（低于这个值的用户预测为bad，将会被拒绝），
查表可知低于`cutoff`的`cum_bad_rate`为`75.5%`，那么将拒绝约`75.5%`的坏账户。
1. 根据bad_rate变化趋势，模型的排序性很好。如果是A卡（信用评分），
那么对排序性要求就比较高，因为需要根据风险等级对用户风险定价。
1. 模型的`KS`达到`52.8%`，区分度很强。这是设定`cutoff`为`0.5`时达到的最理想状态。
实际中由于需权衡通过率与坏账率之间的关系，一般不会设置在理想值。
因此，KS统计量是好坏距离或区分度的上限。
1. 通常情况下，模型`KS`很少能达到`52%`，因此需要检验模型是否发生过拟合，或者数据信息泄漏 。

`KS`值的取值范围是`[0，1]`，一般习惯乘以`100%`。
通常来说，`KS`越大，表明正负样本区分程度越好。
`KS`的业务评价标准如下表所示。由于理解因人而异，不一定完全合理，仅供参考。

|`KS (%)`|`好坏区别能力`|
|:----:|:----:|
|0 < KS < 20|不建议采用|
|20 < KS < 40|较好|
|40 < KS < 50|良好|
|50 < KS < 60|很强|
|60 < KS < 75|非常强|
|KS > 75|能力高但疑似有误|

⚠️ 需要指出的是，KS是在放贷样本上评估的，放贷样本相对于全量申贷样本永远是有偏的。
如果风控系统处于裸奔状态（相当于不生效，随机拒绝），那么这个偏差就会很小；
反之，如果风控系统做得越好，偏差就会越大。因此，KS不仅仅只是一个数值指标，
其背后蕴藏着很多原因，值得我们结合业务去认真分析。

> KS 指标改进优化思路

1. 检验入模变量是否已经被策略使用，使用重复变量会导致区分度不高。
1. 检验训练样本与验证样本之间的客群差异是否变化明显？
1. 开发对目标场景更具针对性的新特征。比如，识别长期信用风险，就使用一些强金融属性变量；
识别欺诈风险，就使用一些短期负面变量。
1. 分群建模或分群测算。分群需要考虑稳定性和差异性。
1. `bad case`分析，提取特征。

<img src="./img/ks.png">
<center>KS 曲线</center>

- 红色曲线代表累计坏账户占比
- 绿色曲线代表累计好账户占比
- 蓝色曲线代表`KS`曲线

> 风控中选用KS指标的原因分析

**KS指标倾向于从概率角度衡量正负样本分布之间的差异。
正是因为正负样本之间的模糊性和连续性，所以KS也是一条连续曲线。
但最终为什么取一个最大值，主要原因是提取KS曲线中的一个显著特征，从而便于相互比较。**

- 风控建模标签GBIX四类
    - G = Good（好人，标记为0）
    - B = Bad（坏人，标记为1）
    - I = Indeterminate （不定，未进入表现期）
    - X = Exclusion(排斥，异常样本)

---

## KS 检验理论分析

KS检验（Kolmogorov-Smirnov Test）是一种根据样本来推断总体是否服从某种分布的方法，
因此也可以用来检验两个经验分布是否服从同一总体分布。

我们可以定义以下假设检验命题：

- 原假设`H0`：正负样本的分数分布服从同一总体分布
- 备择假设`H1`：正负样本的分数分布不服从同一总体分布
- 如果得到的`p-value`比指定的显著水平（假设为`5%`）小，那么我们就可以拒绝原假设，
认为两个分布不服从同一总体分布。

---

## ROC 曲线理论分析

在风控场景中，样本不均衡问题非常普遍，一般正负样本比都能达到1：100甚至更低。
此时，评估模型的准确率是不可靠的。因为只要全部预测为负样本，就能达到很高的准确率。
例如，如果数据集中有95个猫和5个狗，分类器会简单的将其都分为猫，此时准确率是95%。

> 混淆矩阵

<img src="./img/confusion_matrix.png">

- 真阳率（正确）

```latex
TPR=\frac{TP}{Positive}=\frac{TP}{TP+FN}
```

- 假阳率（错误）

```latex
FPR=\frac{FP}{Negative}=\frac{FP}{FP+TN}
```

> ROC曲线

```latex
ks = max(|TPR-FPR|)
```

|KS曲线|ROC曲线|
|:----:|:----:|
|cum__rate|纵轴TPR|
|cum__rate|横轴FPR|
|\|cum_bad_rate-cum_bad_rate\||TPR=FPR+ks|

---

## KS 方法

> Author: 曹春晖

> 描述: KS 相关方法Kiwi实现

> 方法:

```python
Class: FeatureSelect.KS(
    # 保存csv计算过程文件，如果需要保存的话，添加此参数
    csvName=None, 
    # 保存ks图像，如果需要保存的话，添加此参数
    imageName=None,
    # 是否显示在JupyterNotebook中
    jupyterNotebook=True,
)
```

### 连续字段 KS

```python
Function: Countinue(
    # 连续变量
    variables: Series, 
    # target
    target: Series, 
    # 分箱数目
    bins=10, 
    # 分箱方式: 等距'distance', 等频'frequency'
    binType='distance',
)
```

```python
return: (
    # 计算过程明细表
    res, 
    # ks 值
    ks
)
```

> 示例数据

```python
from numpy import random
from pandas import Series

x = random.randint(0, 100, 1000)
x = (x-x.min())/(x.max()-x.min())
y = [random.binomial(1, 1-item) for item in x]
```

> 示例 - 连续字段KS值

```python
# 引入 kivi- 模块
from kivi import LoadData
from kivi.FeatureSelect import KS

# 载入 测试数据
load_data = LoadData()
df_bank = load_data.BankData()
test_data = df_bank[['age', 'target']]

ks = KS()
res, ksValue = ks.Continue(test_data.age, test_data.target)
```

**Result**
```markdown
>>> res
| Bucket        | min_bin | max_bin | total | total_rate | good | bad | bad_rate | cum_bad_rate | cum_good_rate | ks    |
|---------------|---------|---------|-------|------------|------|-----|----------|--------------|---------------|-------|
| "(-0.1, 0.1]" | 0.0     | 0.091   | 104   | 0.104      | 3    | 101 | 0.971    | 0.213        | 0.006         | 0.207 |
| "(0.1, 0.2]"  | 0.101   | 0.192   | 110   | 0.11       | 19   | 91  | 0.827    | 0.404        | 0.042         | 0.362 |
| "(0.2, 0.3]"  | 0.202   | 0.293   | 100   | 0.1        | 26   | 74  | 0.74     | 0.56         | 0.091         | 0.469 |
| "(0.3, 0.4]"  | 0.303   | 0.394   | 100   | 0.1        | 32   | 68  | 0.68     | 0.703        | 0.152         | 0.551 |
| "(0.4, 0.5]"  | 0.404   | 0.495   | 78    | 0.078      | 40   | 38  | 0.487    | 0.783        | 0.229         | 0.555 |
| "(0.5, 0.6]"  | 0.505   | 0.596   | 95    | 0.095      | 57   | 38  | 0.4      | 0.863        | 0.337         | 0.526 |
| "(0.6, 0.7]"  | 0.606   | 0.697   | 97    | 0.097      | 72   | 25  | 0.258    | 0.916        | 0.474         | 0.442 |
| "(0.7, 0.8]"  | 0.707   | 0.798   | 102   | 0.102      | 82   | 20  | 0.196    | 0.958        | 0.63          | 0.327 |
| "(0.8, 0.9]"  | 0.808   | 0.899   | 106   | 0.106      | 92   | 14  | 0.132    | 0.987        | 0.806         | 0.182 |
| "(0.9, 1.1]"  | 0.909   | 1.0     | 108   | 0.108      | 102  | 6   | 0.056    | 1.0          | 1.0           | 0.0   |

>>> ksValue
0.5545864661654135
```

### KS 曲线图示例

```python
ks.KSPlot()
```

<img src="./img/ks.png" width="" height="">

### KS 曲线图 Echarts

```python
ks.KSEcharts().render_notebook()
```

<p><iframe src="./html/ks.html"  width="740" height="480"></iframe></p>


### 离散字段 KS

- ⚠️ 离散 PSI 不进行分箱

```python
Function: Category(
    # 连续变量
    variables: Series, 
    # target
    target: Series, 
)
```

```python
return: (
    # 计算过程明细表
    res, 
    # ks 值
    ks
)
```

> 示例 - 离散字段 KS 计算

```python
# 引入 kivi- 模块
from kivi import LoadData
from kivi.FeatureSelect import KS

# 载入 测试数据
load_data = LoadData()
df_bank = load_data.BankData()
test_data = df_bank[['job', 'target']]

ks = KS()
res, ksValue = ks.Category(test_data.job, test_data.target)
```

**Result**

```markdown
>>> res
| variables     | min_bin       | max_bin       | total | total_rate | good | bad | bad_rate | cum_bad_rate | cum_good_rate | ks    |
|---------------|---------------|---------------|-------|------------|------|-----|----------|--------------|---------------|-------|
| admin.        | admin.        | admin.        | 478   | 0.106      | 420  | 58  | 0.121    | 0.111        | 0.105         | 0.006 |
| blue-collar   | blue-collar   | blue-collar   | 946   | 0.209      | 877  | 69  | 0.073    | 0.244        | 0.324         | 0.08  |
| entrepreneur  | entrepreneur  | entrepreneur  | 168   | 0.037      | 153  | 15  | 0.089    | 0.273        | 0.362         | 0.09  |
| housemaid     | housemaid     | housemaid     | 112   | 0.025      | 98   | 14  | 0.125    | 0.299        | 0.387         | 0.088 |
| management    | management    | management    | 969   | 0.214      | 838  | 131 | 0.135    | 0.551        | 0.596         | 0.046 |
| retired       | retired       | retired       | 230   | 0.051      | 176  | 54  | 0.235    | 0.655        | 0.64          | 0.014 |
| self-employed | self-employed | self-employed | 183   | 0.04       | 163  | 20  | 0.109    | 0.693        | 0.681         | 0.012 |
| services      | services      | services      | 417   | 0.092      | 379  | 38  | 0.091    | 0.766        | 0.776         | 0.01  |
| student       | student       | student       | 84    | 0.019      | 65   | 19  | 0.226    | 0.802        | 0.792         | 0.01  |
| technician    | technician    | technician    | 768   | 0.17       | 685  | 83  | 0.108    | 0.962        | 0.964         | 0.002 |
| unemployed    | unemployed    | unemployed    | 128   | 0.028      | 115  | 13  | 0.102    | 0.987        | 0.992         | 0.006 |
| unknown       | unknown       | unknown       | 38    | 0.008      | 31   | 7   | 0.184    | 1.0          | 1.0           | 0.0   |

>>> ksValue
0.08994721689059498
```

### KS 检验

> 方法 - KS 检验

```python
Function: KSValue(
    # 连续变量
    variables: Series, 
    # target
    target: Series, 
)

return: (
    # ks 值
    ks_value, 
    # ks-test p-value
    p_value
)
```

> 示例 - KS 检验

**✅如果仅是计算`ks`值，不需要`ks`计算表，也建议使用此方法。但此方法运算后没有明细表，不可直接出图。**

```python
ks = KS()
ks_value, P_value = ks.KSValue(Series(x), Series(y))
```

**Result**

```markdown
>>> ks_value
0.5524537126017042 

>>> P_value
1.242935658359181e-66
```

### ROC曲线

> 示例 - ROC 曲线

```python
ks.ROCPlot()
```

<img src="./img/ks_roc.png">
<center>图: ROC curve</center>

### 多个样本的分布

> 方法 - 多个样本的分布

```python
Function: Distribution(
    # Des: 绘制多个样本的分布情况
    # 数据
    data: dict, 
    # 图像参数['style', 'figsize', 'dpi', 'labelfontsize', title, 'x_label', 'y_label'……]
    **kwargs)

return: (
    None
)
```

> 示例 - 多个样本的分布

```python
from numpy import random
data = {
    'class-1': random.normal(0,3,1000), 
    'class-2': random.normal(2, 3, 10000),
    'class-3': random.normal(4, 4, 10000),
    'class-3': random.normal(6, 3, 10000),
}

ks.Distribution(
    data,
)
```

<img src="./img/ks_distribution.png">

---

> 📚 Reference

[1] [风控模型—区分度评估指标(KS)深入理解应用](https://zhuanlan.zhihu.com/p/79934510)

> Editor: Chensy
