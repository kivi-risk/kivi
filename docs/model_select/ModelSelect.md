# 概率校准

## 概率校准基本方法与概念(calibration)

### 分数校准的概念与可靠性曲线

**在机器学习模型实践应用中，我们主要关注分类模型的排序性(ranking)。**
这就引出了校准(calibration)的概念，即预测分布和真实分布（观测）在统计上的一致性。

> 一般概率校准可分为三个方面:
1. **欠采样概率校准**: 由于正负样本的采样频率不同导致的模型输出概率与实际概率不一致。
2. **模型概率校准**: 由于使用的模型方法不同，由模型特性导致的模型输出概率与实际概率不一致。
3. **错误分配概率校准**: 由于测试样本与泛化样本之间的分布发生了变化，导致模型输出概率与实际概率不一致。

> 可靠性曲线图(`Reliability Curve Diagrams`)

由于我们无法获知真实的条件概率，通常用观测样本的标签来统计代替，
并用可靠性曲线图(`Reliability Curve Diagrams`)来直观展示当前模型的输出结果与真实结果有多大偏差。
如下图所示:

<img src="./img/calibration.png" width="480px">

- 横坐标为事件发生预测概率，
- 纵坐标为事件发生实际频率，
- 展示`某个事件预测概率 VS 实际发生的频率`之间的关系。
- 对于一个理想的预测系统，两者是完全一致的，也就是对角线。

如果数据点几乎都落在对角线上，那么说明模型被校准得很好；
反之，如果和对角线的偏离程度越明显，则校准越差。

> 绘制方法请参考：[可靠性曲线图](./model_select/ModelSelect?id=概率校准曲线-可靠性曲线图)

### 分数校准的业务应用场景

> 分数校准主要目的在于：

- 确保不同评分卡给出的分数具有相同的含义。
- 提高预测概率与真实概率之间的一致性。
- 修正实际概率和开发样本中期望概率之间的偏差。

> 业务场景

**分群评分卡**

- 单一评分卡在全量人群上表现并不是特别好。此时会采用先分群(`segmentation`)，再针对各人群建立多个子评分卡模型。
基于以下几个原因，我们需要把分数校准到同一尺度。
    1. 针对多个分支模型需要制订多套风控策略，将会大大增加策略同学的工作量，且不利于策略维护调整。
    1. 不同评分卡输出的分数并不具有可比性，它们的分布存在差异。为了融合后统一输出一个最终分数。
    1. 各分群评分卡相当于一个分段函数，分数之间存在跃变。校准可以保证各分数具有连续性。

**降级备用策略**

- 在用到外部数据建模时，考虑到外部数据采集上存在潜在的不稳定性，我们通常会采取降级策略。
也就是说，去掉外部数据后再建立一个模型，作为主用(`active`)模型的一个备用(`standby`)模型。
如果外部数据有一天停止提供服务，就可以切换到备用模型上。
- 同时，为了使下游业务调用无感知，我们会将主用备用模型的分数校准至一个尺度。
这样就能保证风控策略只需要制订一套cutoff方案，且不用调整，只需做必要的策略切换日志和前后波动监控即可。

**客群变化修正**

- 当面向客群发生变化时，开发样本与最近样本之间存在偏差(`bias`)。
如果开发样本的`Odds`大于实际的`Odds`，那么计算每个分数段的坏样本率，得出来的结果将会大于真实情况。
- 然而考虑到建模成本，我们有时并不想`refit`模型，此时就可以利用最近样本对评分卡进行校准，修正偏差。

### 模型概率校准

> 方法一：`Platt scaling`使用`LR`模型对模型输出的值做拟合
> （并不是对`reliability diagram`中的数据做拟合），
> 适用于**样本量少**的情形，如信贷风控场景中。

