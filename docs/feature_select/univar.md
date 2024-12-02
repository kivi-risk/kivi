> 数据

```python
from kivi import WOE
from kivi.Dataset import *
from kivi.FeatureAnalysis import *

# 载入 测试数据
df_bank = Dataset.BankData()
df_bank = df_bank.select_dtypes(include=['int64', 'float64']).copy()
df_bank.shape
```

### 1. 批量单变量回归，用于批量评估指标性能

> 参数

- `:param df:` DataFrame 需要进行单变量分析的数据。
- `:param col_description:` 字段的中英文映射字典；{var_name: cn_name}。
- `:param target_name:` 目标变量名称。
- `:return:` DataFrame 结果。

> 示例

```python
df_res = StatsUnivariate(df_bank)
```

### 2. 使用`WOE Score`进行批量单变量回归

```python
# 1. 对 df_bank 中的变量进行分箱操作，并对不符合WOE单调性的指标进行重分箱。
df_woe, fault_cols = WOE.WOEBatchWithRebin(df_bank, drop_columns=['target'])

# 2. 将指标转换为 WOE 分数值。
df_woeval = WOE.TransToWOEVal(df_bank, df_woe, values='score', batch=3)

# 3. 使用 WOE Val 分数进行单变量回归；评估指标在WOE 分数上的效果。
df_res = StatsUnivariate(df_woeval)
```

---

