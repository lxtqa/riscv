import json
import numpy as np

# 创建一些示例数据

current = 29

for k in range(current):
    print('result'+str(k)+'.json')
    value = np.array([0,0,0,0,0,0,0,0,0,0])
    num = np.array([0,0,0,0,0,0,0,0,0,0])
    try:
        with open('result/result'+str(k)+'.json', 'r') as json_file:
            results = json.load(json_file)
            for result in results:
                for i,v in enumerate(result):
                    if v == 1:
                        value[i] = value[i]+1
                        num[i] = num[i]+1
                    if v == -1:
                        num[i] = num[i]+1
            for i,v in enumerate(value):
                print(format(num[i]),end=" ")
            print()
            for i,v in enumerate(value):
                if num[i]!=0:
                    print(format(value[i]/num[i],".2f"),end=" ")
                else:
                    print(format(0,".2f"),end=" ")
            print()
        value = np.array([0,0,0,0,0,0,0,0,0,0])
        num = np.array([0,0,0,0,0,0,0,0,0,0])
        with open('result/result'+str(k)+'__.json', 'r') as json_file:
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
                    print(format(value[i]/num[i],".2f"),end=" ")
                else:
                    print(format(0,".2f"),end=" ")
            print()
    except:
        pass


# value = np.array([0,0,0,0,0,0,0,0,0,0])
# num = np.array([0,0,0,0,0,0,0,0,0,0])
# for i in range(current):
#     with open('result/result'+str(i)+'.json', 'r') as json_file:
#         results = json.load(json_file)
#         for result in results:
#             for i,v in enumerate(result):
#                 if v == 1:
#                     value[i] = value[i]+1
#                     num[i] = num[i]+1
#                 if v == -1:
#                     num[i] = num[i]+1
# for i,v in enumerate(value):
#     if num[i]!=0:
#         print(format(value[i]/num[i],".2f"),end = " ")
#     else:
#         print(format(0,".2f"),end=" ")
# print()
# value = np.array([0,0,0,0,0,0,0,0,0,0])
# num = np.array([0,0,0,0,0,0,0,0,0,0])
# for i in range(current):
#     with open('result/result'+str(i)+'__.json', 'r') as json_file:
#         results = json.load(json_file)
#         for result in results:
#             for i,v in enumerate(result):
#                 if v == 1:
#                     value[i] = value[i]+1
#                     num[i] = num[i]+1
#                 if v == -1:
#                     num[i] = num[i]+1
# for i,v in enumerate(value):
#     if num[i]!=0:
#         print(num[i],end = " ")
# print()
# for i,v in enumerate(value):
#     if num[i]!=0:
#         print(format(value[i]/num[i],".2f"),end = " ")
#     else:
#         print(format(0,".2f"),end=" ")
# print()



for k in range(current):
    with open('result/result'+str(k)+'__.json', 'r') as json_file:
        results = json.load(json_file)
        with open('result/result'+str(k)+'.json', 'r') as json_file:
            results_ = json.load(json_file)
            for i,v in enumerate(results):
                for j,w in enumerate(v):
                    if results[i][j] == 1 and results_[i][j] == -1:
                        a = 0


# for k in range(current):
#         with open('result/result'+str(k)+'.json', 'r') as json_file:
#             results_ = json.load(json_file)
#             for i,v in enumerate(results_):
#                 for j,w in enumerate(v):
#                     if j != 2 and j!= 3:
#                         if results_[i][j] == -1:
#                             print(k,i,j)