1. 对于模型输出结果`f(x)`，将输出通过`sigmoid`变化：
```latex
P(y=1|f)=\frac{1}{1+exp(Af(x)+B)}
```
2. 然后通过最大化似然函数（最小化对数损失函数）的方法可以求得参数`A, b`，即：
```latex
arg\ min_{A, B}\{-\sum_{i}y_i log(p_i)+(1-y_i)log(1-p_i)\}
```

3. 最后可得校准后的概率：
```latex
p_i=\frac{1}{1+exp(Af_i+b)}
```

`Platt scaling`是一种参数化方法(`The parametric approach`)， 
使用`LR`模型(`sigmoid`函数)对模型的输出值进行拟合，
将模型的原始输出值映射为概率值，区间`[0，1]`。假设`f(x)`为模型的输出值，
上式中的参数`A`，`B`通过在训练集`(f_i, y_i)`上进行最大似然估计获取。
**更多应用于不同模型的概率校准**。

> 方法二：`Isotonic regression`则是对`reliability diagram`中的数据做拟合，

保序回归是一种非参回归模型`(nonparametric regression)`。
这种方法只有一个约束条件即，函数空间为单调递增函数的空间。
基于可靠性图`(reliability diagram)`，
给定模型预测的分数`f_i` ，真实的分数`y_i`，保序回归的模型公式为：

```latex
y_i = m(f_i)+\varepsilon
```

其中，`m`表示保序函数（单调递增函数）。所以保序回归的目标函数为:

```latex
\hat{m} = arg\ min_z\sum(y_i - z(f_i))^2
```

⚠️ 注意，适用于**样本量多**的情形。例如搜索推荐场景。样本量少时，使用`isotonic regression`容易过拟合。

### 欠采样概率校准 🔨

> 方法三：欠采样下的概率校准方法`Prior Correction`

对于正负样本不平衡的样本，欠采样是一种常用的技术，可以减少正负样本的倾斜。
但是，由于欠采样修改了训练集的先验分布，因此基于采样后样本训练的分类器得到的后验概率会出现偏差。
尽管，欠采样导致的偏差不会影响后验概率的排序性，但是会显著影响分类得到的准确性和以及样本的真实概率。

`Prior Correction`方法可以理解成是基于先验分布的校验。对负样本进行欠采样会改变样本的先验分布，
导致训练得到的模型是有偏的，并且对正样本的估计概率偏高，因此需要把正样本比例作为先验信息，
对负采样后训练得到的模型进行校准。

在样本不平衡的二分类任务中使用欠采样的方法训练分类器，
则可以使用下面的公式将分类器得到的预测概率校准到真实概率上：

```latex
p = \frac{wp_s}{wp_s-p_s+1}
```

其中， `w` 是欠采样过程中负样本（多类样本）的采样率， `p_s` 是欠采样后分类器预测的概率。

**证明：**

假设给定类 $y$ 时，样本选择变量 $s$ 与输入 $x$ 
无关（ $s=1$ 表示样本被选中，$s=0$ 表示样本没被选中），
即 $p(s|y, x) = p(s|y)$，这个假设意味着 $p(x|y, s) = p(x|y)$，即通过消除多数类中的随机观察值，
不会改变类内输入 $x$ 的分布。同时，因为欠采样的原因，样本的先验概率发生了改变
$
p(y|s=1) \neq p
$
，并且条件概率也发生了改变，即
$
p(y|x, s=1) \neq p(y|x)
$
。对于采样后在训练集中的样本点 $(x,\\ y)$，
我们用符号 $+$ 表示 $y=1$，符号 $-$ 表示 $y=0$，利用贝叶斯公式，我们可以得到：

