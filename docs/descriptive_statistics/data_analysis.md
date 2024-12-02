

> 在数据分析过程中的一些需要注意的点。

## 1. PySpark中的列操作

```python
import pyspark.sql.functions as F
```

`F.col()`是一个创建 PySpark DataFrame `Column` 对象的方式。通过`F.col()`可以轻易完成诸多数据列的运算操作或逻辑操作。

### 1.1 两列相加

```python
F.col('I10101001') + F.col('I10101001')
```

```bash
output:
>>> Column<b'(I10101001 + I10101001)'>
```

### 1.2 多列相加

```python
columns = ['I10101001', 'I10101002', 'I10101003', 'I10101004',]
sum_col = sum([F.col(col) for col in columns])
sum_col
```

```bash
output:
>>> Column<b'((((I10101001 + 0) + I10101002) + I10101003) + I10101004)'>
```

### 1.3 多种混合运算

如，`E = A + B - C * D / E`

```python
logic_info = {
    'A': {'index_id': 'I10101001',},
    'B': {'index_id': 'I10101002',},
    'C': {'index_id': 'I10101003',},
    'D': {'index_id': 'I10101004',},
    'E': {'index_id': 'I10101005',},
}

operate = '(A + B) - ((C * D) / E)'

for name, info in logic_info.items():
    info_spare = f"F.col('{info.get('index_id')}')"
    operate = operate.replace(name, info_spare)

# 解析规则运算至 Column 对象
logic_spare = eval(operate)

logic_spare
```

```bash
output:
>>> Column<b'((I10101001 + I10101002) - ((I10101003 * I10101004) / I10101005))'>
```

### 1.4 多种混合逻辑运算
 
假设我们需要输出以下条件下的规则。

`condition = ((A | B) & (C | D)) | F`

```python
logic_info = {
    'A': {
        'index_id': 'I10101001',
        'thres': '1',
        'compare': '>',},
    'B': {
        'index_id': 'I10101002',
        'thres': '2',
        'compare': '>',},
    'C': {
        'index_id': 'I10101003',
        'thres': '3',
        'compare': '>',},
    'D': {
        'index_id': 'I10101004',
        'thres': '4',
        'compare': '>',},
    'E': {
        'index_id': 'I10101005',
        'thres': '5',
        'compare': '>',},
}

logic = '((A | B) & (C | D)) | E'

for name, info in logic_info.items():
    info_spare = f"(F.col('{info.get('index_id')}') {info.get('compare')} {info.get('thres')})"
    logic = logic.replace(name, info_spare)

# 解析规则运算至 Column 对象
logic_spare = eval(logic)

# 配合 case when 生成逻辑结果，命中逻辑为 1 未命中为 0
F.when(logic_spare, 1).otherwise(0)
```

```bash
output: 
>>> Column<b'CASE WHEN ((((I10101001 > 1) OR (I10101002 > 2)) AND ((I10101003 > 3) OR (I10101004 > 4))) OR (I10101005 > 5)) THEN 1 ELSE 0 END'>
```

### 1.5 自定义运算符

> 业务相关考虑，参考：[现实数据提取中的空值成因](/descriptive_statistics/data_analysis?id=_35-现实数据提取中的空值成因)

#### 1.5.1 除法运算符

> 说明，用于 spark 中做除法，并区分分子分母状态，计算逻辑如下：

|分母\分子	|   null|	    0	|   正值或负值|
|-----------|-------|-----------|-------|
|null	|  -4404	|   -4404	|-9999|
|0	    |  -4404	|   -4404|	-9999|
|正值或负值|  -1111	|    0	  |  正常计算|

> 方法一：`operator_div`，该函数以`case-when`的方式返回结果。

```python
data = [(None, 1), (1, 1), (None, None), (0, 0), (0, 1), (0, None), (1, None), (1, 0)]
df = spark.createDataFrame(data, schema=['num', 'den'])
df = df.withColumn('div', operator_div('num', 'den'))
df.show()
```

```bash
>>> output:
    +----+----+-------+
    | num| den|    div|
    +----+----+-------+
    |null|   1|-1111.0|
    |   1|   1|    1.0|
    |null|null|-4404.0|
    |   0|   0|-4404.0|
    |   0|   1|    0.0|
    |   0|null|-4404.0|
    |   1|null|-9999.0|
    |   1|   0|-9999.0|
    +----+----+-------+
```


