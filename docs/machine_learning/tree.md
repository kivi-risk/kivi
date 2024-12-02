## 决策树模型与规则生成

**置于A卡之后**

> 方法:

```python
class: Tree(
    
)
```

> 示例 - 决策树模型

```python
# 引入 kivi- 模块
from kivi import LoadData
from kivi.Model import Tree

# 载入 测试数据
load_data = LoadData()
df = load_data.BankData()

# 筛选数值特征
df = df.convert_dtypes().select_dtypes('int')

# 进行树模型的拟合
TreeModel = Tree(df, y_name='target')
TreeModel.fit(max_depth=4)
```

> 示例 - 决策树绘图

```python
TreeModel.plot_tree()
```

<img src="./img/tree.png" width="60%">

**解读**

1. 每个节点第一个信息为规则
2. 第二个信息为MSE(Mean squared error)
3. 第三个信息为Samples rate
4. 第四个信息为Bad rate

> 示例 - 决策树评估

```python
TreeModel.metrics()
# 总体MSE, 总体违约率
TreeModel.mse, TreeModel.bad_rate
```

> 违约分析：客群增大，违约降低

1. 分别做树回归与贷前分类的`违约、客户占比`交叉表
2. 根据交叉表的违约率选定客群

---

