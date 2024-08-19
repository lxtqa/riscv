import os
from tqdm import tqdm
from utils.ast_utils import get_type
import json
import re
from disjoint_sets import find_disjoint_sets
from utils.arc_utils import *
from utils.patch_utils import *

def bfs_search_function(root):
    queue = [root]
    results = []
    while queue:
        node = queue.pop(0)
        if get_type(node.value) == "function":
            results.append(node)
        else:
            queue.extend(node.children)
    return results

def bfs_get_num(root):
    queue = [root]
    num = 0
    while queue:
        node = queue.pop(0)
        queue.extend(node.children)
        num = num + 1
    return num

def list_files(directory):
    files = []
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith('.cc') or filename.endswith('.h'):
                files.append(os.path.join(root, filename))
    return files

def split_hunk(file_lines,file_name):
    hunk_header_indices = [0]
    header_re = r"^((::[[:space:]]*)?[A-Za-z_].*)$"
    for i,line in enumerate(file_lines):
        if re.match(header_re,line):
            hunk_header_indices.append(i)
    hunk_header_indices.append(INF)

    hunks = []
    for i in range(len(hunk_header_indices) - 1):
        hunk_lines = file_lines[hunk_header_indices[i]:hunk_header_indices[i + 1]]
        hunks.append({
                    "header": file_lines[hunk_header_indices[i]],
                    "content": hunk_lines,
                    "file": file_name
                })
    return hunks



if __name__ == "__main__":
    current_directory = "./v8/src"
    cc_h_files = list_files(current_directory)
    file_list = []

    for file in cc_h_files:
        if has_arcwords(file):
            file_list.append(file)


    disjoint_sets = find_disjoint_sets(file_list, isfilepara)
    _ = []

    for disjoint_set in disjoint_sets:
        if len(disjoint_set) > 1:
            _.append(disjoint_set)
        else:
            a= 0
    disjoint_sets = _

    result = []

    for disjoint_set in tqdm(disjoint_sets):
        all_hunks = []
        for file_name in disjoint_set:
            with open(file_name,"r") as f:
                content = f.read()
                all_hunks += split_hunk(format(content).split("\n"),file_name)

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

    with open('match.json', 'w') as json_file:
        json.dump(result,json_file,indent=4)