> 方法二：`udf_operator_div`，该函数以`udf`自定义运算，返回运算结果。

```python
data = [(None, 1), (1, 1), (None, None), (0, 0), (0, 1), (0, None), (1, None), (1, 0)]
df = spark.createDataFrame(data, schema=['num', 'den'])
df = df.withColumn('div', udf_operator_div(F.col('num'), F.col('den')))
df.show()
```

```bash
>>> output:
    +----+----+-------+
    | num| den|    div|
    +----+----+-------+
    |null|   1|-1111.0|
    |   1|   1|    1.0|
    |null|null|-4404.0|
    |   0|   0|-4404.0|
    |   0|   1|    0.0|
    |   0|null|-4404.0|
    |   1|null|-9999.0|
    |   1|   0|-9999.0|
    +----+----+-------+
```

*注：不同之处，`udf`方式需要以`F.col`对象的形式指定分子分母，`case-when`方式需要指定列名。*

### 1.6 其他列运算操作

**参考：[Functions 文档](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/functions.html?highlight=functions)**

这里介绍一下基本的`functions`类别和基本用途：

1. `Normal Functions`：普通的列操作函数，如：列的选取，空值操作，取小数位数等。
2. `Math Functions`：数学计算操作函数，如：`log, sin, abs`等。
3. `Datetime Functions`: 时间操作函数，如：转换时间格式，取一个月的最后一天，日期加减等。
4. `Collection Functions`: 对多个字段进行组合，如：将多个字段用`list, set, array`组合为一个字段等。
5. `Partition Transformation Functions`: 提取年月日小时等。
6. `Aggregate Functions`: 聚合操作函数，如：分组求平均，求和，最大，方差等。
7. `Window Functions`: 窗口操作函数，如：窗口上计算排名，分位数等。
8. `Sort Functions`: 排序操作函数。
9. `String Functions`: 字符串操作函数，如，正则表达式，截取字符串等。
10. `UDF`: 自定义函数。
11. `Misc Functions`: 加密操作函数，如，`MD5/sha1/sha2/hash`加密等。

## 2. 分布分析

### 2.1 PySpark 下进行分位数计算 `quantile`

> 说明：计算字段的分位数

> 参数

- `:param cols[str]`: 字段名称。
- `:param percent[float]`: 分位点。

> 示例

```python
from ywcxUtils.Buckets import quantile
# OR 
from kivi.Buckets import quantile

# 示例一：计算字段 nsr 0, 0.25, 0.50 的分位数
stats = [quantile('nsr', i).alias(f'{i}') for i in [0, 0.25, 0.50, 0.75, 1]]
df.agg(*stats).show()

# 示例二：计算按月份聚合的字段分位数
df.groupby('load_date').agg(
   quantile('nsr', 0.5),          # nsr 50% 分位数 
   quantile('nsr', 0.6),          # nsr 60% 分位数 
   quantile('zzc', 0.5),          # zzc 50% 分位数 
   quantile('ygr', 0.5),          # ygr 50% 分位数 
)
```

### 2.2 PySpark 下的分段统计 `Bucketizer`

**NaN 单独分一箱**

```python
from pyspark.ml.feature import Bucketizer

bucketizer = Bucketizer(
    inputCol='values1',
    outputCol='buckets',
    splits=[-float("inf"), 0.5, 1.4, float("inf")],
    handleInvalid='keep',
)

bucketed = bucketizer.transform(df)
bucketed.show()
```
```bash
>>> output Data:
>>>
+-------+-------+-------+
|values1|values2|buckets|
+-------+-------+-------+
|    0.1|    0.0|    0.0|
|    0.4|    1.0|    0.0|
|    1.2|    1.3|    1.0|
|    1.4|    1.3|    2.0|
|    1.5|    NaN|    2.0|
|    NaN|    1.0|    3.0|
|    NaN|    0.0|    3.0|
+-------+-------+-------+
```

**NaN 剔除/跳过**

```python
bucketizer = Bucketizer(
    inputCol='values1',
    outputCol='buckets',
    splits=[-float("inf"), 0.4, 1.4, float("inf")],
    handleInvalid='skip',
)

bucketed = bucketizer.transform(df)
bucketed.show()
```
```bash
>>> output Data:
>>>
+-------+-------+-------+
|values1|values2|buckets|
+-------+-------+-------+
|    0.1|    0.0|    0.0|
|    0.4|    1.0|    1.0|
|    1.2|    1.3|    1.0|
|    1.4|    1.3|    2.0|
|    1.5|    NaN|    2.0|
+-------+-------+-------+
```

