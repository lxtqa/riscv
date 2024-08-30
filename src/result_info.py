import json

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

# 创建一些示例数据


value = np.array([0,0,0,0,0,0,0,0,0,0])
num = np.array([0,0,0,0,0,0,0,0,0,0])

with open('result/result12.json', 'r') as json_file:
    results = json.load(json_file)
    for result in results:
        for i,v in enumerate(result):
            if v == 1:
                value[i] = value[i]+1
                num[i] = num[i]+1
            if v == -1:
                num[i] = num[i]+1
    for i,v in enumerate(value):
        if num[i]!=0:
            print(value[i]/num[i])
        else:
            print(0)
