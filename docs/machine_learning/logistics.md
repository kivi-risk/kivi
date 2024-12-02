# 逻辑回归

> 风控与评分卡

风控顾名思义就是风险控制，指风险管理者采取各种措施和方法，
消灭或减少风险事件发生的各种可能性，或风险事件发生时造成的损失。

信用评分卡模型是最常见的金融风控手段之一，它是指根据客户的各种属性和行为数据，
利用一定的信用评分模型，对客户进行信用评分，据此决定是否给予授信以及授信的额度和利率，
从而识别和减少在金融交易中存在的交易风险。

评分卡模型在不同的业务阶段体现的方式和功能也不一样。
按照借贷用户的借贷时间，评分卡模型可以划分为以下三种：

1. 贷前：申请评分卡（Application score card），又称为A卡
1. 贷中：行为评分卡（Behavior score card），又称为B卡
1. 贷后：催收评分卡（Collection score card），又称为C卡

> 逻辑回归

**逻辑回归本身具有良好的校准度，其输出概率与真实概率之间存在良好的一致性。**
因此，我们也就可以直接把概率分数线形映射为整数分数。

将客户违约的概率表示为p，则正常的概率为1-p。
$$
p(y=1|\theta,\ X+b) = \frac{1}{1+e^{-\theta^TX+b}}
$$
整理以上公式：
$$
\begin{aligned}
log(\frac{p}{1-p}) & = \theta^TX+b \\\\
& = \theta^TWoe(X)+b
\end{aligned}
$$
`WOE`变换是一个分段函数，其把自变量`x`与`y`之间的非线性关系转换为线性关系。
若把`WOE`定义如下:

$$ 
Woe(X)=
\begin{cases}
woe_1 = ln(\frac{Bad_1}{Good_1}) - ln(\frac{Bad_T}{Good_T}),\ x\in bin_1 \\\\
woe_2 = ln(\frac{Bad_2}{Good_2}) - ln(\frac{Bad_T}{Good_T}),\ x\in bin_2 \\\\
.... \\\\
woe_m = ln(\frac{Bad_m}{Good_m}) - ln(\frac{Bad_T}{Good_T}),\ x\in bin_m \\\\
\end{cases}
$$

那么含义为：自变量`x`在经过`WOE`变换后，取值越大，预测为`bad`的概率越高。
我们可以定义`Odds`坏好比来表示客户违约的相对概率，`Odds`越大，代表`bad`的概率越高；
而信用分越高，代表`bad`的概率越低。

$$
define
\begin{cases}
A>0,\ B>0 \\\\
odds = \frac{p}{1-p}
\end{cases}
$$

将 $odds$ 带入逻辑回归函数可得：
$$
log(odds) = \theta^TX+b
$$

评分卡的分值可以定义为比率对数的线性表达来，即：
$$
\begin{aligned}
Score & = A-B\times log(odds)\\\\
& = A-B[\theta^TWoe(X)+b]
\end{aligned}
$$

其中`A`与`B`是常数，通常将常数A称为补偿，常数B称为刻度。
`B`前面的负号可以使得违约概率越低，得分越高。
通常情况下，即高分值代表低风险，低分值代表高风险。`A`、`B`的值可以
通过将两个已知或假设的分值带入计算得到。通常情况下，需要设定三个假设（参数）：

1. **基准`Odds`**：与真实违约概率一一对应，可换算得到违约概率。
2. **基准分数**：某个特定的违约概率下的预期评分，即比率`Odds`为 $\theta_0$ 
时的分数为 $P_0$。
2. **`PDO`(Points to Double the Odds)**：该违约概率翻倍的评分，即
`Odds`（坏好比）变成2倍时，所减少的信用分。

解出$A$和$B$:

$$
\begin{aligned}
Base\\_score & = A - B\times ln(Odds_0), \\\\
Base\\_score - PDO & = A - B\times ln(2Odds_0)\\\\
B & = \frac{PDO}{ln2} \\\\
A & = Base\\_score + B\times ln(Odds_0) \\\\
\end{aligned}
$$

在实际的应用中，我们会计算出每个变量的各分箱对应的分值。
新用户产生时，对应到每个分箱的值，将这些值相加，最后加上初始基础分，
得到最终的结果。

$$
Score = A - B{\theta_0 + \theta_1x_1 + ... + \theta_nx_n}
$$

式中：变量 $x_1,\ ...,\ x_n.$ 是出现在最终模型的入模变量。
由于所有的入模变量都进行了`WOE`编码，可以将这些自变量中的每一个都写 
$(\theta_iw_{ij})\delta_{ij}$ 的形式：

$$ 
f(x)=A-B
\begin{cases}
\theta_0 \\\\
+(\theta_1 w_{11})\delta_{11}+(\theta_1w_{12})\delta_{12}+... \\\\
+(\theta_n w_{n1})\delta_{n1}+(\theta_nw_{n1})\delta_{n1}+... \\\\
\end{cases}
$$

其中，$A-B\theta_0$为基础分数，$\theta_i$为逻辑回归中第$i$个自变量的系数，
$w_{ij}$为第$i$个变量的第$j$个分箱的`WOE`值，$\delta_{ij}$是`0，1`逻辑变量，
当$\delta_{ij}$代表自变量$i$取第$j$个分箱，当$\delta_{ij}$代表自变量$i$不取第$j$个分箱。
最终得到评分卡模型：

|变量|分箱类别|分值|
|----|----|----|
|基准分|\\|$A-B\theta_0$|
|$x_1$|1|$-B\theta_1w_{11}$|
|$x_1$|2|$-B\theta_1w_{12}$|
|$x_1$|...|...|
|$x_1$|$k_i$|$-B\theta_1w_{1k_i}$|
|$x_2$|1|$-B\theta_{2}w_{21}$|
|$x_2$|2|$-B\theta_{2}w_{22}$|
|$x_2$|...|...|
|$x_2$|$k_2$|$-B\theta_{2}w_{2k_2}$|
|...|...|...|
|$x_n$|1|$-B\theta_{n}w_{n1}$|
|$x_n$|2|$-B\theta_{n}w_{n2}$|
|$x_n$|...|...|
|$x_n$|$k_n$|$-B\theta_{n}w_{nk_n}$|

从以上公式中，我们发现每个分箱的评分都可以表示为 $-B(\theta_iw_{ij})$，
也就是说影响每个分箱的因素包括三部分，分别为参数 $B$，变量系数 $\theta_i$，
和对应分箱的`WOE`编码 $w_{ij}$。


> 📚 Reference


> Editor&Coding: Chensy