*再对buckets列进行统计分析，即可得到各个分段的统计量。*

### 2.3 PySpark 下进行排名计算

```python
# 行业、地区排名窗口
wind_zone = Window.partitionBy('load_date', 'zone').orderBy(F.desc(feature_name))     # 地区排名窗口
wind_indu = Window.partitionBy('load_date', 'industry').orderBy(F.desc(feature_name)) # 行业排名窗口

# 行业、地区排名字段
df = df.withColumn('rank_zone', F.percent_rank().over(wind_zone))
df = df.withColumn('rank_indu', F.percent_rank().over(wind_indu))
``` 

#### 2.2 其他常用的分布统计量

> Spark下的分布统计量

```python
df_data.groupBy('load_date').agg(
    F.avg('index_name'),             # 均值
    F.max('index_name'),             # 最大
    F.min('index_name'),             # 最小
    F.kurtosis('index_name'),        # 峰度
    F.skewness('index_name'),        # 偏度
    F.stddev('index_name'),          # 标准差 
    F.stddev_samp('index_name'),     # 样本标准差
    F.stddev_pop('index_name'),      # 总体标准差
    F.variance('index_name'),        # 方差
    F.var_samp('index_name'),        # 样本方差
    F.var_pop('index_name'),         # 总体方差
)
```

> Python下的分布统计量，包含`pandas.DataFrame/pandas.Series/numpy.array`

1. `mean()` 均值
2. `median()` 中位数
3. `min()` 最小值
4. `max()` 最大值
5. `std()` 标准差
6. `var()` 方差
7. `skew()` 偏度
8. `kurt()` 峰度
9. `quantile()` 分位数
10. `cov()` 协方差
11. `corr()` 相关系数
12. `mode` 众数

## 3. 空值分析

**在实际数据的分析过程中，一定要注意空值的定义与运算。**不同的数据类型下，不同的空值定义方式，不同的空值运算方式都会导致关于空值的计算结果千差万别。

- `nan/NaN/Nan`: 非数字（not a number）。
- `null/Null/NULL`: 空。

### 3.1 Spark Null 与 np.nan 与 None

> `nan`与`null`是完全不同的概念。Spark 在处理`Float` 或 `Double`时，对非数字 (NaN) 进行了特殊处理。具体来说：

1. `NaN = NaN` `return True`。
1. 在聚合中，所有 `NaN` 值都分组在一起。
1. `NaN` 在连接键中被视为正常值；在进行比较时，`NaN > 8 return True`。
1. `NaN` 值在升序时排在最后，大于任何其他数值。
1. 与 `Python NaN` 相比，`Spark NaN`排序为最大且 `Spark` 认为 `NaN` 相等。

> `Spark` 中的 `Null` 即为 `Python` 中的 `None`。

1. `F.isnan`: 是一个非数值。
2. `F.isnull`: 是一个Null。

### 3.2 关于 Null 的运算

> **Null的比较运算符**

|Left Operand|Right Operand|>|	>=|	=|	<|	<=|	<=>|
|----|---------|----|-------|-------|-------|-------|-------|
|NULL|Any value|NULL|	NULL|	NULL|	NULL|	NULL|	False|
|Any value|NULL|NULL|	NULL|	NULL|	NULL|	NULL|	False|
|NULL|NULL|NULL|	NULL|	NULL|	NULL|	NULL|	True|

`Spark` 提供了一个空安全相等运算符 `<=>`，一边为 `Null` 时返回 `False`，两边为 `Null` 时返回 `True`。

> **Null的逻辑运算符**

|Left Operand|	Right Operand|	OR|	AND|
|----|------|-----|----|
|True|	NULL|	True|	NULL|
|False|	NULL|	NULL|	False|
|NULL|	True|	True|	NULL|
|NULL|	False|	NULL|	NULL|
|NULL|	NULL|	NULL|	NULL|

> **Null 的聚合运算操作**

聚合函数通过处理一组输入行来计算单个结果。以下是聚合函数如何处理 `NULL` 值的规则。

所有聚合函数都会忽略 `NULL` 值，唯一例外是 `COUNT(*)` 函数。

当所有输入值为 `NULL` 或输入数据集为空时，某些聚合函数会返回 `NULL`。
这些函数是：

- MAX
- MIN
- SUM
- AVG
- EVERY
- ANY
- SOME

