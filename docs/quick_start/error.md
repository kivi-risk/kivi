-----
## 1. 代码执行注意事项

1. 要确认跑数文件的文件名称、文件版本、文件时间等信息。
2. 要确认跑数过程中会使用到的原始表，中间表，输出表；尤其是输出表是否会覆盖其他数据，数据的修改、保存、覆盖、删除一定要慎重。
3. 要确认反馈输出的数据内容，分析数据是否正确符合预期。

## 2. 代码异常排查

### 2.1 代码报错

1. **要区分三方包代码错误，还是自己的代码错误，一般需要定位找到我们自己代码最后一层异常的地方就可以解决问题了。**
2. 一般代码问题只涉及到`Jupyter脚本`层面，最多涉及到`.py`层面，涉及到`包/库`层面的问题会非常少，修改起来相对也比较麻烦。

> **Jupyter 中的脚本异常**

<img src="/img/error_0.png">

> **.py 文件中的异常**

<img src="/img/error_1.png">

上图中，代码引用了`functions.py`中的`fun`函数，涉及到两个地方的报错，

1. 第一，指向了`fun`函数。
2. 第二，指向了`functions.py`文件中定义的`fun`函数，并且指向了该文件的第`3`行。
3. 最终，错误定位为输入数据的数据类型不符合要求，即`'1'`是字符串类型，不是`int`类型。

> **包/库(pkg) 的异常**

<img src="/img/error_2.png">

这里引用了`kivi`库，可以看到报错的路径中有`lib\site-packages\kivi\`，一般出现`site-packages`说明，该位置提示的是第三方库报错的地方，
一般第三方库存在问题的可能性很小，排查问题排查到这一层一般就可以了。

> **自定义函数 UDF 的异常**

```python
@F.udf(returnType=DoubleType())
def udf_operator_div(num, den):
    if ((num is None) or (num == 0)) and ((den is None) or (den == 0)):
        return num / den
    elif ((den is None) or (den == 0)):
        return -9999.
    elif num is None:
        return -1111.
    else:
        return num / den

data = [(None, 1), (1, 1), (None, None), (0, 0), (0, 1), (0, None), (1, None), (1, 0)]
df = spark.createDataFrame(data, schema=['num', 'den'])
df = df.withColumn('div', udf_operator_div(F.col('num'), F.col('den')))
df.show()
```

**如果，我们定义了一个`UDF`函数，出现问题了某些时候不一定会在`Jupyter`前端显示全部真实的报错信息。需要去`spark-ui-stages`中去查看具体`UDF`定义是哪里的问题。**

*第一步，找到spark-ui-stages*

<img src="/img/error_3.png">

*第二步，找到出错误的`stage`的具体报错信息，并找到有关`UDF`的提示。一般有关`UDF`的提示会提示位置是`ipython kernel 或 .py 或 pkg`*

<img src="/img/error_4.png">

### 2.2 性能排查

> hadoop UI 中的进程资源占用查看

<img src="./img/hadoop_app_0.png" width="1280px">

> spark UI 中的进程资源查看

*spark ui jobs*

<img src="./img/spark_ui_0.png" width="1280px">

*spark ui stages: 一个`spark job`会有多个`spark stage`*

<img src="./img/spark_ui_1.png" width="1280px">

**重点需要查看`Job`或者`Stage`是否有失败的地方（`Failed`），或者运行较为卡顿。**

## 3. 数据异常排查

### 3.1 无数据或数据量异常大

1. 首先，排查数据中间表的数据量，按月或按某维度进行数据量的统计，看是否有异常。
2. 然后，排查数据代码中涉及数据过滤条件的`PySpark DataFrame`的数据量。

## 4. 数据修改原则

1. 在做任何试探性修改时，需要保留原来的计算表，尽量不去覆盖原来的表；在修改前后要对比两个表的差异，看是否修改时恰当的符合预期的。
   - 如，修改了数据的聚合范围，修改了跑数周期，修改了某些关联条件、数据过滤条件等。
   - 如，有一张样本表`t_cch_sample_v1`；修改了部分的筛选条件后，再跑数时将表名进行一定的修改`t_cch_sample_v2`，然后严格对比修改前后的区别。
2. 修改分区数据时，应注意是修改的全表，还是仅修改了某分区。


