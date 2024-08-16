import json

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

# 创建一些示例数据

value = np.array([0,0,0,0,0,0,0,0,0,0,0])



with open('./versions_diff_hunk.json', 'r') as json_file:
    functions = json.load(json_file)
    for version in functions:
        for type in version["contents"]:
            if len(type) == 9:
                a = 0
            value[len(type)] = value[len(type)] + 1

#[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
#修改前
#[0, 0, 1521, 512, 248, 230, 162, 202, 146, 301, 114]

#修改后
#[0, 0, 1506, 502, 261, 227, 170, 205, 147, 314, 127]
#[0, 0, 1514, 523, 254, 223, 149, 196, 157, 391, 138]

#= [0, 0, 3012, 1506, 1044, 1135, 1020, 1435, 1176, 2826, 1270]
#= [0, 0, 3028, 1569, 1016, 1115, 894, 1372 ,1256, 3519, 1380]
data = pd.DataFrame({
    'Category': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10'],
    'Values': value
})

# 设置Seaborn的样式
sns.set(style="whitegrid")

# 创建子图
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# 1. 柱状图
sns.barplot(x='Category', y='Values', data=data, ax=axes[0], palette='Blues_d')
axes[0].set_title('Bar Chart')



# 显示图表
plt.tight_layout()
plt.show()

