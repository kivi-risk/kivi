# 批量分箱计算与其他补充内容

## WOE分箱批量计算

> 参数：`WOEBatch`

- `:param df:` DataFrame 原始数据集。
- `:param bins[int, dict]:` [int]分箱数量，默认为 5；[dict(var_name: bins)]依据截断点分箱。
- `:param max_bin:` 允许最大分箱数量。
- `:param min_bin:` 允许最小分箱数量。
- `:param rebin:` 是否重新分箱，默认为 `True`。
- `:param woe_type:` 分箱方法，默认为决策树分箱 `TreeBins`。
- `:param woe_columns:` 需要进行分箱的字段，默认为全部字段。
- `:param target_name:` 标签名称，默认为 `target`。
- `:param observe_order:` 保留分箱单调性，默认为 `['单调上升','单调下降']`；即对不满足条件的数据进行重分箱。
- `:param abnormal_vals:` 需要剔除异常值，如[-9099, -4404]
- `:param protect_columns:` 需要剔除分箱的字段, 如不需要进行分箱的字段['uuid', 'target']。
- `:param logger:` 日志记录器，默认为 `None`。
- `:param verbose:` 是否打印分箱日志，默认为 `False`。

> 示例: 批量分箱

```python
from kivi.woe import *
from kivi.datasets import *

df_bank = Dataset.bank_data()
df = df_bank.select_dtypes(include=['int64', 'float64']).copy()

batch = WOEBatch(df, woe_type=TreeBins, rebin=False)
df_woe = batch.fit()
```

*输出*

<img src="./img/woe/woe_batch_0.png" width="50%">

<img src="./img/woe/woe_batch_1.png" width="50%">

> 示例: 批量分箱并进行分箱的优化(` rebin=True `)

```python
batch = WOEBatch(df, woe_type=TreeBins, max_bin=5, min_bin=2, rebin=True)
df_woe = batch.fit()
```

*输出*

<img src="./img/woe/woe_batch_2.png" width="50%">

<img src="./img/woe/woe_batch_3.png" width="50%">

*可以看到，上面的过程共进行了4次分箱优化，最大分箱数为5，最小为2，分箱排序均为`单调上升、单调下降`的单调分箱。*

## WOE赋分方法

### WOE分箱与样本校验

> 由于训练集样本与其他样本的数值偏差，在进行WOE分箱赋分时，`kivi`会对以下数据内容进行校验。

1. 样本的唯一性，即`UUID`是否是唯一的。
2. `target/UUID`是否存在。
3. WOE分箱中无空箱，但样本中出现了空值。

*分别对应以下Error:*

```text
1. uuid is not unique, please check your data.
2. uuid {id_name} not in columns, please check your data.
3. target {target_name} not in columns, please check your data.
4. WOE data is not valid, please check your data.
    - [WOEScore] WOE does not contain nan bin but there are nan values in the data <age>, please check the data: age.
```

### WOE批量赋分

> 参数：`WOEScore`

- `:param df`: 原始数据
- `:param df_woe`: woe编码后的数据
- `:param id_name`: uuid
- `:param target_name`: 目标变量名称，默认为 target
- `:param dtype`: 数据类型，默认为float
- `:param batch_size`: 批量大小，默认为32
- `:param error`: 错误处理方式，默认为error
- `:param logger`: 日志记录器，默认为None
- `:param verbose`: 是否显示进度条，默认为True

> 示例

```python
import numpy as np
from kivi.woe import *
from kivi.datasets import *

df_bank = Dataset.bank_data()
df_bank['uuid'] = np.arange(0, len(df_bank))

batch = WOEBatch(df_bank, verbose=False)
df_woe = batch.woe_batch_with_rebin()

woe_score = WOEScore(df=df_bank, df_woe=df_woe, batch_size=3, verbose=True)
df_score = woe_score.batch_run()
```

*输出*

<img src="./img/woe/woe_batch_4.png" width="50%">

<img src="./img/woe/woe_batch_5.png" width="50%">

## 手动调整分箱

### 手动分箱

在自动分箱满足不了实际需求的情况时，可以考虑手动指定分箱的截断点进行手动分箱操作。一般用于数据分析阶段，反复尝试不同的分箱截断点会有什么样的影响或效果。

> 参数`ManualBinsTool`

- `:param df`: 数据集
- `:param target_name`: 目标变量名
- `:param abnormal_vals`: 异常值
- `:param logger`: 日志
- `:param verbose`: 是否打印日志

> 示例

```python
import numpy as np
from kivi.woe import *
from kivi.datasets import *

df_bank = Dataset.bank_data()
print(df_bank.shape)

batch = WOEBatch(df=df_bank, max_bin=5, min_bin=2, rebin=False)
df_woe = batch.fit()
print(df_woe.head(10))

# 手动分箱，bins为手动指定的分箱截断点
rebin_tool = ManualBinsTool(df=df_bank, verbose=True)
df_rebin_woe = rebin_tool.manual_rebin(column="age", bins=[-np.inf, 20, 22, 50, 70, np.inf])
```

*输出*

<center>
<img src="./img/woe/woe_batch_6.png" width="50%">
<h6>自动分箱结果</h6>

<img src="./img/woe/woe_batch_7.png" width="50%">
<h6>手动分箱结果</h6>
</center>

