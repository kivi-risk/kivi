```python
from kivi import Model

dataSet = [[1, 3, 4], [2, 3, 5], [1, 2, 3, 5], [2, 5]]
apriori = Model.Apriori(dataSet, minSupport=0.5, ruleSupport=0.5)

apriori.rules
```