#  基本统计分析方法

## 数据质量分析

### 数据字段数据类型分析

- 默认情况返回：
    - dataType: [dict] 
        - keys: 
            - nanCol: 整列都为缺失的字段
            - numCol: 数值型字段
            - boolCol: 布尔值字段
            - categoryCol: 类别字段
            - targetCol: Label 字段
            - singleValueCol: 单值字段
            - addressCol: 地址字段
            - timeCol: 时间日期类字段
        - values:
            - 各字段的列名
    - df: 经过基本处理的原始数据
    
- 添加如下字段增加返回各数据字段的缺失情况。

    ```python 
    returnType='DataFrame'
    ```
    返回: 
    
    - dataType: 同上
    - df: 同上
    - dfDataType: 各字段缺失情况统计表

> Demo 1

```python
# 引入 kivi- 模块
from kivi import LoadData
from kivi import DataPreparing

# 载入 测试数据
load_data = LoadData()
df_bank = load_data.BankData()

dt = DataPreparing.DataType(df_bank)
(dataType, df) = dt.DataTypeAnalysis()

dataType
```

> Demo 2

```python
# 引入 kivi- 模块
from kivi import LoadData
from kivi import DataPreparing

# 载入 测试数据
load_data = LoadData()
df_bank = load_data.BankData()

dt = DataPreparing.DataType(df_bank, returnType='DataFrame')
(dataType, df, dfDataType) = dt.DataTypeAnalysis()

dataType
```

> Demo 3

- 获取某种数据类型的列名

```python
dataType.get('numCol')
```

- 获取某种类型的数据

```python
df[dataType.get('numCol')]
```

## 数值型字段统计分析

### 数值型字段描述性统计分析

- 偏度（skewness）：
反映总体分布的对称信息，偏度越接近0，说明分布越对称，否则越偏斜。
    - 若偏度为负，说明样本服从左偏分布（概率密度的左尾巴长，顶点偏向右边）。
    - 反之。
- 峰度（kurtosis）：
反映总体分布密度曲线在其峰值附近的陡峭程度（根据样本2阶和4阶中心距计算）
    - 正态分布的峰度为3，如果样本峰度大于3，说明总体分布密度曲线在其峰值附近比正态分布来得陡
    - 小于3，说明总体分布密度曲线在其峰值附近比正态分布平缓。
	- **当数据集偏度或峰度过大时，可能需要进行对数化处理**

```python
# 引入 kivi- 模块
from kivi import LoadData
from kivi.DesStatistic import WoeIV
from kivi import DesStatistic

# 载入 测试数据
load_data = LoadData()
df_bank = load_data.BankData()

des = DesStatistic.Des(df_bank)
description = des.Description()
```

### 数值型字段分布分析 - Box

```python
# 引入 kivi- 模块
from kivi import LoadData
from kivi.DesStatistic import WoeIV
from kivi import DataPreparing

# 载入 测试数据
load_data = LoadData()
df_bank = load_data.BankData()

# 分析数据类型
dt = DataPreparing.DataType(df_bank)
(dataType, df) = dt.DataTypeAnalysis()

# 选取全部数值型数据
numDataCol = dataType.get('numCol')
numData = df[numDataCol]

# 数据归一化
from kivi import DataPreparing

scale = DataPreparing.Scale(numData)
scaleData = scale.MinMax()

# 描述性统计
from kivi import DesStatistic

des = DesStatistic.Des(scaleData)
description = des.Description()

# 绘制 Box
from kivi import DataPreparing

FB = DataPreparing.FeatureBox(description)
FB.Box().render_notebook()
```
### 数值型字段分布分析 - KDE

> 请参考非参数方法 - 核密度估计

## 离散型字段统计分析

- 包含：离散字段Category的类型、数量、比例、以及相应的违约量、违约比例。
	- 在有 target 参数的情况下详细分析，category data 的出现频率与相应的 target 表现。
    - 在无 target 参数的情况下返回 category 的出现频率信息。
    - return: 返回分析结果 cateInfo[DataFrame]

