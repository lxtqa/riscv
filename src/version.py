import subprocess
import re
import os
from tqdm import tqdm
import json
from arc_utils import has_arcwords,remove_arcwords
import json
from unit_result import remove_whitespace,read_patch,start_line

INF = 2**31

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

    hunk_header_indices = [0]
    header_re = r"^((::[[:space:]]*)?[A-Za-z_].*)$"
    for i,line in enumerate(file_lines):
        if re.match(header_re,line):
            hunk_header_indices.append(i)

    hunk_header_indices.append(INF)

    hunk_start_indices = []
    current_pointer = 0
    for i, line in enumerate(lines):
        if line.startswith('@@'):
            new_start, _ = start_line(line)
            if new_start > hunk_header_indices[current_pointer]:
                hunk_start_indices.append(i)
            while new_start > hunk_header_indices[current_pointer]:
                current_pointer = current_pointer + 1

    if not hunk_start_indices:
        print("No hunks found in the diff file.")
        return []

    hunk_start_indices.append(len(lines))  # Add end index for the last hunk

    hunks = []
    for i in range(len(hunk_start_indices) - 1):
        hunk_lines = lines[hunk_start_indices[i]:hunk_start_indices[i + 1]]
        hunks.append({
                    'patch': hunk_lines
                })

    return hunks


# 假设isfilepara和ishunkpara函数已经实现
def isfilepara(file1, file2):
    # 实现文件是否平行的逻辑
    return remove_whitespace(remove_arcwords(file1)) == remove_whitespace(remove_arcwords(file2))

def ishunkpara(hunk1, hunk2):
    # 实现hunk是否平行的逻辑
    hunk1 = remove_whitespace(remove_arcwords(hunk1))
    hunk2 = remove_whitespace(remove_arcwords(hunk2))
    if hunk1 == "" or hunk2 == "":
        return hunk1 == hunk2
    if hunk1 == hunk2:
        return True
    if hunk1 in hunk2:
        return True
    if hunk2 in hunk1:
        return True
    return False

def collect_parallel_hunks(commit_diffs):
    """
    整合commit下多个文件的所有hunks, 找到所有平行的hunks并返回一个JSON对象。
    :param commit_diffs: 字典, 键为文件路径, 值为文件的diff内容列表。
    :return: JSON对象, 包含所有平行的hunks信息。
    """
    all_hunks = []
    # 收集所有文件的hunks
    for file_path, hunks in commit_diffs:
        for hunk in hunks:
            hunk['file'] = file_path
        all_hunks.extend(hunks)

    parallel_hunks_groups = []

    # 找到所有平行的hunks
    visited = [False] * len(all_hunks)
    for i in range(len(all_hunks)):
        if visited[i]:
            continue
        parallel_group = [all_hunks[i]]
        visited[i] = True
        for j in range(i + 1, len(all_hunks)):
            hunk_header1 = read_patch(all_hunks[i]['patch'])
            if hunk_header1 == []: hunk_header1 = [""]
            hunk_header2 = read_patch(all_hunks[j]['patch'])
            if hunk_header2 == []: hunk_header2 = [""]
            read_patch(all_hunks[j]['patch'])
            if isfilepara(all_hunks[i]['file'], all_hunks[j]['file']) and ishunkpara(hunk_header1[0], hunk_header2[0]):
                parallel_group.append(all_hunks[j])
                visited[j] = True
        if len(parallel_group) > 1:
            parallel_hunks_groups.append(parallel_group)

    return parallel_hunks_groups




def get_commits(adjacent_version):

    result = subprocess.run(["git","log","--format=%H","--decorate" ,adjacent_version[0]+".."+adjacent_version[1]],cwd="./v8", stdout=subprocess.PIPE)
    output = result.stdout.decode('utf-8', errors='ignore')
    commits = output.split("\n")
    while "" in commits:
        commits.remove("")
    return commits

if __name__ == "__main__":
    versions_diff = []
    for i in tqdm(range(len(versions)-1)):
        result = subprocess.run(["git","diff","-U0",versions[i],versions[i+1]],cwd="./v8", stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8', errors='ignore')
        patch = output.split("\n")
        filtered_patchs ={"versions":[versions[i],versions[i+1]],"commits":[],"contents":[]}
        contents = []
        filtered_patch = []
        tmp_filename = None
        for line in patch:
            filename = re.findall(r"^diff --git a/(.+) b/(.+)$",line)
            if filename != []:
                if filtered_patch != []:
                    if filtered_patch[1][0:17] != "deleted file mode" and filtered_patch[1][0:13] != "new file mode":
                        result = subprocess.run(["git","show",versions[i]+":"+tmp_filename],cwd="./v8", stdout=subprocess.PIPE)
                        output = result.stdout.decode('utf-8', errors='ignore')
                        hunks = split_diff_lines_to_json(filtered_patch,output.split("\n"))
                        contents.append([tmp_filename,hunks])
                    filtered_patch = []
                if has_arcwords(filename[0][0]):
                    tmp_filename = filename[0][0]
                else:
                    tmp_filename = None
            if tmp_filename:
                filtered_patch.append(line)
        if contents != []:
            filtered_patchs["commits"] = get_commits([versions[i],versions[i+1]])
            filtered_patchs["contents"] = collect_parallel_hunks(contents)
            versions_diff.append(filtered_patchs)
    with open("./versions_diff_hunk.json","w") as f:
        json.dump(versions_diff,f,indent=4)