$$
\begin{aligned}
P(+|x,\ s=1)\ & =\ \frac{p(+,\ x,\ s=1)}{p(x,\ s=1)}\\\\
& =\ \frac{p(s=1|+,\ x)p(+,\ x)}{p(s=1|x)p(x)}\\\\
& =\ \frac{p(s=1|+)p(+|x)p(x)}{(p(s=1|+)p(+|x)\ +\ p(s=1|-)P(-|x))p(x)}\\\\
& =\ \frac{p(s=1|+)p(+|x)}{p(s=1|+)p(+|x)\ +\ p(s=1|-)p(-|x)}\\\\
\end{aligned}
$$
$$
\because\ P(s=1|+)\ =\ 1\\\\
P(+|x,\ s=1)\ =\ \frac{p(+|x)}{p(+|x)\ +\ p(s=1|-)p(-|x)}
$$

定义 $w=p(s=1|-)$ 为负类样本的采样率，$p=p(+|x)$ 为原始样本下正类的后验概率（即样本为正的真实概率），
$p_s=p(+|x,\ s=1)$ 为采样后正类的后验概率（即利用采样后样本训练分类器得到的预测概率），
则上式可以写成：
```latex
p_s = \frac{p}{p+w(1-p)}
```
即:
```latex
p = \frac{wp_s}{wp_s-p_s+1}
```
---
*ps:*
该概率校准公式的另外一种表现形式如下：
```latex
p(+|x)=[1+(\frac{1}{p(+|x,\ s=1)}-1)(\frac{1-\tau}{\tau})(\frac{\overline{y}}{1-\overline{y}})]^{-1}
```
其中，`p(y=1|x)`表示正样本的真实概率，p(y=1|x,\ s=1)表示欠采样后模型预测的正样本概率，$\tau$ 
为采样前样本中正样本比例，$\overline{y}$ 为采样后样本中正样本比例，
具体证明方法可以参考论文<sup>[9]</sup>。
令$p$表示真实概率（即校准后的概率），$p_s$ 表示预测概率，$w$ 表示负样本的采样率，可知:
```latex
\frac{1}{w} = (\frac{1-\tau}{\tau})(\frac{\overline{y}}{1-\overline{y}})\\
\ \\
p = \frac{1}{1+(\frac{1}{p_s}-1)/w} = \frac{wp_s}{wp_s-p_s+1}
```
所以该概率校准公式的两种形式是等价的。
对于二分类问题中的逻辑回归模型:
```latex
IF:\ p(y=1|x,\ s=1)=(1+e^{-X\beta})^{-1}\\
\ \\
SO:\ p(y=1|x)=[1+e^{-X\beta+ln[(\frac{1-\tau}{\tau})(\frac{\overline{y}}{1-\overline{y}})]}]^{-1}=[1+e^{-x\beta-ln(w)}]^{-1}
```
---
所以欠采样后利用`MLE`估计得到的模型参数中，
非截距项的参数与真实参数是一致的，不用校准。
只需对截距项的参数按下面的公式进行校准即可：
```latex
\beta_0 = \hat{\beta_0}-ln[(\frac{1-\tau}{\tau})(\frac{\overline{y}}{1-\overline{y}})] = \hat{\beta_0} + ln(w)
```
对于LR模型来说，截距项的校准可以离线完成，不需要实时计算，能减少实时计算量。

> 方法四：欠采样下的概率校准方法`Weighting`

`Weghting`方法可以理解成对样本进行加权。
在进行欠采样后，对正负样本进行样本加权，然后再训练模型。
在逻辑回归模型中，当样本不加权时，对数似然函数`log-likelihood`可以写成：

$$
\begin{aligned}
lnL(\beta|y) & = \sum_{y_{i}=1}ln(p_i)+\sum_{y_{i}=0}ln(1-p_i) \\\\
& = -\sum_{i=1}^{n}ln(1+e^{(1-2y_i)X_i\beta})
\end{aligned}
$$

当正负样本加权后，加权的对数似然函数可以写成：

$$
\begin{aligned}
lnL_{w}(\beta|y) & = w_1\sum_{y_{i}=1}ln(p_i)+w_0\sum_{y_{i}=0}ln(1-p_i) \\\\
& = -\sum_{i=1}^{n}w_iln(1+e^{(1-2y_i)X_i\beta})
\end{aligned}
$$

