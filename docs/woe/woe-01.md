# WOE-API

> `WOE-IV` 简介

WOE技术是指“权重编码（Weight of Evidence）”技术，用于评估自变量（解释变量）对因变量（被解释变量）的影响。该技术常用于信用风险评估、欺诈检测等金融领域的风险评估和分类模型构建中。

- `WOE(Weight of Evidence)`常用于特征变换
- `IV(Information Value)`则用来衡量特征的预测能力

> `WOE` 应用

- 处理缺失值：当数据源没有`100%`覆盖时，那就会存在缺失值，此时可以把`null`单独作为一个分箱。这点在分数据源建模时非常有用，可以有效将覆盖率哪怕只有`20%`的数据源利用起来。
- 处理异常值：当数据中存在离群点时，可以把其通过分箱离散化处理，从而提高变量的鲁棒性（抗干扰能力）。例如，`age`若出现`200`这种异常值，可分入`age > 60`这个分箱里，排除影响。
- 业务解释性：我们习惯于线性判断变量的作用，当`x`越来越大，`y`就越来越大。但实际`x`与`y`之间经常存在着非线性关系，此时可经过`WOE`变换。

> 本文介绍`kivi`中的各类分箱API，您可以在实际场景中灵活选用。

1. 无监督分箱：等距分箱 、等频分箱 、类别型分箱、`Kmeans` 分箱 、手动指定分箱模式
2. 有监督分箱：`Pearson` 分箱 、决策树分箱、`KS-Best` 分箱 、卡方分箱

## 无监督分箱

### 等距分箱

::: kivi.woe.woe_obj.DistanceBins

### 等频分箱

::: kivi.woe.woe_obj.FrequencyBins

### 类别型分箱

> 参数：

- `:param variables:` 待分箱变量。
- `:param target:` 目标标签变量。
- `:param fill_bin:` 在各分箱中偶发性会出现 good 或 bad 为 0 的情况，默认 fill_pos 为 True ，为该分箱填充 0.5。

> 示例：

```python
bins = CategoryBins(df_bank.job, df_bank.target, bins=5)
df_woe = bins.fit(score=True, origin_border=False)
print(df_woe.to_markdown())
```

*输出*

```markdown
|    | var_name   |   missing_rate | min_bin       | max_bin       |   total |   bad |   bad_rate |       woe |       iv |   iv_value | order   |   score |
|---:|:-----------|---------------:|:--------------|:--------------|--------:|------:|-----------:|----------:|---------:|-----------:|:--------|--------:|
|  0 | job        |              0 | admin.        | admin.        |     478 |    58 |   0.121339 |  0.058488 | 0.00037  |   0.132519 | 未知    |      60 |
|  1 | job        |              0 | blue-collar   | blue-collar   |     946 |    69 |   0.072939 | -0.504101 | 0.043762 |   0.132519 | 未知    |     100 |
|  2 | job        |              0 | entrepreneur  | entrepreneur  |     168 |    15 |   0.089286 | -0.284088 | 0.002687 |   0.132519 | 未知    |      85 |
|  3 | job        |              0 | housemaid     | housemaid     |     112 |    14 |   0.125    |  0.092389 | 0.000219 |   0.132519 | 未知    |      55 |
|  4 | job        |              0 | management    | management    |     969 |   131 |   0.135191 |  0.182479 | 0.007653 |   0.132519 | 未知    |      50 |
|  5 | job        |              0 | retired       | retired       |     230 |    54 |   0.234783 |  0.8568   | 0.051105 |   0.132519 | 未知    |       0 |
|  6 | job        |              0 | self-employed | self-employed |     183 |    20 |   0.10929  | -0.059718 | 0.000141 |   0.132519 | 未知    |      65 |
|  7 | job        |              0 | services      | services      |     417 |    38 |   0.091127 | -0.26165  | 0.005707 |   0.132519 | 未知    |      80 |
|  8 | job        |              0 | student       | student       |      84 |    19 |   0.22619  |  0.808351 | 0.016344 |   0.132519 | 未知    |       5 |
|  9 | job        |              0 | technician    | technician    |     768 |    83 |   0.108073 | -0.072279 | 0.000863 |   0.132519 | 未知    |      70 |
| 10 | job        |              0 | unemployed    | unemployed    |     128 |    13 |   0.101562 | -0.141683 | 0.000538 |   0.132519 | 未知    |      75 |
| 11 | job        |              0 | unknown       | unknown       |      38 |     7 |   0.184211 |  0.550223 | 0.003128 |   0.132519 | 未知    |      25 |
```

