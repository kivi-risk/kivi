
### 2. `CSI` (Characteristic Stability Index)

**特征稳定性指标，用来衡量特征层面的变化。**当评分卡主模型分数发生变化时，
对每个特征计算CSI，可以知道哪些特征分布发生变化从而导致的评分卡主模型分数偏移
以及哪个特征对模型得分变化的影响最大。因此监控特征的CSI指标可以在评分卡主模型发生偏移时快速定位问题。
一般来说，特征层面的监控既包含了PSI，也包含了CSI。

> 公式: 

$$
CSI = \sum_{i=1}^{n}(Actual_i\\%-Expected_i\\%)Score_i
$$

> 计算步骤: 
1. 以训练样本作为预期分布(`Excepted`)，根据评分卡主模型训练过程中每个特征的分箱阈值，
对预期样本进行分箱，得到每箱样本占比（该箱样本数/总样本数）。
2. 按预期分布分箱阈值对实际分布(`Actual`)进行分箱，计算每箱样本占比。
3. 按公式 **(实际占比-预期占比)*每箱得分** 计算每箱的分数偏差。
4. 累加每箱的分数偏差得到最后的`CSI`。

> 注意: 

- `不同变量之间的CSI是不可比的：`由CSI的计算公式可知，影响其计算结果的因素除了特征分布的变化外，还包括特征对主模型得分的“贡献”。
例如，对于变量A和B，变量A对主模型的贡献远大于变量B，这会导致变量A分布的轻微变化时的CSI可能也远大于变量B分布发生巨大变化时的CSI。
- 因为CSI的计算涉及特征不同分箱的得分，因此该指标并不适用于一般的机器学习模型（树模型等）。
- 在评分卡的训练过程中，特征每个分箱的得分往往存在有正有负，这对CSI的计算没有影响。
- 每个分箱计算得到的分数偏差的绝对值，反映了该特征当前分箱分布的变化对模型整体分数的影响。
当该特征的`CSI为正`时，则表明该特征分布变化使模型得分往`高分偏移`，当`CSI为负时，则相反`。

## 特征稳定性指标 - CSI

`CSI` (Characteristic Stability Index)


---

- [1] [风控模型—群体稳定性指标(PSI)深入理解应用](https://zhuanlan.zhihu.com/p/79682292)
- [2] [评分卡模型监控（一）PSI & CSI](https://zhuanlan.zhihu.com/p/94619990)