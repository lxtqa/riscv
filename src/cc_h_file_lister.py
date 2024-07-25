import os
from tqdm import tqdm
from ast_utils import get_type
import json
from extract_unit import extract_unit
import re
from disjoint_sets import find_disjoint_sets

def remove_whitespace(input_string):
    return re.sub(r'\s+', '', input_string)

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


def has_arcwords(text,arcword = ""):
    if arcword == "arm64" or arcword == "":
        for keyword in ["arm64","Arm64","ARM64"]:
            if keyword in text:
                return True
        return False
    elif arcword == "riscv" or arcword == "":
        for keyword in ["riscv64","Riscv64","RISCV64","riscv32","Riscv32","RISCV32","riscv","Riscv","RISCV"]:
            if keyword in text:
                return True
        return False

def remove_arcwords(text,arcword = ""):
    if arcword == "arm64":
        for keyword in ["arm64","Arm64","ARM64"]:
            text = text.replace(keyword, '')
        return text
    elif arcword == "riscv":
        for keyword in ["riscv64","Riscv64","RISCV64","riscv32","Riscv32","RISCV32","riscv","Riscv","RISCV"]:
            text = text.replace(keyword, '')
        return text
    elif arcword == "":
        for keyword in ["arm64","Arm64","ARM64","riscv64","Riscv64","RISCV64","riscv32","Riscv32","RISCV32","riscv","Riscv","RISCV"]:
            text = text.replace(keyword, '')
        return text

def file_parallel(file_name1,file_name2):
    if remove_arcwords(file_name1) == remove_arcwords(file_name2):
        return True
    return False

if __name__ == "__main__":
    current_directory = "./v8/src"
    cc_h_files = list_files(current_directory)
    functions = []

    riscv_num = 0
    arm_num = 0
    riscv_file_list = []
    arm_file_list = []
    for file in cc_h_files:
        if has_arcwords(file,"arm64"):
            arm_file_list.append(file)
            arm_num = arm_num+1
        if has_arcwords(file,"riscv"):
            riscv_file_list.append(file)
            riscv_num = riscv_num+1
    print(riscv_num)
    print(riscv_file_list)
    print(arm_num)
    print(arm_file_list)

    disjoint_sets = find_disjoint_sets(cc_h_files, file_parallel)
    _ = []

    for disjoint_set in disjoint_sets:
        if len(disjoint_set) > 1:
            _.append(disjoint_set)
    disjoint_sets = _

    result = []

    for disjoint_set in disjoint_sets:
        units1,units2 = [],[]
        len1, len2 = 0,0
        for file_name in disjoint_set:
            with open(file_name,"r") as f:
                if has_arcwords(file_name,"arm64"):
                    content = f.read()
                    len1+=len(content)
                    units1 += extract_unit(content)
                elif has_arcwords(file_name,"riscv"):
                    content = f.read()
                    len2+=len(content)
                    units2 += extract_unit(content)

        match = []
        for unit1 in units1:
            matchlist = []
            #首先匹配函数名
            for unit2 in units2:
                if remove_whitespace(remove_arcwords(unit1["name"],"arm64")) == remove_whitespace(remove_arcwords(unit2["name"],"riscv")):
                    matchlist.append(unit2)
            if matchlist == []:
                continue
            if len(matchlist) > 1:
                matchlist_ = []
                #在匹配到多个函数名的情况下比较除了函数体之外的部分
                for unit2 in matchlist:
                    if remove_whitespace(remove_arcwords(unit1["name_and_para"],"arm64")) == remove_whitespace(remove_arcwords(unit2["name_and_para"],"riscv")):
                        matchlist_.append(unit2)
                if matchlist_ == []:
                    continue
            match.append([unit1,matchlist[0]])
        rate1 = -1
        rate2 = -1
        text_rate1 =-1
        text_rate2 =-1
        if len(units1) != 0 and len(units2) != 0:
            rate1 = len(match)/len(units1)
            l1 = 0
            l11=0
            for i in units1:
                l1 +=len(i["content"])
            for i in match:
                l11 += len(i[0]["content"])
            text_rate1 = l11/l1
            rate2 = len(match)/len(units2)
            l2 = 0
            l22=0
            for i in units2:
                l2 +=len(i["content"])
            for i in match:
                l22 += len(i[1]["content"])
            text_rate2 = l22/l2
        print("| {} | {} | {} | {} | {} | {} | {} |".format(disjoint_set[0],rate1,rate2,text_rate1,text_rate2,len1,len2))
        result.append([disjoint_set,rate1,rate2,match])

    with open('match.json', 'w') as json_file:
        json.dump(result,json_file,indent=4)
