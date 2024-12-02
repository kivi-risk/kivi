## LASSO 回归

> Lasso

`Lasso`(Least absolute shrinkage and selection operator, Tibshirani(1996))
方法是一种压缩估计。它通过构造一个罚函数得到一个较为精炼的模型，
使得它压缩一些系数，同时设定一些系数为零。因此保留了子集收缩的优点，
是一种处理具有复共线性数据的有偏估计。$l_1$范数的好处是当$\lambda$充分大时，
可以把某些待估系数精确地收缩到零。
`Lasso`在学习过程中可以直接将部分`feature`系数赋值为`0`的特点使其在调参时非常方便。

**优化目标**

$$
min_w \frac{1}{2 * n_{samples}} ||y - Xw||^2_2 + \alpha * ||w||_1
$$

> Lasso 示例

```python
from kivi import LoadData
from kivi.Model import Lasso

load_data = LoadData()
crime_data = load_data.CrimeData()

crime_data.head()

la = Lasso(
    data=crime_data.copy(),
    y_name='murder',
    alphas=[0.01, 0.1, 1, 10],
    normalize=True
)
```

**返回参数**
```python
# 特征系数
la.coef
# 截距 | 常数项
la.intercept
# mean squared error
la.mse
# 拟合优度
la.r2_score
# 预测
la.model.predict(X)
# 最终选用的alpha值
la.model.alpha_
```

> Lasso 特征选择

**绘制特征重要性**
```python
la.plot_variable_importance()
```

<img src="./img/lasso_feature_select.png">

**筛选前N重要的特征，并返回这些特征的数据**

```python
# 筛选出前2重要的特征
la.select_features(2)
>>>
    |    |   single |   poverty |
    |---:|---------:|----------:|
    |  0 |     17.5 |      29   |
    |  1 |      9   |      25.5 |
    |  2 |     16.5 |      25.7 |
    |  3 |     18.8 |      26.3 |
    |  4 |     14.2 |      27.8 |
    | ...|     ...  |      .... |
```
