import os
from tqdm import tqdm
import json
from extract_hunk import extract_hunk
from disjoint_sets import find_disjoint_sets
from utils.arch_utils import *
from utils.patch_utils import *

def list_files(directory):
    files = []
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith('.cc') or filename.endswith('.h'):
                files.append(os.path.join(root, filename))
    return files


def split_hunk(version_hash):
    dir = "./v8"
    os.chdir(dir)
    current_directory = "./src"
    os.system("git -c advice.detachedHead=false  checkout "+version_hash)
    cc_h_files = list_files(current_directory)
    file_list = []

    for file in cc_h_files:
        if has_archwords(file):
            file_list.append(file)


    disjoint_sets = find_disjoint_sets(file_list, isfilepara)
    _ = []

    for disjoint_set in disjoint_sets:
        if len(disjoint_set) > 1:
            _.append(disjoint_set)
    disjoint_sets = _

    result = []

    for disjoint_set in tqdm(disjoint_sets):
        all_hunks = []
        for file_name in disjoint_set:
            with open(file_name,"r") as f:
                content = f.read()
                all_hunks += extract_hunk(format(content).split("\n"),file_name)

        visited = [False] * len(all_hunks)

        parallel_hunks_groups = []
        same_named = [False] * len(all_hunks)
        for i in range(len(all_hunks)):
            if same_named[i]:
                continue
            name1 = extract_name(all_hunks[i]['header'])
            if name1 == None:
                continue
            for j in range(i+1,len(all_hunks)):
                if all_hunks[i]['file'] != all_hunks[j]['file']:
                    continue
                name2 = extract_name(all_hunks[j]['header'])
                if name2 == None:
                    continue
                if remove_whitespace(name1) == remove_whitespace(name2) \
                    and remove_whitespace(all_hunks[i]['header']) != remove_whitespace(all_hunks[j]['header']):
                    same_named[i],same_named[j] = True, True
        for i in range(len(all_hunks)):
            if visited[i]:
                continue
            parallel_group = [all_hunks[i]]
            visited[i] = True
            if same_named[i]:
                hunk_header1 = all_hunks[i]['header']
                for j in range(i + 1, len(all_hunks)):
                    hunk_header2 = all_hunks[j]['header']
                    if isfilepara(all_hunks[i]['file'], all_hunks[j]['file']) and ishunkpara(hunk_header1, hunk_header2):
                        parallel_group.append(all_hunks[j])
                        visited[j] = True
            else:
                hunk_name1 = extract_name(all_hunks[i]['header'])
                hunk_header1 = all_hunks[i]['header']
                for j in range(i + 1, len(all_hunks)):
                    hunk_name2 = extract_name(all_hunks[j]['header'])
                    if hunk_name1 != None and hunk_name2 != None and not same_named[j]:
                        if isfilepara(all_hunks[i]['file'], all_hunks[j]['file']) and ishunkpara(hunk_name1, hunk_name2):
                            parallel_group.append(all_hunks[j])
                            visited[j] = True
                    else:
                        hunk_header2 = all_hunks[j]['header']
                        if isfilepara(all_hunks[i]['file'], all_hunks[j]['file']) and ishunkpara(hunk_header1, hunk_header2):
                            parallel_group.append(all_hunks[j])
                            visited[j] = True
            #判断parallel_group中是否存在相同的，如果相同，则合并
            if len(parallel_group) > 1:
                merged_dict = {}

                for item in parallel_group:
                    key = (item['header'], item['file'])

                    if key in merged_dict:
                        # 假设 'value' 字段是一个列表，进行合并
                        merged_dict[key]['content'].extend(item['content'])
                    else:
                        # 如果这个键不存在，直接添加到合并字典中
                        merged_dict[key] = item
                # 将合并结果转换回列表格式
                if len(list(merged_dict.values())) > 1:
                    parallel_hunks_groups.append(list(merged_dict.values()))

        result.append([disjoint_set,parallel_hunks_groups])

    arch_dic = {"arm":0,"arm64":1,"riscv32":2,"riscv64":3,"mips":4,"ia32":5,"x64":6,"loong":7,"s390":8,"ppc":9}
    chart = []

    for hunk_set in result:
        file_type = remove_archwords(hunk_set[0][0])
        content = []
        for hunks in hunk_set[1]:
            lst = [[] for _ in range(10)]
            for hunk in hunks:
                if has_archwords(hunk["file"]) == "riscv":
                    lst[2]=hunk["content"]
                    lst[3]=hunk["content"]
                else:
                    lst[arch_dic[has_archwords(hunk["file"])]]=hunk["content"]
            content.append(lst)
        chart.append([file_type,content])


    os.system("git -c advice.detachedHead=false  checkout main")
    os.chdir("..")
    return chart


if __name__ == "__main__":
    versions = ["519ee9d66cd", # 9.10.0
        "dc97b450587", # 10.0
        "d571cf7c2f4", # 10.1.0
        "a0204ff9aea", # 10.2.0
        "01af3a6529a", # 10.3.0.1
        "24226735269", #10.4.0.1
        "e9d54c53d14", #10.5.0.2
        "6df7f9e416d", # 10.6.0
        "cfe9945828d", # 10.7.0
        "78dc1fc670f", #10.8.0
        "5be28a22d10", #10.9.0
        "d7f28a43690", # 11.0.0
        "5b84df0b994", # 11.1.0
        "d60b62b0afb", # 11.2.0
        "49a080e6ff5", # 11.3.0
        "6038c5bb8a8", # 11.4.0
        "ae4d3975ab0", # 11.5.0
        "6dcdb718b6d", # 11.6.0
        "2dcf2bc02cc", # 11.7.0
        "78017dccc38", # 11.8.0
        "8997fd159a8", # 11.9.0
        "ef0e120e97a", # 12.0.0
        "811b7e772fa", # 12.1.0
        "3130a66a9d9", # 12.2.0
        "40d669e1505", # 12.3.0
        "8ddb5aeb866", # 12.4.0
        "6c1c3de6422", # 12.5.0
        "a56fcee3ed5", # 12.6.0
        "ca4889a4ab8", # 12.7.0
        "4699435f7bb", # 12.8.0
        "70ccb6965dd", # 12.9.0
        ]
    for version_hash in versions:
        result = split_hunk(version_hash)
        if not os.path.exists("match"):
            os.mkdir("match")
        with open('match/match_'+version_hash+'.json', 'w') as json_file:
            json.dump(result,json_file,indent=4)