$$
w_1 = \frac{\tau}{\overline{y}} = 1
$$

为正样本的权重，
$$
\begin{aligned}
w_0 & = \frac{1-\tau}{1-\overline{y}} \\\\
& = (\frac{1-\tau}{\tau})(\frac{\overline{y}}{1-\overline{y}}) \\\\
& = \frac{1}{w}
\end{aligned}
$$

正样本权重为负样本采样率的倒数。对比`Prior Correction`和`Weighting`方法，
当建立的模型存在偏差时，`Weighting`方法的鲁棒性优于`Prior Correction`。
当样本量较少时，`Weighting`方法不如`Prior Correction`，但是差异不大；
当样本量较大时，`Weighting`方法更适合。论文<sup>[6]</sup>的附录B还推导给出了多类别的校准公式，
这个就可以用于`Softmax Regression`等模型中。

### 错误分配概率校准 🔨

> 方法五: Odds校准，错误分配`Misassignment`

LR中的截距近似于开发样本的ln(Odds)，那么就可以采取以下方式进行校准。

$$
\begin{aligned}
ln(\frac{p}{1-p}) & = W^TX + ln(Odds_{expect}) \\\\
ln(Odds_{calibrate}) & = ln(\frac{Odds_{actual}}{Odds_{expect}}) = ln(Odds_{actual}) - ln(Odds_{expect})
\end{aligned}
$$

$$
\begin{aligned}
ln(\frac{p}{1-p}) & = w_1x_1 + ln(Odds_{expect}) + ln(Odds_{calibrate})\\\\
& = w_1x_1 + ln(Odds_{actual}) \\\\
\because Score & = A-Bln(Odds)
\end{aligned}
$$

那么，利用近期样本和开发样本就可以分别绘制出这样一条直线。
如果这两条直线是平行关系，此时我们认为：在同一个分数段上，
开发样本相对于近期样本把$Odds$预估得过大或过小。
因此，可通过 $Ln(Odds_{actual}) - Ln(Odds_{expect})$ 来进行校正。

> 针对**分群评分卡和降级备用策略**进行Platt校准

