import os
from tqdm import tqdm
import json
from extract_block import extract_block
from disjoint_sets import find_disjoint_sets
from utils.arch_utils import *
from utils.patch_utils import *
from utils.version_hash import versions

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
    current_directory = "."
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

    chart = []

    for block_set in result:
        file_type = remove_archwords(block_set[0][0])
        content = []
        files = ["" for _ in range(10)]

        for file in block_set[0]:
            if has_archwords(file) == "riscv":
                with open(file,"r") as f:
                    files[2] = f.read()
                    files[3] = files[2]
            else:
                with open(file,"r") as f:
                    files[arch_dic[has_archwords(file)]] = f.read()

        for blocks in block_set[1]:
            lst = [[] for _ in range(10)]
            for block in blocks:
                if has_archwords(block["file"]) == "riscv":
                    lst[2]=block["content"]
                    lst[3]=block["content"]
                else:
                    lst[arch_dic[has_archwords(block["file"])]]=block["content"]
            content.append(lst)
        chart.append([file_type,files,content])


    os.system("git -c advice.detachedHead=false checkout main")
    os.chdir("..")
    return chart


if __name__ == "__main__":
    for version_hash in versions:
        result = split_block(version_hash)
        if not os.path.exists("match"):
            os.mkdir("match")
        with open('match/match_'+version_hash+'.json', 'w') as json_file:
            json.dump(result,json_file,indent=4)