### 3.3 WHERE、HAVING 和 JOIN 子句中的条件表达式。

`WHERE`,`HAVING`运算符根据指定的条件过滤行。
`JOIN`运算符用于根据连接条件组合两个表中的行。

对于三个运算符，条件表达式都是布尔表达式并且可以返回 True 的记录, `False` 或 `Unknown (NULL)`的记录不返回。

### 3.4 空值的聚合、排序、集合

1. 聚合（`GroupBy`）：NULL为一个分组。
1. 排序（`Order`）：默认NULL排在最前面。
1. 聚合（`UNION、INTERSECT、EXCEPT`）：Null值以安全比较的方式决定是否相等。

### 3.5 现实数据提取中的空值成因

> **业务指标计算阶段：**

1. 在实际业务指标计算的过程中，未找到某些企业的业务场景，在指标长表中体现为`无该企业的任何信息`，但转换为样本指标宽表后，该企业的该指标为`Null`。
    - 如：在“企业纳税”方案中，需要在交易流水中提取纳税相关的交易，然后聚合成企业的纳税指标，但是`若企业无符合该方案的记录，则映射到样本宽表时，该企业的纳税相关指标为Null`。
    - `空值`与`0值`，一般是在业务流水提取过程中找到了某主体的相关交易，但无某具体聚合分类时`赋值为0值`，或经过计算该指标确实为0值。比如：
        - 企业有符合纳税方案的流水记录，但无符合纳税聚合的记录则赋值为0值；
        - 企业有未结清贷款，但是无未结清狭义贷款，则未结清狭义贷款为0；
        - 企业每天都有流水金额，但是每天流入流出正好相等，则企业日均活期存款为0值；
        - 企业有非银交易相关流水，但是无符合“小贷、保理”等具体非银交易的记录，则“小贷、保理”等指标值为0值。
        - 最后，需要特别注意的是，在某些方案中要求了聚合指标时统计值大于0，即聚合0值在库中无记录，宽表形态下为Null值；司法、止付、风险账户往来相关方案就是这种情况，没有记录0值，空值即为0值。

2. 存在多家机构报送同样一个字段时，不同机构字段值出入过大，我们无法相信其中任何一家时，对该主体的该指标赋值为`Null`。这类字段主要是主体的基本信息，如：员工人数、总资产、年收入等。

3. 关联指标时出现空值，有如下几种情况：
    - 主体无关联方时，关联指标为`Null`。
    - 主体有关联方但关联方该指标值为`Null`。

> **指标衍生阶段：**

1. 指标的衍生一般指，在业务指标的基础之上计算同比、环比、交叉比率、行业排名等。
2. 数值相除，**在实际的业务分析中，分母为Null，与分子为Null可能体现不同的业务含义。**在计算两个数相除时，分以下几种情况考虑：
    - 分子为`Null`，分母为`Null`时，指标值为应为`Null`，系统记录为`-4404`；在计算企业的资产负债率时，此种情况一般认为`企业既无存款也无贷款`。
    - 分子为`Null`，分母不为`Null`时，指标值为应为`Null`，系统记录为`-1111`；在计算企业的资产负债率时，此种情况一般认为`企业既有存款无贷款`。
    - 分子不为`Null`，分母为`Null`时，指标值为应为`Null`，系统记录为`-1111`；在计算企业的资产负债率时，此种情况一般认为`企业既无存款但有贷款`。
    - 分母为0时，指标值为应为`Null`，系统记录为`-1111`。在计算企业的资产负债率时，此种情况一般认为`企业无存款`。

**在企业资产负债率的业务分析中，在其他条件相同的情况下，一般认为客户资质有如这样的排列（`无存款有负债 < 有存款有负债 < 有存款无负债`）；在数据分析与建模中应当分布考虑以上种种情况对于风险的影响。**
    
*注：以上情况讨论假设资产负债率计算如下*
$$
资产负债 = \frac{负债}{存款}
$$

3. 数值排名（百分位）：
    - 一般指数值从大到小排列，数值大的百分位大。
    - `Null/Nan`不参与百分位排列，这里`Nan`值应指业务上不参与百分位排名，在实际计算上应注意排除该类型的值再进行排名计算，赋值`Null`。

> **特别注意更复杂的一些空值情况：**

