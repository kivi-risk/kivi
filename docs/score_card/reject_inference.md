----
## 1. 拒绝推断基本概念

1. `已知好坏标签（Know Good Bad，KGB）样本`：准入模型允许通过的样本集，已知标签。由KGB样本训练的模型又叫KGB模型。
2. `未知标签（Inferred Good Bad，IGB）拒绝样本`：准入模型拒绝的样本集，未知标签。由于IGB样本没有标签，通常不会用于训练模型。在部分方法中可能会生成伪标签，从而参与建模过程。
3. `全量（All Good Bad，AGB）样本`：包含`KGB`和`IGB`两部分的全量样本集。由该部分数据训练得到的模型又称`AGB`模型。

## 2. 截断法

### 2.1 截断法基本步骤

> 基本假设：假设`违约`与`放款`相互独立。

> 步骤：

1. 使用`KGB`模型在拒绝样本上做预测。
2. 将低分样本（如，分数最低的$20%$样本）认为是负样本，其余拒绝样本全部视为灰色样本，不予考虑，或其余样本为正样本，带入模型进行估计。

### 2.2 截断法实践



### 2.3 截断法效果分析

<center>
    <figure class="half">
        <img src="./img/reject_inference_01.png" height="260">
        <img src="./img/reject_inference_02.png" height="260">
    </figure>
    <br>
    <div style="color:orange; border-bottom: 1px solid #d9d9d9;
    display: inline-block;
    color: #999;
    padding: 2px;">上图红线为IGB基准效果，蓝线为n%标记为bad迭代的IBG效果。在标记了拒绝客户98%为bad之后进行模型的拟合，新模型的效果超过了基准效果。</div>
</center>

## 3. 模糊展开发

> 基本假设：

> 步骤：

1. 

## 4. 拒绝推断的应用

### 4.1 什么时候需要应用到拒绝推断



----

## Reference

1. [如何量化样本偏差对信贷风控模型的影响？](https://zhuanlan.zhihu.com/p/350616539)
2. [风控建模中的样本偏差与拒绝推断](https://zhuanlan.zhihu.com/p/88624987)
3. [模型偏差与拒绝推断的Python实现](https://zhuanlan.zhihu.com/p/162724703)

----