#### `Kmeans`分箱

> 参数：

- `:param variables:` 待分箱变量。
- `:param target:` 目标标签变量。
- `:param cutoffpoint:` 分箱截断点。
- `:param fill_bin:` 在各分箱中偶发性会出现 good 或 bad 为 0 的情况，默认 fill_pos 为 True ，为该分箱填充 0.5。

> 示例：

```python
bins = KmeansBins(df_bank.age, df_bank.target, bins=5)
df_woe = bins.fit()
print(df_woe.to_markdown())
```

*输出*

```markdown
|    | var_name   |   missing_rate |   min_bin |   max_bin |   total |   bad |   bad_rate |       woe |       iv |   iv_value | order    |   score |
|---:|:-----------|---------------:|----------:|----------:|--------:|------:|-----------:|----------:|---------:|-----------:|:---------|--------:|
|  0 | age        |              0 |      -inf |        34 |    1472 |   178 |   0.120924 |  0.05459  | 0.000991 |     0.0861 | 下降上升 |      85 |
|  1 | age        |              0 |        34 |        42 |    1236 |   116 |   0.093851 | -0.229194 | 0.013145 |     0.0861 | 下降上升 |     100 |
|  2 | age        |              0 |        42 |        51 |     977 |   103 |   0.105425 | -0.100052 | 0.002081 |     0.0861 | 下降上升 |      90 |
|  3 | age        |              0 |        51 |        64 |     747 |    92 |   0.123159 |  0.075453 | 0.000968 |     0.0861 | 下降上升 |      80 |
|  4 | age        |              0 |        64 |       inf |      89 |    32 |   0.359551 |  1.46098  | 0.068915 |     0.0861 | 下降上升 |       0 |
```

### 手动分箱

> 参数：

- `:param variables:` 待分箱变量。
- `:param target:` 目标标签变量。
- `:param bins:` 分箱截断点。
- `:param fill_bin:` 在各分箱中偶发性会出现 good 或 bad 为 0 的情况，默认 fill_pos 为 True ，为该分箱填充 0.5。

> 示例：

```python
bins = ManuallyBins(
    df_bank.age, df_bank.target,
    bins=[-np.inf, 20, 22, 50, 70, np.inf],)
df_woe = bins.fit()
print(df_woe.to_markdown())
```

*输出*

```markdown
|    | var_name   |   missing_rate |   min_bin |   max_bin |   total |   bad |   bad_rate |       woe |       iv |   iv_value | order    |   score |
|---:|:-----------|---------------:|----------:|----------:|--------:|------:|-----------:|----------:|---------:|-----------:|:---------|--------:|
|  0 | age        |              0 |      -inf |        20 |       7 |     3 |   0.428571 |  1.75062  | 0.00833  |   0.088071 | 下降上升 |       5 |
|  1 | age        |              0 |        20 |        22 |      16 |     4 |   0.25     |  0.939687 | 0.004395 |   0.088071 | 下降上升 |      45 |
|  2 | age        |              0 |        22 |        50 |    3571 |   384 |   0.107533 | -0.077893 | 0.004651 |   0.088071 | 下降上升 |     100 |
|  3 | age        |              0 |        50 |        70 |     873 |   106 |   0.12142  |  0.059252 | 0.000694 |   0.088071 | 下降上升 |      95 |
|  4 | age        |              0 |        70 |       inf |      54 |    24 |   0.444444 |  1.81516  | 0.070002 |   0.088071 | 下降上升 |       0 |
```

## 有监督分箱

### Pearson 分箱

- 计算全部变量的最优分箱，依据`Pearson`相关系数合并最优分箱的优化过程。

> 参数：

- `:param variables:` 待分箱变量。
- `:param target:` 目标标签变量。
- `:param r:` 相关系数阈值。
- `:param min_bin:` 最小分箱数。
- `:param max_bin:` 最大分箱数。

> 示例：

```python
bins = PearsonBins(df_bank.age, df_bank.target, min_bin=3)
df_woe = bins.fit()
print(df_woe.to_markdown())
```