1. 关联方的资产负债率指标为`Null`，可能为以下情况：
    - 主体无关联人。
    - 主体有关联人，有贷款无存款。
    - 主体有关联人，无贷款无存款。
    - 主体有关联人，无贷款无存款。
    
2. 关联方未结清非抵质押类的贷款指标为`Null`：
    - 主体无关联人。
    - 主体有关联人，关联人历史无信贷记录时值为`Null`;
    - 主体有关联人，关联人历史有信贷记录，但无非抵质押贷款，指标值为`0`。

### 3.6 空值分析总结

**1. 空值的分析，是指标建设处理最精细的一个环节，处理的好可以大大增强指标的风险指示效果。**

**2. 在技术计算细节上理清各类空值的算法是及其重要的，重点要区分`Null`与`Nan`的区别，以及在`Spark集群`与`单机Python`环境下计算的各种区别，计算错了就麻烦了。**

**3. 在业务分析上分别明晰空值的特征工程操作，可以大大提高模型的效果，是值得花费功夫处理清楚的一块重要工作内容。**

**4. 以上空值的分类讨论应该概况了工作中98%以上的场景；其他极少数的场景还应该具体问题具体分析。**

## 4. 表转置操作

### 4.1 `pivot` 长表转宽表

> 说明：**长表转宽表直接可以使用：`pivot`**

1. 一般该操作用于构建样本宽表，进行统计分析，模型分析使用。
2. 该方法可以构建列联表，用于数据分析。

> 参数

- `param: groupBy`: 聚合主键信息。
- `param: pivot`: 将哪列转换为表值。
- `param: agg`: 聚合方式。
  - 在长表转宽表时一般为`F.first`，即仅取第一个值就可以了（实际上也只有一个值）；
  - 在列联表转换中可以是其他聚合方式，如：`F.mean/F.max/F.min`。

> 示例

```python
df_wide = df_long.groupby('uuid', 'load_date').pivot("index_id").agg(
    F.first("index_val"),)
```

### 4.2 `unpivot` 宽表转长表

> 说明：将指标宽表转换为指标长表，

1. 一般用于在不修改表结构时进行指标的提取。
2. 也可以用于数据分析的维度聚合，长表可以更方便的聚合数据的各类维度。

> 参数

- `:param df_wide[PySpark DataFrame]:` 宽表。
- `:param columns[List]:` 转换指标名称List。
- `:param val_type[PySpark.sql.types]:` 数据类型，如：`StringType()`, `FloatType()`。
- `:param index_name[Str, List]:` 基础信息，一般为`uuid`或`["uuid", "load_date"]`。
- `:param feature_name:` 指标名称列。
- `:param feature_value:` 指标值列。

> 示例

```python
from ywcxUtils import *
# OR
from kivi import *

df_long = unpivot(
    df_wide, columns, val_type=None, index_name='uuid', 
    feature_name='name', feature_value='value')
```

### 4.3 `pandas` 中的转置

1. long to wide: `pd.pivot`
1. long to wide: `pd.pivot_table`
1. wide to long: `pd.wide_to_long`

## 5. 样本空间

### 5.1 `贷前`样本空间的回溯

> 说明：用于贷前样本空间的回溯构建。

> 参数

- `:param data_date`: 数据周期，依据该日期进行样本指标的回溯。
- `:param sample_date`: 样本周期 `[观察点, 表现期结束时点]`。
- `:param sxje`: 筛选样本的授信金额；默认为跨机构授信金额 1 千万。
- `:param dbfs`: 担保类型，默认不限制担保类型，如`['信用', '保证]`。
- `:param table_name`: 保存样本空间表表名。
- `:param load_dates`: 回溯信贷合同时间周期，如`['20190131', end_date]`。
- `:param update_date`: 最新指标数据日期。
- `:param schema`: 样本表的表结构。
- `:param db_name`: 样本库名。
- `:param disp`: 是否展示必要的关键节点。
- `:param spark`: spark session。

> 示例-样本表表结构

```python
# 默认模式
schema = StructType([
   StructField('uuid', StringType(), True),        # uuid
   StructField('label', StringType(), True),       # label: 观察时点的违约状况，一般回溯过去一年的未结清贷款。0-正常；1-关注；2-不良；null-未知。
   StructField('target', IntegerType(), True),     # target: 表现期结束时点的违约状况。0-正常；1-违约。
   StructField('obs_date', IntegerType(), True),   # obs_date: 观察时点，以该时间进行指标数据的索引。
   StructField('load_date', StringType(), True),   # load_date: 落库时最新指标的日期；这是分区字段，用以在未来时回溯该数据日期下的样本结果，模型结果。
])
```

