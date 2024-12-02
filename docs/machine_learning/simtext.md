## 文本相似度

- **Sim_Cosine**    cosine相似性
- **Sim_Jaccard**   Jaccard相似性
- **Sim_MinEdit**  最小编辑距离
- **Sim_Simple**  微软Word中的track changes

> 中文

```python
from kivi.Model import similarity

text1 = '''
    微风轻轻的一吹让人感觉心旷神怡。这时候太阳藏在云里，我走到一棵大树前，
    大树很高树叶随着风轻轻的飘动着，我停在那里闭上眼睛，抬起头感受着风，那是一种十分奇妙的感觉。
'''
text2 = '''
    这时，我缓缓睁开眼睛突然之间，感觉天空离我很近，大片云朵就在我的头顶不知何时那被藏住的太阳透过云层当中的缝隙撒了下来，
    不知为何，我突然感觉到了希望，那是一种莫名的希望，我就这样呆呆的看着这一幕，可真美呀！
'''

sim = similarity()
sim.compute(text1, text2)
```

> 英文

```python
A = 'We expect demand to increase.'
B = 'We expect worldwide demand to increase.'

sim = similarity()
AB = sim.compute(A, B)

print(AB)
```