‼️ 注意`Platt Scaling`应用于以上两种场景是[信用评分卡模型分数校准](https://zhuanlan.zhihu.com/p/82670834)<sup>[5]</sup>
这篇文献给出的建议，但一般认为`Platt Scaling`方法只能应用于分群评分卡或降级备用策略中采用了不同预测模型的情况。
在这种情况下使用`Platt Scaling`方法，对输出概率进行一致性校准，可得到一致性的概率输出，从而使不同模型输出的概率可以进行平行比较。
但在文献[信用评分卡模型分数校准](https://zhuanlan.zhihu.com/p/82670834)<sup>[5]</sup>给出的示例情况下，
不建议采用`Platt Scaling`方法，而应该采用统一的缩放机制。这里`Platt Scaling`方法的应用核心应该在于，不同的模型是否采用了同样的预测模型。
因此下文给出一个示例进行不同模型之间的`Platt Scaling`，请参考下文[*模型概率校准*](./model_select/ModelSelect?id=模型概率校准)。

> 针对**客群变化修正**进行Odds校准

## 概率校准曲线 | 可靠性曲线图

> 问题与概念 - 明确一般机器学习模型的近似概率输出与逻辑回归的差异

逻辑回归本身具有良好的校准度，其输出概率与真实概率之间存在良好的一致性。
因此，我们也就可以直接把概率分数线形映射为整数分数。

但是，逻辑回归简单的模型结构也导致了在大数据的背景下，其概率拟合精度差强人意。
如果我们用机器学习模型（如XGBoost、随机森林等）来风控建模，
又希望把概率对标到真实概率，那么我们就需要对机器学习模型的输出结果进行概率校正，
使其输出概率与真实概率尽量一致。首先我们需要明确一般机器学习模型的近似概率输出与逻辑回归的差异。
这里采用概率校准曲线的方式，可视化这种差异。

> 示例 - 概率校准曲线

```python
from kivi.LoadData import MakeData
from kivi.ModelSelect import Calibration

# 创建数据集
make_data = MakeData()
X_train, X_test, y_train, y_test = make_data.get_dataset()

# 实例化 Calibration
calibra = Calibration()

from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC

# 定义分类器
lr = LogisticRegression()
gnb = GaussianNB()
svc = LinearSVC(C=1.0)
rfc = RandomForestClassifier()

# 储存预测概率的List
ProbPosLs = []

# 训练与预测
for clf, name in [(lr, 'Logistic'),
                  (gnb, 'Naive Bayes'),
                  (svc, 'Support Vector Classification'),
                  (rfc, 'Random Forest')]:
  clf.fit(X_train, y_train)
  if hasattr(clf, "predict_proba"):
    prob_pos = clf.predict_proba(X_test)[:, 1]
  else:
    prob_pos = clf.decision_function(X_test)
    prob_pos = (prob_pos - prob_pos.min()) / (prob_pos.max() - prob_pos.min())
  ProbPosLs.append((name, prob_pos))

# 绘制概率校准曲线
% matplotlib
inline  # 仅在Jupyter Notebook中需要
calibra.Plot(y_test, ProbPosLs)
```

<img src="./img/calibration.png" width="480px">


> 概率校准分析

- 对于一般的逻辑回归函数分类器，一般输出可以直接解释为置信度。
例如，模型计算样本中给出的`predict_proba`值接近于0.8，近似`80％`属于`1`分类。
- 由于`LogisticRegression`直接优化了对数损失，因此返回了经过良好校准的预测概率。
而其他机器学习方法返回有偏概率，每种方法有不同的偏差：
- `GaussianNaiveBayes`倾向于将概率推理到`0`或`1`（请注意直方图中的计数）。
这主要是因为它假定要素在给定类别的情况下是条件独立的，
- `RandomForestClassifier`表现出相反的行为：直方图显示的峰值约为。
概率为`0.2`和`0.9`，而接近`0`或`1`的概率非常罕见。
- 支持向量分类`SVC`与`RandomForestClassifier`相比，显示出更大的`S`型曲线，
该方法侧重于靠近决策边界的样本。

## 概率校准评估指标

> 对数损失函数(`Logarithmic Loss，LL`)

```latex
Loss_{log} = -\sum_{i=1}^{N}(y_ilog(p_i)+(1-y_i)*log(1-p_i)) \\
\ \\
y_i \in \{0, 1\}: Actual\ class\ label \\
\ \\
p_i \in [0, 1]: Estimated\ default\ probability
```

当真实label=0，预测概率为1时，损失函数将达到+∞。
LL惩罚明显错误的分类。当预测概率越接近于真实标签，
LL越小，模型的校准效果就越好。

> Brier分数(`Brier score，BS`)

```latex
Brier = \frac{1}{N}\sum_{i=1}^{N}(y_i-P_i)^2\\
\ \\
y_i \in \{0, 1\}: Actual\ class\ label \\
\ \\
p_i \in [0, 1]: Estimated\ default\ probability
```

当BS指标越小，代表模型预测结果越接近于真实标签。
因此，这两个指标都反映样本集上真实标签与预测概率之间的差异性，也就是一致性。
这里关于`Brier`分数的计算推荐直接使用`sklearn.metrics.brier_score_loss`方法。
参数方法与示例如下。

> Coding by Scikit-learn

**参数**

```python
Parameters:
    # True targets.
    y_true: array, shape (n_samples,)
    
    # Probabilities of the positive class.
    y_prob: array, shape (n_samples,)
    
    # Sample weights.
    sample_weight: array-like of shape (n_samples,), default=None
    
    # Label of the positive class. 
    # Defaults to the greater label unless y_true is 
    # all 0 or all -1 in which case pos_label defaults to 1.
    pos_label: int or str, default=None

Returns:
    # Brier score
    score: float
```

**示例**

```python
import numpy as np
from sklearn.metrics import brier_score_loss

y_true = np.array([0, 1, 1, 0])
y_true_categorical = np.array(["spam", "ham", "ham", "spam"])
y_prob = np.array([0.1, 0.9, 0.8, 0.3])
brier_score_loss(y_true, y_prob)
>>> 0.037...
brier_score_loss(y_true, 1-y_prob, pos_label=0)
>>> 0.037...
brier_score_loss(y_true_categorical, y_prob, pos_label="ham")
>>> 0.037...
brier_score_loss(y_true, np.array(y_prob) > 0.5)
>>> 0.0
```

## 模型概率校准方法

### 模型概率校准方法

> 问题描述

在上面[概率校准曲线 | 可靠性曲线图](./model_select/ModelSelect?id=概率校准曲线-可靠性曲线图)的介绍中，初步了解了逻辑回归的概率输出与
其他机器学习模型概率输出的概率差别；并基本认为，逻辑回归基本近似真实概率，而其他模型的输出并不是真实概率的近似。

> 绘制[概率校准曲线 | 可靠性曲线图](./model_select/ModelSelect?id=概率校准曲线-可靠性曲线图)中的各类分类器的概率输出分布。

```python
from kivi.kivi.FeatureSelect import KS

ks = KS()

ks.Distribution(
  dict(ProbPosLs),
)
```

**Result**

<img src="./img/calibration_distribution.png">

上图展示了不同分类器的概率输出分布，发现不同分类器的概率输出差别很大。
如果以逻辑回归为真实概率的近似的话，
其他分类器的输出远远不能认为是真实概率的近似，需要进一步的转换。

> 概率校准

> Coding by Scikit-learn

**以下给出一种粗糙的模型模拟**

```python
import matplotlib.pyplot as plt

# 数据
from sklearn import datasets
# 分类器
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
# 评估
from sklearn.metrics import (brier_score_loss, precision_score, recall_score, f1_score)
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import train_test_split

from kivi.ModelSelect import Calibration

calibration = Calibration()

# 模拟数据
X, y = datasets.make_classification(n_samples=100000, n_features=20,
                                    n_informative=2, n_redundant=10,
                                    random_state=42)

# 切分数据
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.99,
                                                    random_state=42)


def plot_calibration_curve(est, name, fig_index):
  """Plot calibration curve for est w/o and with calibration. """
  # 使用 isotonic calibration 进行校准
  isotonic = CalibratedClassifierCV(est, cv=2, method='isotonic')

  # 使用 sigmoid calibration 进行校准
  sigmoid = CalibratedClassifierCV(est, cv=2, method='sigmoid')

  # 逻辑回归基准
  lr = LogisticRegression(C=1.)

  fig = plt.figure(fig_index, figsize=(10, 10), dpi=150)
  ax1 = plt.subplot2grid((3, 1), (0, 0), rowspan=2)
  ax2 = plt.subplot2grid((3, 1), (2, 0))

  ax1.plot([0, 1], [0, 1], "k:", label="Perfectly calibrated")
  for clf, name in [(lr, 'Logistic'),
                    (est, name),
                    (isotonic, name + ' + Isotonic'),
                    (sigmoid, name + ' + Sigmoid')]:
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    if hasattr(clf, "predict_proba"):
      prob_pos = clf.predict_proba(X_test)[:, 1]
    else:
      prob_pos = clf.decision_function(X_test)
      prob_pos =
        (prob_pos - prob_pos.min()) / (prob_pos.max() - prob_pos.min())

    clf_score = brier_score_loss(y_test, prob_pos, pos_label=y.max())
    print("%s:" % name)
    print("\tBrier: %1.3f" % (clf_score))
    print("\tPrecision: %1.3f" % precision_score(y_test, y_pred))
    print("\tRecall: %1.3f" % recall_score(y_test, y_pred))
    print("\tF1: %1.3f\n" % f1_score(y_test, y_pred))

    fraction_of_positives, mean_predicted_value =
      calibration.calibration_curve(y_test, prob_pos, n_bins=10)

    ax1.plot(mean_predicted_value, fraction_of_positives, "s-",
             label="%s (%1.3f)" % (name, clf_score))

    ax2.hist(prob_pos, range=(0, 1), bins=10, label=name,
             histtype="step", lw=2)

  ax1.set_ylabel("Fraction of positives")
  ax1.set_ylim([-0.05, 1.05])
  ax1.legend(loc="lower right")
  ax1.set_title('Calibration plots  (reliability curve)')

  ax2.set_xlabel("Mean predicted value")
  ax2.set_ylabel("Count")
  ax2.legend(loc="upper center", ncol=2)

  plt.tight_layout()


# Naive Bayes
plot_calibration_curve(GaussianNB(), "Naive Bayes", 1)

# Linear SVC
plot_calibration_curve(LinearSVC(max_iter=10000), "SVC", 2)

plt.show()
```

**Result**

<figure class="half">
    <img src="./img/svc_calibration.png" width="350">
    <img src="./img/naive_bayes_calibration.png" width="350">
</figure>

**上图显示经过概率校准，机器学习分类器输出概率近似真实概率。**

`Naive Bayes`:

| 指标      | Logistic | Naive Bayes | Naive Bayes + Isotonic | Naive Bayes + Sigmoid |
|----------|-----------|-------------|-----------------------|-----------------------|
| Brier    | 0.099     | 0.118        | `0.098`              | `0.109`               |
| Precision | 0.872     | 0.857       | 0.883               | 0.861                  |
| Recall    | 0.852     | 0.876       | 0.836               | 0.871                  |
| F1        | 0.862     | 0.867       | 0.859               | 0.866                  |

`SVC`:

| 指标      | Logistic | SVC    | SVC + Isotonic | SVC + Sigmoid |
|----------|----------|--------|----------------|---------------|
| Brier    | 0.099    |0.163   |`0.100`         |`0.099`        |
| Precision|0.872     |0.872   |0.853           |0.874          |
| Recall   |0.852     |0.852   |0.878           |0.849          |
| F1       |0.862     |0.862   |0.865           |0.861          |

**上表显示了概率校准取得了良好的概率输出结果**

### 错误分配概率校准方法 🔨

### 欠采样概率校准方法 🔨

> 📚 Reference

- [1] Predicting Good Probabilities with Supervised Learning, A. Niculescu-Mizil & R. Caruana, ICML 2005
- [2] [Reliability diagrams](https://www.cnblogs.com/downtjs/p/3433021.html)
- [3] [使用 Isotonic Regression 校准分类器](https://vividfree.github.io/%25E6%259C%25BA%25E5%2599%25A8%25E5%25AD%25A6%25E4%25B9%25A0/2015/12/21/classifier-calibration-with-isotonic-regression)
- [4] Alexandru Niculescu-Mizil, et al. Predicting Good Probabilities With Supervised Learning. ICML2005.
- [5] [信用评分卡模型分数校准](https://zhuanlan.zhihu.com/p/82670834)
- [6] Gary King, Langche Zeng. Logistic Regression in Rare Events Data. Political Methodology. 2002
- [7] [Calibrating Probability with Undersampling for Unbalanced Classification](www3.nd.edu/~rjohns15/content/papers/ssci2015_calibrating.pdf)
- [8] ["SAS"-Oversampling](www.data-mining-blog.com/tips-and-tutorials/overrepresentation-oversampling/)
- [9] [面向稀有事件的 Logistic Regression 模型校准](vividfree.github.io/%25E6%259C%25BA%25E5%2599%25A8%25E5%25AD%25A6%25E4%25B9%25A0/2015/12/15/model-calibration-for-logistic-regression-in-rare-events-data)


> Editor&Coding: Chensy
