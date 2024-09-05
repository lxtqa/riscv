from gen_result import read_file,write_file,gen_result
import tempfile
import subprocess
from extract_hunk import extract_hunk
import subprocess
from utils.arch_utils import *
from utils.patch_utils import *


def collect_parallel_hunks(all_hunks):
    """
    整合commit下多个文件的所有hunks, 找到所有平行的hunks并返回一个JSON对象。
    :param all_hunks: 字典, 键为文件路径, 值为文件的hunks内容列表。
    :return: JSON对象, 包含所有平行的hunks信息。
    """

    parallel_hunks_groups = []

    #首先过一遍纯name的检查，然后再进行header的检查
    #先检查同文件内是否有相同name的函数，如果没有，则直接认为name相同即为para
    #如果有则比较hunk
    # 判断平行的条件：file平行且不同，

    # 找到所有平行的hunks

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

    visited = [False] * len(all_hunks)
    for i in range(len(all_hunks)):
        if visited[i]:
            continue
        parallel_group = [all_hunks[i]]
        visited[i] = True
        if same_named[i]:
            hunk_header1 = all_hunks[i]['header']
            for j in range(i + 1, len(all_hunks)):
                hunk_header2 = all_hunks[j]['header']
                if ishunkpara(hunk_header1, hunk_header2):
                    parallel_group.append(all_hunks[j])
                    visited[j] = True
        else:
            hunk_name1 = extract_name(all_hunks[i]['header'])
            hunk_header1 = all_hunks[i]['header']
            for j in range(i + 1, len(all_hunks)):
                hunk_name2 = extract_name(all_hunks[j]['header'])
                if hunk_name1 != None and hunk_name2 != None and not same_named[j]:
                    if ishunkpara(hunk_name1, hunk_name2):
                        parallel_group.append(all_hunks[j])
                        visited[j] = True
                else:
                    hunk_header2 = all_hunks[j]['header']
                    if ishunkpara(hunk_header1, hunk_header2):
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

    return parallel_hunks_groups


def clear(file1String,changed_header):
    tmp_file1String = file1String.split("\n")
    header_re = r"^((::[\[:space:]]*)?[A-Za-z_].*)$"
    for i,line in enumerate(tmp_file1String):
        if line != changed_header:
            tmp_file1String[i] = " "*len(line)
        else:
            for j,line in enumerate(tmp_file1String):
                if j <= i :  continue
                if re.match(header_re,line):
                    for k,line in enumerate(tmp_file1String):
                        if k < j :  continue
                        tmp_file1String[k] = " "*len(line)
                    return tmp_file1String


def hunk_result(cfile1,
                patch1,
                cfile2,
                use_docker,
                MATCHER_ID,
                TREE_GENERATOR_ID):

    changed_header = patch1["header"]
    file1String = "\n".join(clear(cfile1,changed_header))

    with tempfile.NamedTemporaryFile(delete=True, mode='w', suffix='.cc') as file1, \
        tempfile.NamedTemporaryFile(delete=True, mode='w', suffix='.patch') as patchfile1:
            file1.write(file1String)
            file1.flush()
            patch1["patch"] = ["diff --git a/a.cc b/b.cc","--- a/a.cc","+++ b/b.cc"] + patch1["patch"]
            patchfile1.write("\n".join(patch1["patch"])+"\n")
            patchfile1.flush()
            output11_ = subprocess.run(["patch",file1.name,patchfile1.name,"--output=-"],capture_output=True,text = True)
            file1_String = output11_.stdout
    file2String = cfile2



    hunks1  = {"header":changed_header,"content":file1String.strip().split("\n"), "file":"1" }
    hunks1_ = {"header":changed_header,"content":file1_String.strip().split("\n"),"file":"1_"}
    hunks2 = extract_hunk(file2String.split("\n"),file_name="2")

    #处理增加函数的情况
    USE_ORIGIN = False


    if USE_ORIGIN:
        # print("USING ORIGIN METHOD")
        file2String = gen_result(file1String,file2String,file1_String,use_docker,MATCHER_ID,TREE_GENERATOR_ID)
    else:
        matches = collect_parallel_hunks([hunks1]+[hunks1_]+hunks2)
        for i in range(len(matches)):
            for j in range(len(matches[i])):
                matches[i][j]["content"] = "\n".join(matches[i][j]["content"])
        for match in matches:
            #写到hunk_file中
            hunk2_ = gen_result(match[0]["content"],match[2]["content"],match[1]["content"],use_docker,MATCHER_ID,TREE_GENERATOR_ID)
            #应对未发生改动的情况
            if remove_whitespace(match[2]["content"]) != remove_whitespace(hunk2_):
                if match[2]["content"] not in file2String:
                    exit(400)
                file2String = file2String.replace(match[2]["content"],hunk2_)
                if match[0]["content"] not in file1String:
                    exit(400)
                file1String = file1String.replace(match[0]["content"],match[1]["content"])
        if remove_whitespace(file1_String) != remove_whitespace(file1String):
            file2String = gen_result(file1String,file2String,file1_String,use_docker,MATCHER_ID,TREE_GENERATOR_ID)

    return file2String