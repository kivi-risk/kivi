# Quick Start

## 安装使用

```bash
# [推荐] 安装最新版本ZLAI的所有模块
pip install kivi[all] -U
# [补充] 增加了一些 nlp 内容
pip install kivi[jieba] -U
# [补充] 增加了一些 pyspark 内容
pip install kivi[pyspark] -U
```

## 内置数据

```python
from kivi.datasets import Dataset

ds = Dataset()
df_bank = ds.bank_data()
print("bank data shape: ", df_bank.shape)

ds = Dataset()
df_crime = ds.crime_data()
print("crime data shape: ", df_crime.shape)
```

*输出*

```text
bank data shape: (4521, 17)
crime data shape: (51, 7)
```

**kivi**中内置了两份二分类数据，作为测试或者学习使用。

## 数据分析

### pyspark

1. [pyspark 相关表操作](./SparkSupport/SparkSupport): 表的增删改查，获取`spark session`等。
1. [pyspark 列操作](./descriptive_statistics/data_analysis?id=_1-pyspark中的列操作): `pyspark dataframe` 的各类列运算，列操作，列混合操作。
1. [分布分析](./descriptive_statistics/data_analysis?id=_2-分布分析): 分位数计算、排名计算、分布统计量。
1. [空值分析](./descriptive_statistics/data_analysis?id=_3-空值分析): `Nan`与`Null`的区别，空值的一般注意事项，时间数据操作过程中产生空值的原因。
1. [表转置操作](./descriptive_statistics/data_analysis?id=_4-表转置操作): 长表宽表的互相转换。

## 分箱分析

> 分箱API

| 分箱类型  | 方法              | 分箱名称              |
|-------|-----------------|-------------------|
| 无监督分箱 | `DistanceBins`  | 等距分箱              |
| 无监督分箱 | `FrequencyBins` | 等频分箱              |
| 无监督分箱 | `Category`      | 类别型分箱             |
| 无监督分箱 | `KmeansBins`    | Kmeans 分箱         |
| 无监督分箱 | `CutOffPoint`   | 模式): 手动指定分箱模式     |
| 有监督分箱 | `Pearson`       | Pearson 分箱        |
| 有监督分箱 | `TreeBins`      | : 决策树分箱           |
| 有监督分箱 | `KSMerge`       | S分箱): `Best-KS`分箱 |
| 有监督分箱 | `Chi2Bins`      | 卡方分箱              |

> 批量分箱及其他辅助方法

1. [`WOE.WOEBatch`](./woe_iv/woe_embedding?id=_1-woe-计算批量化): `WOE` 计算批量化
1. [`WOE.WOEBatchWithRebin`](./woe_iv/woe_embedding?id=_2-WOE-计算批量化并进行自动合并分箱): `WOE` 计算批量化并进行自动合并分箱
1. [`WOE.SaveWOEVal`](./woe_iv/woe_embedding?id=_3-Woe-赋分方法): `Woe` 赋分方法
1. [`WOE.TransToWOEVal`](./woe_iv/woe_embedding?id=_4-Woe-Batch-赋分方法): Woe-Batch 赋分方法
1. [`WOE.Rebins`](./woe_iv/woe_embedding?id=_5-手动分箱尝试): 手动分箱尝试
1. [`WOE.AppendRebinWoe`](./woe_iv/woe_embedding?id=_6-合并手动分箱结果): 合并手动分箱结果


## 样本建设

1. [样本建设的概念](./score_card/sample): 样本建设的基本概念，需要注意的事项，样本的存储等。

## 回归诊断

### 相关系数

> [`spearmanr`](./feature_select/mutivar?id=_1-相关系数-spearman): 相关系数 `spearman`

### 共线性诊断

1. [`VIF.vif`](http://localhost:3000/#/feature_select/mutivar?id=_212-vifvif-计算某变量与其他变量的vif): 计算某变量与其他变量的`VIF`
1. [`VIF.StatsTableVIF`](http://localhost:3000/#/feature_select/mutivar?id=_213-vifstatstablevif-依次计算全表vif): 依次计算全表`VIF`
1. [`VIF.LowVIFFeatures`](http://localhost:3000/#/feature_select/mutivar?id=_214-viflowviffeatures-依据vif设定阈值，选择最小vif特征组合): 依据`VIF`设定阈值，选择最小`VIF`特征组合

## 5. 指标与模型的评估

### 5.1 区分效果评估

1. [`LIFT`](./model_select/model_eval?id=_1-lift): LIFT，评估指标或者分数的提升度
1. [`lift_compare`](./model_select/model_eval?id=_2-lift_compare): lift_compare，评估指标或者不同数据集分数的lift
1. [`绘制ROC图`](./model_select/model_eval?id=_3-绘制ROC图): 绘制`ROC`图，并标注`AUC`与`KS`
1. [`AUC`和`KS`](./model_select/model_eval?id=_4-AUC-和-KS): 输出预测值与真实值的 `AUC` 和 `KS`
1. [`PR曲线`]()

### 稳定性评估

1. [`PSI`](./feature_select/PSI-CSI?id=群体稳定性指标-psi)
1. [`CSI`](./feature_select/PSI-CSI?id=特征稳定性指标-csi) 

### 评分卡分数转换

> 

-----
