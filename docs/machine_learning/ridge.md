## 岭回归 🔨

`Ridge` 回归通过对系数的大小施加惩罚来解决普通最小二乘法的一些问题。
岭系数最小化的是带罚项的残差平方和:

$$
min_w ||y - Xw||^2_2 + \alpha * ||w||^2_2
$$

其中， $\alpha \geq 0$是控制系数收缩量的复杂性参数：
$\alpha$ 的值越大，收缩量越大，模型对共线性的鲁棒性也更强。

> Ridge 回归 - 示例

```python
from kivi import LoadData
from kivi.Model import Ridge

load_data = LoadData()
crime_data = load_data.CrimeData()

ri = Ridge(
    data=crime_data.copy(),
    y_name='murder',
    alphas=[0.01, 0.1, 1, 10],
    normalize=True
)

ri.r2_score
ri.model.alpha_
ri.mse
ri.intercept
```
---