*输出*

```markdown
|    | var_name   |   missing_rate |   min_bin |   max_bin |   total |   bad |   bad_rate |       woe |       iv |   iv_value | order    |   score |
|---:|:-----------|---------------:|----------:|----------:|--------:|------:|-----------:|----------:|---------:|-----------:|:---------|--------:|
|  0 | age        |              0 |      -inf |        35 |    1652 |   197 |   0.119249 |  0.038742 | 0.000557 |   0.024693 | 下降上升 |      30 |
|  1 | age        |              0 |        35 |        45 |    1388 |   129 |   0.092939 | -0.239961 | 0.016113 |   0.024693 | 下降上升 |     100 |
|  2 | age        |              0 |        45 |       inf |    1481 |   195 |   0.131668 |  0.152007 | 0.008023 |   0.024693 | 下降上升 |       0 |
```

### 决策树分箱

> 参数：

- `:param variables:` 待分箱变量。
- `:param target:` 目标标签变量。
- `:param bins:` 分箱数量，默认为 5 。
- `:param fill_bin:` 在各分箱中偶发性会出现 good 或 bad 为 0 的情况，默认 fill_pos 为 True ，为该分箱填充 0.5。

> 示例：

```python
tree_bins = TreeBins(df_bank.age, df_bank.target, bins=5)
df_woe = tree_bins.fit()
print(df_woe.to_markdown())
```

*输出*

```markdown
|    | var_name   |   missing_rate |   min_bin |   max_bin |   total |   bad |   bad_rate |       woe |       iv |   iv_value | order   |   score |
|---:|:-----------|---------------:|----------:|----------:|--------:|------:|-----------:|----------:|---------:|-----------:|:--------|--------:|
|  0 | age        |              0 |      -inf |        29 |     482 |    74 |   0.153527 |  0.331098 | 0.013255 |   0.153044 | 未知    |      40 |
|  1 | age        |              0 |        29 |        52 |    3289 |   332 |   0.100943 | -0.148496 | 0.015149 |   0.153044 | 未知    |      65 |
|  2 | age        |              0 |        52 |        55 |     255 |    34 |   0.133333 |  0.166497 | 0.001666 |   0.153044 | 未知    |      45 |
|  3 | age        |              0 |        55 |        58 |     250 |    13 |   0.052    | -0.864811 | 0.029661 |   0.153044 | 未知    |     100 |
|  4 | age        |              0 |        58 |       inf |     245 |    68 |   0.277551 |  1.08166  | 0.093313 |   0.153044 | 未知    |       0 |
```

### `Best-KS`分箱

> 参数：

- `:param variables:` 待分箱变量。
- `:param target:` 目标标签变量。
- `:param bins:` 分箱数量。
- `:param fill_bin:` 在各分箱中偶发性会出现 good 或 bad 为 0 的情况，默认 fill_pos 为 True ，为该分箱填充 0.5。

> 示例：

```python
# 类别型分箱计算
ks = KSBins(df_bank.age, df_bank.target, bins=5, )
df_woe = ks.fit()
print(df_woe.to_markdown())
```

*输出*

```markdown
|    | var_name   |   missing_rate |   min_bin |   max_bin |   total |   bad |   bad_rate |       woe |       iv |   iv_value | order   |   score |
|---:|:-----------|---------------:|----------:|----------:|--------:|------:|-----------:|----------:|---------:|-----------:|:--------|--------:|
|  0 | age        |              0 |      -inf |        30 |     632 |    90 |   0.142405 |  0.242843 | 0.009045 |   0.148341 | 未知    |      45 |
|  1 | age        |              0 |        30 |        45 |    2408 |   236 |   0.098007 | -0.181272 | 0.016319 |   0.148341 | 未知    |      65 |
|  2 | age        |              0 |        45 |        55 |     986 |   114 |   0.115619 |  0.003709 | 3e-06    |   0.148341 | 未知    |      55 |
|  3 | age        |              0 |        55 |        58 |     250 |    13 |   0.052    | -0.864811 | 0.029661 |   0.148341 | 未知    |     100 |
|  4 | age        |              0 |        58 |       inf |     245 |    68 |   0.277551 |  1.08166  | 0.093313 |   0.148341 | 未知    |       0 |
```

