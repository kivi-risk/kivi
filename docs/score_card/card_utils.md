----

### 1. 权重分数转换

> 参数

- `:param df_woeval:` 指标经过 WOE 转换的分数值。
- `:param df_param:` 指标的权重。
- `:param weight_name:` 权重的名称。
- `:param target_name:` 标签的名称。
- `:param reset_index:` 重置 index。
- `:param score_border:` 分值的值域。
- `:return:` `df_score[['score', 'target']]`

> 示例

```python
model_score_by_weight(df_val, params, score_border=[300, 700])
```

<center>
    <figure class="half">
        <img src="./img/score_dist.png" height="260">
        <img src="./img/score_roc.png" height="260">
    </figure>
    <br>
    <div style="color:orange; border-bottom: 1px solid #d9d9d9;
    display: inline-block;
    color: #999;
    padding: 2px;">上图左为分数分布，右为分数的效果评估</div>
</center>

### 2. 对数分数转换

> 参数

```python

```


