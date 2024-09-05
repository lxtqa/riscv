import subprocess
import re
import tempfile
from tqdm import tqdm
import json
from utils.arch_utils import *
from utils.patch_utils import *

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



def split_diff_lines_to_json(lines,file_lines):


    block_header_indices = [0]
    header_re = r"^((::[\[:space:]]*)?[A-Za-z_].*)$"
    for i,line in enumerate(file_lines):
        if re.match(header_re,line):
            block_header_indices.append(i)
    block_header_indices.append(INF)

    block_start_indices = []
    current_pointer = 0
    for i, line in enumerate(lines):
        if line.startswith('@@'):
            new_start, _ = start_line(line)
            flag = 0
            while new_start > block_header_indices[current_pointer]:
                current_pointer = current_pointer + 1
                flag = 1
            if flag:
                block_start_indices.append([i,block_header_indices[current_pointer-1]])

    if not block_start_indices:
        print("No blocks found in the diff file.")
        return []
    block_start_indices.append([len(lines),""])  # Add end index for the last block

    blocks = []
    for i in range(len(block_start_indices) - 1):
        block_lines = lines[block_start_indices[i][0]:block_start_indices[i + 1][0]]
        if re.match(header_re,block_lines[1][1:]):
            header = block_lines[1][1:]
        else:
            header  = file_lines[block_start_indices[i][1]]
        blocks.append({
                    "header": header,
                    'patch': block_lines
                })

    return blocks



def collect_parallel_blocks(commit_diffs):
    """
    整合commit下多个文件的所有blocks, 找到所有平行的blocks并返回一个JSON对象。
    :param commit_diffs: 字典, 键为文件路径, 值为文件的diff内容列表。
    :return: JSON对象, 包含所有平行的blocks信息。
    """
    all_blocks = []
    # 收集所有文件的blocks
    for file_path, blocks in commit_diffs:
        for block in blocks:
            block['file'] = file_path
        all_blocks.extend(blocks)

    parallel_blocks_groups = []

    #首先过一遍纯name的检查，然后再进行header的检查
    #先检查同文件内是否有相同name的函数，如果没有，则直接认为name相同即为para
    #如果有则比较block
    # 判断平行的条件：file平行且不同，

    # 找到所有平行的blocks

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

    visited = [False] * len(all_blocks)
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
                    merged_dict[key]['patch'].extend(item['patch'])
                else:
                    # 如果这个键不存在，直接添加到合并字典中
                    merged_dict[key] = item
            # 将合并结果转换回列表格式
            if len(list(merged_dict.values())) > 1:
                parallel_blocks_groups.append(list(merged_dict.values()))

    return parallel_blocks_groups




def get_commits(adjacent_version):

    result = subprocess.run(["git","log","--format=%H","--decorate" ,adjacent_version[0]+".."+adjacent_version[1]],cwd="./v8", stdout=subprocess.PIPE)
    output = result.stdout.decode('utf-8', errors='ignore')
    commits = output.split("\n")
    while "" in commits:
        commits.remove("")
    return commits



def get_file(commit_hash,file_path):
    try:
        subprocess.run(
            ["git", "cat-file", "-e", f"{commit_hash}:{file_path}"],
            check=True,
            cwd="./v8",
            stderr=subprocess.DEVNULL
        )
        code = subprocess.run(["git","show",commit_hash+":"+file_path],cwd="./v8", stdout=subprocess.PIPE)
        code = format(code.stdout.decode('utf-8', errors='ignore'))
        return code
    except subprocess.CalledProcessError:
        return None


if __name__ == "__main__":
    versions_diff = []
    for i in range(len(versions)-1):
        result = subprocess.run(["git","diff","-U0",versions[i],versions[i+1]],cwd="./v8", stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8', errors='ignore')
        patch = output.split("\n")
        filtered_patchs ={"versions":[versions[i],versions[i+1]],"commits":[],"contents":[]}
        contents = []
        filtered_patch = []
        ###
        for line in patch:
            filename = re.findall(r"^diff --git a/(.+) b/(.+)$",line)
            if filename != []:
                    tmp_filename = filename[0][0]
                    if has_archwords(tmp_filename) and (tmp_filename.endswith(".cc") or tmp_filename.endswith(".h")):
                            old_code = get_file(versions[i],tmp_filename)
                            new_code = get_file(versions[i+1],tmp_filename)
                            if old_code == None or new_code == None:
                                continue
                            with tempfile.NamedTemporaryFile(delete=True, mode='w', suffix='.cpp') as old_temp, \
                                    tempfile.NamedTemporaryFile(delete=True, mode='w', suffix='.cpp') as new_temp:

                                    old_temp.write(old_code)
                                    old_temp.flush()
                                    new_temp.write(new_code)
                                    new_temp.flush()

                            # 使用 git diff 比较两个临时文件
                                    result = subprocess.run(
                                        ["git", "diff","--no-index", "-U0", old_temp.name, new_temp.name],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE
                                    )
                                    blocks = split_diff_lines_to_json(result.stdout.decode().split("\n"),old_code.split("\n"))
                                    contents.append([tmp_filename,blocks])

        ###
        if contents != []:
            filtered_patchs["commits"] = get_commits([versions[i],versions[i+1]])
            filtered_patchs["contents"] = collect_parallel_blocks(contents)
            versions_diff.append(filtered_patchs)
    with open("./versions_diff_block.json","w") as f:
        json.dump(versions_diff,f,indent=4)