```python
# 补充模式
schema = StructType([
   StructField('uuid', StringType(), True),                 # uuid
   StructField('label', StringType(), True),                # label: 观察时点的违约状况，一般回溯过去一年的未结清贷款。0-正常；1-关注；2-不良；null-未知。
   StructField('target', IntegerType(), True),              # target: 表现期结束时点的违约状况。0-正常；1-违约。
   StructField('je_max', FloatType(), True),                # je_max: 最大合同金额。
   StructField('je_min', FloatType(), True),                # je_min: 最小合同金额。
   StructField('je_avg', FloatType(), True),                # je_avg: 平均合同金额。
   StructField('zydbfs', ArryType(StringType()), True),     # zydbfs: 主要担保方式。
   StructField('obs_date', IntegerType(), True),            # obs_date: 观察时点，以该时间进行指标数据的索引。
   StructField('load_date', StringType(), True),            # load_date: 落库时最新指标的日期；这是分区字段，用以在未来时回溯该数据日期下的样本结果，模型结果。
])
```

> 示例-跑数函数

```python
# 全量 300 万授信样本
SampleSpeaceInfrontCredit(
    data_date, sample_date, sxje=3e6, dbfs=None, 
   table_name='znfk_bj_sample_zj_pd_a_v2', shcema=schema,
    load_dates=['20190131', end_date], 
   update_date=end_date, spark=spark, disp=True)
```

### 5.2 `贷前`单个样本空间提取

> 说明：`5.1` 中构建的样本表可能存在多个数据时间的样本，实际使用建模样本是，一般仅需要一个数据时间的样本，`5.2`是一个提取一个时间样本的示例。

> 示例

```python
def trans_sample_speace(db_name='tmp_work', table_name=None, label=0, load_date=None, spark=None):
    """
    :param db_name: 样本表库名
    :param table_name: 样本表表名
    :param label: 观察时点的违约状况，一般回溯过去一年的未结清贷款。0-正常；1-关注；2-不良；null-未知。
    :param load_date: 数据时间日期
    :param spark: spark session
    """
    df_sample = spark.sql(f"""
        SELECT uuid, target, obs_date AS load_date
        FROM {db_name}.{table_name}
        WHERE label = {label}
            AND load_date = '{load_date}'
        """)
    FrameToHive(df_sample, db=db_name, table_name=f"{table_name}_{load_date}", spark=spark, partitionBy='load_date')

trans_sample_speace(table_name='znfk_bj_sample_zj_pd_a_v2', load_date=end_date, spark=spark)
```

**注意：**
1. *单一数据日期的样本表表名会默认保存为{table_name}_{load_date}。*
2. *原样本表的`obs_date`会修改为`load_date`，这样与指标的`load_data`进行对应，便于指标取数。*
3. *`label`选取应该注意，若预测为`good To bad`则`label=0`，若预测为`首贷 To bad`则`label=null`，其他预测情况应根据业务要求选择适当的观察时点状态，这里不一一列举。*

### 5.3 `贷中`样本空间的回溯

```python
# 待建设
```

### 5.4 `贷中`单个样本空间提取

```python
# 待建设
```

## 6. 数据指标的匹配索引

### 6.1 样本周期的计算

> 说明：用以计算观察期的开始时间，结束时间；计算表现期的开始时间，结束时间。

> 参数

- `:param obs_months[int]`: 表现期长度。
- `:param start_date`: 观察时点的开始日期。
- `:param end_date`: 最新指标日期。
- `:param start_data_date`: 索引数据最早日期。

> 示例

```python
from ywcxUtils.Dataset import *

# 贷前样本信息表
obs_months = 16                 # 表现期时长
start_date = '20191231'
end_date = '20211031'
start_data_date='20180901'

# 数据周期与样本周期
data_date, sample_date = data_dates(
    obs_months=obs_months, start_date=start_date, 
    end_date=end_date, start_data_date=start_data_date)
```

> `sample_date`：第一个日期为观察时点日期，第二个日期为表现期结束时点日期；在实际应用中以第一个日期索引指标构建样本`X`，以第二个日期回溯样本好坏标签构建样本`Y`。
```bash
[['20191231', '20210430'],
 ['20200131', '20210531'],
 ['20200229', '20210630'],
 ['20200331', '20210731'],
 ['20200430', '20210831'],
 ['20200531', '20210930'],
 ['20200630', '20211031']]
```