*可以看到，上面的手动分箱结果是按照手工指定的截断点(`[-np.inf, 20, 22, 50, 70, np.inf]`)进行的分箱计算。*

### 合并手动分箱结果

> `ManualBinsTool.append_rebin_woe`方法的作用是将手工分箱结果合并至全量分箱结果`df_woe`中。该过程会使用 `df_rebin` 中的分箱数据完全替换 `df_woe` 中的分箱数据。

> 参数：

- `:param df_woe`: 原始分箱
- `:param df_rebin`: 手工分箱

> 示例：`ManualBinsTool.append_rebin_woe`

```python
# 前置代码与上一小节一致
df_woe_manually = rebin_tool.append_rebin_woe(df_woe=df_woe, df_rebin=df_rebin_woe)
```

### 训练集分箱缺陷

> 在训练集上分箱时，如果某些分箱的样本量过少，可能会导致分箱结果在其他样本上的不可用。

如，若训练集中某些指标不存在空值，但在测试集中存在空值，则会导致测试集中该指标的空值无法被正确分箱，从而影响后续的评分计算。

#### 补充空箱

`ManualBinsTool.add_nan_bin`方法的作用是对训练集中未包含`Nan`箱的字段增加空箱，以及相应的分数，确保能够覆盖测试集中`Nan`的数据情况。

> 参数：

- `:param df_woe`: woe分箱结果
- `:param columns`: 需要填充的变量名，有以下两种格式可以选择
  - `List[str]`: 如` ["age", "education"] `是对这两个字段进行空箱默认值的填充，默认值参考参数`fill_score`
  - `Dict[str, int]`: 如 ` {"age": 15, "duration": 30} ` 会对 `age` 自动空箱填充为15分，`duration` 字段填充为30分
- `:param fill_score`: 填充的分值策略。默认时会按照风险排序给定风险策略，具体如下：
  - 单调上升: 95
  - 单调下降: 5
  - 上升下降: 30
  - 下降上升: 30
  - 数据不足: 30
  - 未知: 30

几种补充空箱的示例如下：

> 自动对全部字段进行补充`Nan`箱

```python
import numpy as np
from kivi.woe import *
from kivi.datasets import *

# data
df_bank = Dataset.bank_data()
df_bank['uuid'] = np.arange(0, len(df_bank))

# 批量自动分箱
batch = WOEBatch(df_bank, rebin=False, verbose=False)
df_woe = batch.fit()

# 补充Nan箱
bin_tool = ManualBinsTool(df=df_bank, verbose=True)
# method: 不指定字段，自动对全部字段进行补充Nan
df_woe = bin_tool.add_nan_bin(df_woe=df_woe)
print(df_woe[df_woe.var_name == "age"].to_markdown())
print(df_woe.shape, df_woe.shape, len(df_woe.var_name.unique()))
```

*输出*

```text
|    | var_name   |   missing_rate |   min_bin |   max_bin |   total |   bad |   bad_rate |       woe |       iv |   iv_value | order   |   score |
|---:|:-----------|---------------:|----------:|----------:|--------:|------:|-----------:|----------:|---------:|-----------:|:--------|--------:|
|  0 | age        |              0 |      -inf |        29 |     482 |    74 |   0.153527 |  0.331098 | 0.013255 |   0.153044 | 未知    |      40 |
|  1 | age        |              0 |        29 |        52 |    3289 |   332 |   0.100943 | -0.148496 | 0.015149 |   0.153044 | 未知    |      65 |
|  2 | age        |              0 |        52 |        55 |     255 |    34 |   0.133333 |  0.166497 | 0.001666 |   0.153044 | 未知    |      45 |
|  3 | age        |              0 |        55 |        58 |     250 |    13 |   0.052    | -0.864811 | 0.029661 |   0.153044 | 未知    |     100 |
|  4 | age        |              0 |        58 |       inf |     245 |    68 |   0.277551 |  1.08166  | 0.093313 |   0.153044 | 未知    |       0 |
|  5 | age        |              0 |       nan |       nan |       0 |     0 |   0        |  0        | 0        |   0.153044 | 未知    |      30 |

(31, 12) (38, 12) 7
```

*可以看到，上面的示例中，默认对7个字段进行了空箱的补充，其中`age`字段填充的分数为`30`，全部分箱表的长度由填充前31行变为填充后38行。*

> 指定字段进行补全`Nan`箱

```python
df_woe = bin_tool.add_nan_bin(df_woe=df_woe, columns=["age"])
print(df_woe[df_woe.var_name == "age"].to_markdown())
print(df_woe.shape, df_woe.shape)
```

> 指定字段并指定分数

```python
df_woe = bin_tool.add_nan_bin(df_woe=df_woe, columns={"age": 15, "duration": 30})
print(df_woe[df_woe.var_name.isin(["age", "duration"])].to_markdown())
print(df_woe.shape, df_woe.shape)
```

> 指定填充策略

```python
fill_score = {
    "单调上升": 88, "单调下降": 28,
    "上升下降": 13, "下降上升": 12,
    "数据不足": 8, "未知": 8
}

df_woe = bin_tool.add_nan_bin(df_woe=df_woe, fill_score=fill_score)
print(df_woe[df_woe.var_name.isin(["age", "duration"])].to_markdown())
print(df_woe.shape, df_woe.shape)
```

---
@2020/06/07 write
@2024/07/08 update
