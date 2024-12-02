# 数据可视化

> diagonal correlation

下三角相关系数heatmap。

```python
from kivi.DataVision import diagonal_corr
from string import ascii_letters
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Generate a large random sql
rs = np.random.RandomState(33)
d = pd.DataFrame(data=rs.normal(size=(100, 26)),
                 columns=list(ascii_letters[26:]))
diagonal_corr(d)
plt.show()
```

<img src="./img/diagonal_heatmap_corr.png">

> structure correlation

此 Heatmap 增加了对于字段的聚类分析，使得在相关性分析中可以更直观的观察特征直接的联结程度。

```python
from kivi.DataVision import structure_corr

col_cate = [f"{item.split('_')[0]}_{item.split('_')[1]}" for item in col]
structure_corr(
    # DataFrame, 需要分析的数据集
    df_temp,
    # 字段类别标签
    col_cate,
)
```

<img src="./img/structure_corr.png">