> `data_date`: 第一个日期为观察期开始时间，第二个日期为观察期结束日期。
```bash
[('20180930', '20191231'),
 ('20181031', '20200131'),
  ......... ,   ........ 
 ('20200630', '20210930'),
 ('20200731', '20211031')]
```

### 6.2 获取全量指标的信息

> 说明：获取当前全量的指标信息，包括指标名称、代码、存储表等。

> 示例

```python
df_index = GetIndexName()
df_index
```

> 输出结果

|    | body   | class   | sub_class   | module   | index_name     | index_id   | biz_code   | dat_store_tab_nme         | db     | table              | dim      |
|---:|:-------|:--------|:------------|:---------|:--------------|:-----------|:-----------|:--------------------------|:-------|:-------------------|:---------|
|  0 | 企业   | 融资    | 行为充分度  | 融资行为评价 | 距离最早****      | I10301***  |            | zj_dws.t_ent_index_****** | zj_dws | t_ent_index_credit | 日期     |
|  1 | 企业   | 融资    | 行为充分度  | 融资行为评价 | 历史发生****      | I10301***  |            | zj_dws.t_ent_index_****** | zj_dws | t_ent_index_credit | 机构数   |
|  2 | 企业   | 融资    | 行为充分度  | 融资行为评价 | 历史发生****      | I10301***  |            | zj_dws.t_ent_index_****** | zj_dws | t_ent_index_credit | 贷款余额 |
|  3 | 企业   | 融资    | 行为充分度  | 融资行为评价 | 距离最早****      | I10301***  |            | zj_dws.t_ent_index_****** | zj_dws | t_ent_index_credit | 月份数   |
|  4 | 企业   | 融资    | 行为充分度  | 融资行为评价 | 距离最早****      | I10301***  |            | zj_dws.t_ent_index_****** | zj_dws | t_ent_index_credit | 月份数   |

### 6.3 指定`UUID`获取全量的指标长表与指标宽表

> 说明：用于对样本空间，进行指标匹配，由于指标比较多，会先创建样本长表，然后在转换为样本宽表。

> 示例

```python
Ft = ExtractInfrontIndex(
   env='bj',                  # 所属环境 bj-北京 zj-浙江 cq-重庆
   spark=spark,               # spark session
   db_name='tmp_work',        # 样本表长表、宽表存储的库
   dates=sample_date,         # 样本的日期
   sample_speace_table=f'tmp_work.znfk_sample_zj_pd_a_v2_new_credit_20211031',  # 样本空间名称
   long_table_name=f't_cch_sample_infront_long_jt_v2_new_credit',               # 样本长表名称
   wide_table_name=f't_cch_sample_infront_wide_jt_v2_new_credit',               # 样本宽表名称
)

Ft.BatchLong(reset=True, ind=False)       # 样本长表跑数，reset=True 重置长表，reset=False 不重置长表从之前最后的分区时间继续跑数。
Ft.stringCols = []                        # 指定宽表中的字符串列，默认情况下宽表中的字段均为Float类型。
Ft.BatchWide(reset=True)                  # 样本宽表跑数，reset=True 重置宽表，reset=False 不重置宽表从之前最后的分区时间继续跑数。
```

> 长表表结构：

|英文名|中文名|
|-----|-----|
|uuid|唯一编码|
|index_id|指标编码|
|index_val|指标日期|
|module|指标来源（分区字段，一般是表名）|
|load_date|数据日期（分区字段）|


> 宽表示例：

|uuid|target|index_1|index_2|index_3|... ...|load_date|
|-------|-------|-------|-------|-------|-------|-------|
|唯一编码|违约标签y|指标x|指标x|指标x|指标x|数据日期|

*这里，有个性能问题，随着指标数量的增加，`pivot`转宽表的效率会变低；一两千指标百万数据量（uuid）以下还是可以的，后续考虑如何解决吧。*

## X 其他数据分析操作

### X.1 `mapLabel`键值转换

> 说明: `[UDF]` 用来匹配 `pyspark DataFrame` 中的键值对

> 参数

- `:param mapping[Dict]`: 需要匹配的字典

> 示例
```python
# 使用行业分类码值表，设置一列中文行业名称。
df.withColumn('industryCnName', mapLabel(industryDict)(df.industryCode))
```

*也可用`replace`*

----
