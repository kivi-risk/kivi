## 混淆矩阵

> 混淆矩阵方法

```python
class: ConfusionMatrix()
# 计算混淆矩阵
function: matrix(
    # 真实值
    y_true: 
    # 预测值
    y_pred: 
    # 标签名称
    labels: None
    # 对columns和index的补充
    suffixes: None or ('true_', 'pre_')
    return: DataFrame
)
```

> 混淆矩阵实现方式

```python
from kivi import ModelSelect

# 模型数据
y_true = [2, 0, 2, 2, 0, 1]
y_pred = [0, 0, 2, 2, 0, 2]
lalel = ['a', 'b', 'c']

metrics = ModelSelect.ConfusionMatrix()
matrix = metrics.matrix(y_true, y_pred, lalel)
matrix
```

**Result**

```markdown
|        |   pre_a |   pre_b |   pre_c |
|:-------|--------:|--------:|--------:|
| true_a |       2 |       0 |       0 |
| true_b |       0 |       0 |       1 |
| true_c |       1 |       0 |       2 |
```

> 混淆矩阵可视化

```python
# normalized 为是否将混淆矩阵归一化、默认为False
metrics.plot_matrix(matrix, normalized=True)
```

<img src="./img/egconfusion_matrix.png">

---

## AUC-ROC

> 示例 - 绘制Roc曲线

```python
# 制作模拟数据
import numpy as np

y = np.random.binomial(1, 0.8, 1000)
y_pre = np.abs(y - np.random.normal(0, 0.7, 1000))

# 调用ROC方法
from kivi.kivi import ModelSelect

auc_roc = ModelSelect.AucRoc(y, y_pre)

# 绘制曲线
auc_roc.plot_roc()
```

**Result**

<img src="./img/Roc_auc.png">

> AUC

```python
# AUC
auc_roc.auc_area
# False positive rate and True positive rate
# auc_roc.fpr, auc_roc.tpr
```

---
