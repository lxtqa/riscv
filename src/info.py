import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# 创建一些示例数据

value = np.array([0,0,0,0,0,0,0,0,0,0,0,0])



with open('./versions_diff_block.json', 'r') as json_file:
    versions = json.load(json_file)
    for version in versions:
        for type in version["contents"]:
            flag = False
            for arc in type:
                if "riscv" in arc["file"] or "Riscv" in arc["file"] or "RISCV" in arc["file"]:
                    flag = True
                    break
            if flag:
                value[len(type)] = value[len(type)] + 1

#[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
#所有
#[0, 0, 1514, 523, 254, 223, 149, 196, 157, 391, 138]
#包含riscv
#[  0,   0, 262, 213, 151, 126,  98, 154,  74, 384, 138]

#= [0, 0, 3028, 1569, 1016, 1115, 894, 1372 ,1256, 3519, 1380]

#= [0, 0, 524，639, 604, 630, 588, 1078, 592, 3456, 1380]
data = pd.DataFrame({
    'Category': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10','11'],
    'Values': value
})


