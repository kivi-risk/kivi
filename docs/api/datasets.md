# 项目数据集

## 银行违约数据集

> 示例

```python
from kivi.datasets import *

df_bank = Dataset.bank_data()
print(df_bank.head().to_markdown())
```

*输出*

```text
|    |   age | job         | marital   | education   | default   |   balance | housing   | loan   | contact   |   day | month   |   duration |   campaign |   pdays |   previous | poutcome   |   target |
|---:|------:|:------------|:----------|:------------|:----------|----------:|:----------|:-------|:----------|------:|:--------|-----------:|-----------:|--------:|-----------:|:-----------|---------:|
|  0 |    30 | unemployed  | married   | primary     | no        |      1787 | no        | no     | cellular  |    19 | oct     |         79 |          1 |      -1 |          0 | unknown    |        0 |
|  1 |    33 | services    | married   | secondary   | no        |      4789 | yes       | yes    | cellular  |    11 | may     |        220 |          1 |     339 |          4 | failure    |        0 |
|  2 |    35 | management  | single    | tertiary    | no        |      1350 | yes       | no     | cellular  |    16 | apr     |        185 |          1 |     330 |          1 | failure    |        0 |
|  3 |    30 | management  | married   | tertiary    | no        |      1476 | yes       | yes    | unknown   |     3 | jun     |        199 |          4 |      -1 |          0 | unknown    |        0 |
|  4 |    59 | blue-collar | married   | secondary   | no        |         0 | yes       | no     | unknown   |     5 | may     |        226 |          1 |      -1 |          0 | unknown    |        0 |
```

## 犯罪数据集

> 示例

```python
from kivi.datasets import *

df_bank = Dataset.crime_data()
print(df_bank.head().to_markdown())
```

```text
|    |   violent |   murder |   hs_grad |   poverty |   single |   white |   urban |
|---:|----------:|---------:|----------:|----------:|---------:|--------:|--------:|
|  0 |     459.9 |      7.1 |      82.1 |      17.5 |     29   |    70   |   48.65 |
|  1 |     632.6 |      3.2 |      91.4 |       9   |     25.5 |    68.3 |   44.46 |
|  2 |     423.2 |      5.5 |      84.2 |      16.5 |     25.7 |    80   |   80.07 |
|  3 |     530.3 |      6.3 |      82.4 |      18.8 |     26.3 |    78.4 |   39.54 |
|  4 |     473.4 |      5.4 |      80.6 |      14.2 |     27.8 |    62.7 |   89.73 |
```

## 虚拟数据集

> 示例

```python
from kivi.datasets import *

make_data = MakeData()

data = make_data.dataset()
print("train", data.x_train.shape, data.y_train.shape)
print("test", data.x_test.shape, data.y_test.shape)

df_train, df_test = make_data.sample()
print(df_train.shape, df_test.shape)
```

*输出*

```text
>>> train (7000, 5) (7000,)
>>> test (3000, 5) (3000,)

>>> (7000, 7) (3000, 7)
```

## End

-----
