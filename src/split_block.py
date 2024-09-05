import os
from tqdm import tqdm
import json
from extract_block import extract_block
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


def split_block(version_hash):
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
        all_blocks = []
        for file_name in disjoint_set:
            with open(file_name,"r") as f:
                content = f.read()
                all_blocks += extract_block(format(content).split("\n"),file_name)

        visited = [False] * len(all_blocks)

        parallel_blocks_groups = []
        same_named = [False] * len(all_blocks)
        for i in range(len(all_blocks)):
            if same_named[i]:
                continue
            name1 = extract_name(all_blocks[i]['header'])
            if name1 == None:
                continue
            for j in range(i+1,len(all_blocks)):
                if all_blocks[i]['file'] != all_blocks[j]['file']:
                    continue
                name2 = extract_name(all_blocks[j]['header'])
                if name2 == None:
                    continue
                if remove_whitespace(name1) == remove_whitespace(name2) \
                    and remove_whitespace(all_blocks[i]['header']) != remove_whitespace(all_blocks[j]['header']):
                    same_named[i],same_named[j] = True, True
        for i in range(len(all_blocks)):
            if visited[i]:
                continue
            parallel_group = [all_blocks[i]]
            visited[i] = True
            if same_named[i]:
                block_header1 = all_blocks[i]['header']
                for j in range(i + 1, len(all_blocks)):
                    block_header2 = all_blocks[j]['header']
                    if isfilepara(all_blocks[i]['file'], all_blocks[j]['file']) and isblockpara(block_header1, block_header2):
                        parallel_group.append(all_blocks[j])
                        visited[j] = True
            else:
                block_name1 = extract_name(all_blocks[i]['header'])
                block_header1 = all_blocks[i]['header']
                for j in range(i + 1, len(all_blocks)):
                    block_name2 = extract_name(all_blocks[j]['header'])
                    if block_name1 != None and block_name2 != None and not same_named[j]:
                        if isfilepara(all_blocks[i]['file'], all_blocks[j]['file']) and isblockpara(block_name1, block_name2):
                            parallel_group.append(all_blocks[j])
                            visited[j] = True
                    else:
                        block_header2 = all_blocks[j]['header']
                        if isfilepara(all_blocks[i]['file'], all_blocks[j]['file']) and isblockpara(block_header1, block_header2):
                            parallel_group.append(all_blocks[j])
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
                    parallel_blocks_groups.append(list(merged_dict.values()))

        result.append([disjoint_set,parallel_blocks_groups])

    arch_dic = {"arm":0,"arm64":1,"riscv32":2,"riscv64":3,"mips":4,"ia32":5,"x64":6,"loong":7,"s390":8,"ppc":9}
    chart = []

    for block_set in result:
        file_type = remove_archwords(block_set[0][0])
        content = []
        for blocks in block_set[1]:
            lst = [[] for _ in range(10)]
            for block in blocks:
                if has_archwords(block["file"]) == "riscv":
                    lst[2]=block["content"]
                    lst[3]=block["content"]
                else:
                    lst[arch_dic[has_archwords(block["file"])]]=block["content"]
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
        result = split_block(version_hash)
        if not os.path.exists("match"):
            os.mkdir("match")
        with open('match/match_'+version_hash+'.json', 'w') as json_file:
            json.dump(result,json_file,indent=4)