# 评分卡模型监控

> 对模型表现的监控预警和模型影响分析是至关重要的，
模型分数的稳定性变化会直接影响决策阈值的准确性，
并且对现有模型表现进行分析可以对下一步决策提供帮助。

从模型的监控指标中，观察当前**样本分数分布**的变化、**入模特征值分布**的变化、**模型的线上表现**等。
另外，对模型进行监控可以让我们可以及时了解模型状态，当模型发生问题时，
可以快速定位问题的原因（某些特征引起的或客群变化导致的），
也可以快速决定是需要重新构建模型还是只需要对现有模型分数进行校准即可。

评分卡模型监控主要可以分为**前端分析(Front-End)**和**后端分析(Back-End)**，

> **前端分析**: 监控评分卡开发样本和现有样本分数分布的差异程度，关注样本人群的稳定性。
1. Population Stability Index (PSI)：
群体稳定性指标，用来衡量分数分布的变化
2. Characteristic Stability Index (CSI)：
特征稳定性指标，用来衡量特征层面的变化
3. Selection Process: Reject waterfall：
选择过程：拒绝瀑布流，即在申贷放款过程中每个环节
（反欺诈拒绝、政策拒绝、人为拒绝、风控拒绝等）拒绝流量变化，反映了整体流程的稳定性
4. Override Analysis：
撤销分析，分析风控整体决策后最终决定（放款、拒绝）的变化，
即对被模型通过但是被信审拒绝人群的拒绝原因进行分析
5. Concordance Analysis：
一致性分析，分析模型决策与策略决策（不使用模型分的策略规则）的一致性，
即模型决策过程中认为的坏样本，策略决策过程中是否也认为是坏样本

> **后端分析**: 监控评分卡对当前样本的预测能力，关注现有用户的具体表现（需等到当前样本进入表现期）。
1. Vintage Analysis：账龄分析，在账龄的基础上分析投资组合变现
2. Portfolio Analysis：组合分析，关注组合风险，
主要包含逾期分布(Delinquency Distribution)和转移矩阵(Transition Matrix)
3. Ranking & Accuracy：排序性和准确性，用来量化评分卡的强度，
主要通过Lift，Odds，KS(Kolmogorov-Smirnov)，AUC，Gini等指标进行反映
4. Marginal IV On Characteristic：特征的边际信息值，
用来监控特征预测能力的变化，可以和CSI结合起来看
5. Concept Drift Detection：客群偏移检测，用来监控客群变化
6. Score Misalignment：分数错配，用来监控评分卡分数的偏移程度，
从而确定是否需要重新Refit评分卡模型

---

模型监控也可以分为模型表现监控和模型影响分析：

模型表现监控 ：
1. Ranking & Accuracy
2. Population Stability Index
3. Characteristic Stability Index
4. Vintage Analysis
5. Portfolio Analysis
6. MIV On Characteristic
7. Concept Drift Detection
8. Score Misalignment

模型影响分析 ：
1. Selection Process: Reject waterfall
2. Concordance Analysis
3. Override Analysis

> 主标尺二项检验

该检验假设每个等级下的违约事件是相互独立的，对于信用等级$K$，原假设与备择假设如下：

- $H_0:$ 评级等级$K$的违约概率$PD$估计是正确的。
- $H_1:$ 评级等级$K$的违约概率$PD$估计是错误的。

则二项检验统计量表述如下:

对于二项分布$B(N_k,\ PD_k)$，存在临界值$d_k,\ U_{\frac{\alpha}{2}}$与$d_k,\ L_{\frac{\alpha}{2}}$，则

$$
d_k,\ U_{\frac{\alpha}{2}}=min\\{d:\ \sum_{i=d}^{N_k}C_{N_K}^{i}PD_{K}^{i}(1-PD_K)^{N_k-i}\leqslant \frac{\alpha}{2}\\}
$$

$$
d_k,\ L_{\frac{\alpha}{2}}=max\\{d:\ \sum_{i=0}^{d}C_{N_K}^{i}PD_{K}^{i}(1-PD_K)^{N_k-i}\leqslant \frac{\alpha}{2}\\}
$$

使得$D_k$介于临界值之间的概率为
$P(d_{K,\ U_{\frac{\alpha}{2}}} \leqslant D_k \leqslant L_{K,\ \frac{\alpha}{2}}) \geqslant 1-\alpha$, 

若$D_k>d_{K,\ U_{\frac{\alpha}{2}}}$或$D_k<d_{K,\ L_{\frac{\alpha}{2}}}$则拒绝该等级的$H_0$假设，认为$PD$估计值不准。

其中：

- $\alpha$为显著性水平
- $PD_k$为信用等级$K$的违约概率
- $N_k$为信用等级$K$的评级客户数
- $D_k$为等级$K$的实际违约客户数

> 二项检验API: BinomialTest

**置信度默认$\alpha=0.05$**

1. 调用方式一：给定样本的评级等级、预测PD、真实违约

```python
from kivi.ScoreCard import BinomialTest

bt = BinomialTest(
    # 评级等级
    ranking=df.ranking,
    # 真实违约
    target=None,
    # 预测PD
    proba=None,
    # 默认置信度
    alpha=0.05
)

# P值二项检验 
bt.binomial_pvalue()
# 上下界二项检验
bt.binomial_boundary()
```

2. 调用方式二：给定依据评级等级分组后DataFrame

```python
from kivi.ScoreCard import BinomialTest

bt = BinomialTest(df_res=df_level)

# P值二项检验
bt.binomial_pvalue(
    count_col='Count',
    proba_col='PD',
    default_nums_col='bad_count',
)
# 上下界二项检验
bt.binomial_boundary(
    count_col='Count',
    proba_col='PD',
    default_nums_col='bad_count',
    # 单边检验，默认为None, 左侧left, 右侧right
    unilateral=None,
)
```

> 赫芬达尔指数 $Herfindahl\ Index$

**计量样本中不同评级的集中度**

$$H = \sum_{i=1}^{k} \alpha_i^2$$

其中：
$$k=16; 等级数量$$

$$\alpha_i; 为不同等级的样本量占总体的比例$$

$H$的取值范围为$[\frac{1}{k},\ 1]$，值越小表示评级越分散，最大为$20\\%.$

该指数无统计方法来计算置信区间。

```python
from kivi.ScoreCard import herfindahl

# 输入为全样本的评级等级 
herfindahl(ranking)
```

