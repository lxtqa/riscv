import matplotlib.pyplot as plt
import numpy as np

# 创建数据
labels = ["arm","arm64","mips","ia32","x64","loong","s390","ppc"]
data1 = [0.41, 0.37, 0.50, 0.38, 0.32, 0.47, 0.47, 0.42] #0.4175
data2 = [0.51, 0.43, 0.58, 0.46, 0.39, 0.55, 0.52, 0.49] #0.49125

x = np.arange(len(labels))  # 标签位置
width = 0.35  # 柱状图的宽度

# 绘制柱状图
fig, ax = plt.subplots()
bar1 = ax.bar(x - width/2, data1, width, label='old method')
bar2 = ax.bar(x + width/2, data2, width, label='new method with replacement')

# 添加标签和标题
ax.set_xlabel('Archs')
ax.set_ylabel('Accuracy')
ax.set_title('Comparison of Two Methods')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()

# 展示图形
plt.show()