### 卡方分箱

> 什么是卡方分箱

卡方分箱正是一种基于卡方检验的分箱方法，使用卡方独立性检验来实现核心分箱功能的。

> 卡方统计量

$$\chi^2 = \sum_{i=1}^{m}\sum_{j=1}^{k}\frac{(A_{ij} - E_{ij})^2}{E_{ij}}$$

- $m=2$：表示相邻的两个分箱数目
- $k$：表示目标变量的类别数，比如目标是网贷违约的好和坏，那么$k=2$。$k$也可以是多类，大于2。
- $A_{ij}$：实际频数，即第i个分箱的j类频数
- $E_{ij}$：期望频数

其中，期望频数的公式如下，可根据$P(AB)=P(A)P(B)$推导出来：

$$E_{ij} = \frac{R_i}{C_k}{N}$$

- $R_i$&$C_j$：分别是实际频数整列和整行的加和。

> **假设有以下数据，分为Bins-1，Bins-2两组。频数如下表：**

| 组别     | 标签：0 | 标签：1 | R    |
|--------|------|------|------|
| Bins-1 | 100  | 9    | 109  |
| Bins-2 | 101  | 8    | 109  |
| C      | 201  | 17   | 218  |

> 卡方分箱步骤

1. 初始化步骤
   1. 根据连续变量值大小进行排序 
   2. 构建最初的离散化，即把每一个单独的值视为一个箱体。这样做的目的就是想从每个单独的个体开始逐渐合并。
   3. 计算所有相邻分箱的卡方值：也就是说如果有1,2,3,4个分箱，那么就需要绑定相邻的两个分箱，共三组：12,23,34。然后分别计算三个组的卡方值。

2. 合并：
   1. 从计算的卡方值中找出最小的一个，并把这两个分箱合并，比如，23是卡方值最小的一个，那么就将2和3合并，本轮计算中分箱就变为了1,23,4。
   2. 低卡方值表明它们具有相似的类分布。直到满足停止条件。

3. 停止条件：
   1. 卡方停止的阈值
   2. 分箱数目的限制

*只要当所有分箱对的卡方值都大于阈值，并且分箱数目小于最大分箱数时，计算就会继续，直到不满足。*

> 参数：

- `:param variables:` 待分箱变量
- `:param target:` 目标标签变量
- `:param init_bins:` 初始化分箱数量，在此分箱数量基础上进行等频分箱，再依据卡方检验进行分箱的合并
- `:param min_bins:` 最小的分箱数量
- `:param max_bins:` 最大的分箱数量
- `:param m:` 目标变量类别数
- `:param fill_bin:` 在各分箱中偶发性会出现 good 或 bad 为 0 的情况，默认 fill_bin 为 True ，为该分箱填充 0.5。
- `:param confidence_level:` 卡方检验置信度

> 示例：

```python
bins = Chi2Bins(
   df_bank.age, df_bank.target, init_bins=20, min_bins=5, max_bins=10,)
df_woe = bins.fit()
print(df_woe.to_markdown())
```

*输出*

```markdown
|    | var_name   |   missing_rate |   min_bin |   max_bin |   total |   bad |   bad_rate |       woe |       iv |   iv_value | order   |   score |
|---:|:-----------|---------------:|----------:|----------:|--------:|------:|-----------:|----------:|---------:|-----------:|:--------|--------:|
|  0 | age        |              0 |      -inf |        29 |     482 |    74 |   0.153527 |  0.331098 | 0.013255 |   0.132842 | 未知    |      55 |
|  1 | age        |              0 |        29 |        45 |    2558 |   252 |   0.098514 | -0.175541 | 0.016293 |   0.132842 | 未知    |      85 |
|  2 | age        |              0 |        45 |        56 |    1060 |   120 |   0.113208 | -0.020089 | 9.4e-05  |   0.132842 | 未知    |      80 |
|  3 | age        |              0 |        56 |        59 |     247 |    20 |   0.080972 | -0.390918 | 0.007178 |   0.132842 | 未知    |     100 |
|  4 | age        |              0 |        59 |       inf |     174 |    55 |   0.316092 |  1.26651  | 0.096022 |   0.132842 | 未知    |       0 |
```

## 异常值分箱