```python
ac = AnalysisCategory(
	cateData, 
	target='target'
)
ac.CategoryInfo()
```
> Demo

```python
# 引入 kivi- 模块
from kivi import LoadData
from kivi.DesStatistic import WoeIV
from kivi import DataPreparing

# 载入 测试数据
load_data = LoadData()
df_bank = load_data.BankData()

# 分析数据类型
dt = DataPreparing.DataType(df_bank)
(dataType, df) = dt.DataTypeAnalysis()

# 选取全部离散型数据
cateDataCol = dataType.get('categoryCol')
cateData = df[cateDataCol + ['target']]

# 分析离散数据
from kivi import DesStatistic

ACD = DesStatistic.AnalysisCategory(cateData)
ACD.CategoryInfo()
```

## 违约概率分析

### 连续型数据

> DefaultAnalysis

- 连续型数据方法: DefaultFreGraph
- 离散型数据方法: DefaultCateGraph

> Demo

```python
# 引入 kivi- 模块
from kivi import LoadData
from kivi.DesStatistic import WoeIV
from kivi.DesStatistic import DefaultAnalysis

# 载入 测试数据
load_data = LoadData()
df_bank = load_data.BankData()
test_data = df_bank[['age', 'target']]

# 等距分箱计算
Distance = WoeIV.Distance(bins=10)
woe = Distance.WoeIV(
    test_data.age,
    test_data.target,
)

# 违约频率分析
DA = DefaultAnalysis(
    woe,
    imageName='default_cate',
    width='750px',
    height='480px'
)
DA.DefaultFreGraph().render_notebook()
```

<p><iframe src="./html/default_rate.html"  width="750" height="500"></iframe></p>

### 离散型数据

> DefaultAnalysis

- 连续型数据方法: DefaultFreGraph
- 离散型数据方法: DefaultCateGraph

> Demo

```python
# 引入 kivi- 模块
from kivi import LoadData
from kivi.DesStatistic import DefaultAnalysis

# 载入 测试数据
load_data = LoadData()
df_bank = load_data.BankData()
test_data = df_bank[['job', 'target']]

# 违约频率分析
DA = DefaultAnalysis(
    test_data,
    col='job',
    sortBy='bad',
    imageName='default_rate_cate',
    width='750px',
    height='480px'
)
DA.DefaultCateGraph().render_notebook()
```

<p><iframe src="./html/default_rate_cate.html"  width="750" height="480"></iframe></p>

**Png格式**

```python
DA.DefaultCatePng(
    # 支持以下四种排序方式绘图
    # bad good bad_rate sample_rate
    sort_by='labels',
    # Title
    title=f'{col} {col_des.get(col)}', 
    # X轴旋转
    rotation=0, 
    # 字体
    font=font
)
```

<img src="./img/cate_default_png.jpeg" width="60%">

**Bin-Plot**

```python
from kivi.DesStatistic import plot_bin

plot_bin(
    woe
)
```

## 相关系数示例

> Demo

```python
# 引入 kivi- 模块
from kivi import LoadData
from kivi import DesStatistic

# 载入 测试数据
load_data = LoadData()
df_bank = load_data.BankData()

# 绘图并保存数据
DesStatistic.CorrHeatMap(df_bank, csvName='test', imageName='test').render_notebook()
```

<p><iframe src="./html/corr_hootmap.html"  width="1100" height="620"></iframe></p>

## 其他方法

### 归一化

> Min-Max Normalization

```latex
 x' = \frac {x - X_{min}} {X_{max} - X_{min}}
```

```python
from kivi.DataPreparing import Scale

scale = Scale(DataFrame)
scale.MinMax()
```

> 平均归一化

```latex
x' = \frac{x - μ}{MaxValue - MinValue}
```

```python
from kivi.DataPreparing import Scale

scale = Scale(DataFrame)
scale.MeanMinMax()
```

### 标准化

> Z-score规范化

```latex
x' = \frac{x - \mu}{\sigma}
```

```python
from kivi.DataPreparing import Scale

scale = Scale(DataFrame)
scale.ZScore()
```