> 数据中存在异常值

1. 当数据中存在异常值：`-1111`,`-9999`。
2. 当比率型指标，分子不存在，或分母不存在时需要进行分类讨论；比如资产负债率指标，
资产不存在与负债不存在可能是完全不同的状况，需要在分箱时分类讨论。

**在以上情况下，** 可以指定`abnormal_vals`参数。示例如下：

```python
bins = TreeBins(df_bank.age, df_bank.target, bins=5, abnormal_vals=[19, 31])
df_woe = bins.fit()
print(df_woe.to_markdown())
```

> 结果数据的介绍

```markdown
|    | var_name   |   missing_rate |   min_bin |   max_bin |   total |   bad |   bad_rate |       woe |       iv |   iv_value | order   |   score |
|---:|:-----------|---------------:|----------:|----------:|--------:|------:|-----------:|----------:|---------:|-----------:|:--------|--------:|
|  0 | age        |      0.0449016 |      -inf |        29 |     478 |    72 |   0.150628 |  0.308613 | 0.011325 |    0.16042 | 未知    |      60 |
|  1 | age        |      0.0449016 |        29 |        52 |    3090 |   316 |   0.102265 | -0.134004 | 0.011655 |    0.16042 | 未知    |      75 |
|  2 | age        |      0.0449016 |        52 |        55 |     255 |    34 |   0.133333 |  0.166497 | 0.001666 |    0.16042 | 未知    |      65 |
|  3 | age        |      0.0449016 |        55 |        58 |     250 |    13 |   0.052    | -0.864811 | 0.029661 |    0.16042 | 未知    |     100 |
|  4 | age        |      0.0449016 |        58 |       inf |     245 |    68 |   0.277551 |  1.08166  | 0.093313 |    0.16042 | 未知    |      35 |
|  5 | age        |      0.0449016 |        19 |        19 |       4 |     2 |   0.5      |  2.0383   | 0.006805 |    0.16042 | 未知    |       0 |
|  6 | age        |      0.0449016 |        31 |        31 |     199 |    16 |   0.080402 | -0.398598 | 0.005995 |    0.16042 | 未知    |      85 |
```

*可以看到，上面的分箱过程中将`19/31`单独列为两个分箱进行计算。任何分箱都支持指定`abnormal_vals`值的方式对异常值进行单独的统计计算。*

## 分箱分数

> Score 计算方式

*step 1:*

$$
woe_{neg} = - woe
$$

*step 2:*

$$
woe_{score} = \frac{woe_{neg} - min(woe_{neg})}{max(woe_{neg}) - min(woe_{neg})}
$$

*step 3:*

对 $woe_{score}$ 按照 `5` 进行取整。如：
1. `24.5` 取整为 `25`；
2. `25.5` 取整为 `25`；
3. `28.5` 取整为 `30`；

## 补充说明

> `.fit()` 说明

- `score=True`: 是否增加 WOE 分数，默认为 `True`。
- `order=True`: 是否增加分箱的排序判断，默认为 `True`。
- `origin_border=False`: 是否增加统计分箱中的最大值与最小值，默认为 `False`。

> 其他变量方法：

- `woe.cutoff_point`: 分箱截断点。
- `var_name`: 指标的名称。
- `missing_rate`: 指标的缺失率。
- `min_bin`: 分箱的左边界，左开右闭。
- `max_bin`: 分箱的右边界，左开右闭。
- `total`: 该箱样本总量。
- `bad`: 该箱坏样本量。
- `bad_rate`: 该箱违约率。
- `woe`: `woe` 值。
- `iv`: 该箱 `iv` 贡献。
- `iv_value`: 该变量的`IV`值。
- `order`: 变量单调性`['单调上升', '单调下降', '数据不足', '未知',]`。
- `score`: 分箱的分值，值域为`[0, 100]`分，违约越低分值越大。

> 指标选取的一般原则

1. 各分箱的样本数量应相对均衡。
2. 分箱应尽量保证单调性。
3. ...

## 分箱比较

> 无监督分箱

无监督分箱一般只取决于数据字段自身的分布，不同的分箱方式有的时候好有的时候差。

> 有监督分箱

决策树分箱与卡方分箱一般优于`Best-KS`；决策树分箱比卡方分箱效率会高一些。

----
