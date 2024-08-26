from gen_result import read_file,write_file,gen_result
import tempfile
from extract_hunk import extract_hunk
import subprocess
from utils.arc_utils import *
from utils.patch_utils import *


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
                    merged_dict[key]['patch'].extend(item['patch'])
                else:
                    # 如果这个键不存在，直接添加到合并字典中
                    merged_dict[key] = item
            # 将合并结果转换回列表格式
            if len(list(merged_dict.values())) > 1:
                parallel_hunks_groups.append(list(merged_dict.values()))

    return parallel_hunks_groups



def hunk_result(dir,
                    cfile_name1,
                    cfile_name2,
                    cfile_name1_,
                    cfile_name2_,
                    use_docker,
                    MATCHER_ID,
                    TREE_GENERATOR_ID
                    ):
    '''
    cfile_name1为架构a下的文件, cfile2_name2为架构b下的文件, cfile_name1_为cfile_name1修改后的文件
    取cfile1和cfile2的match部分, 取cfile1与cfile1_的diff部分
    '''

    file1String = read_file(dir + "/" + cfile_name1)
    file1_String = read_file(dir + "/" + cfile_name1_)
    file2String = read_file(dir + "/" + cfile_name2)

    diff = subprocess.run(["diff","-up",dir + "/" + cfile_name1,dir + "/" + cfile_name1_],capture_output=True,text = True)

    changed_hunk_headers = read_patch(diff.stdout)

    hunks1 = extract_hunk(file1String.split("\n"))
    hunks1_ = extract_hunk(file1_String.split("\n"))
    hunks2 = extract_hunk(file2String.split("\n"))

    USE_ORIGIN = False

    new_hunks1 = []
    new_hunks1_ = []

    for changed_hunk_header in changed_hunk_headers:
        flag = False
        for hunk in hunks1:
            if changed_hunk_header in hunk["content"].split("\n")[0]:
                if hunk not in new_hunks1:
                    new_hunks1.append(hunk)
                flag = True
                break
        if flag == False:
            USE_ORIGIN = True
            break

    for changed_hunk_header in changed_hunk_headers:
        flag = False
        for hunk in hunks1_:
            if changed_hunk_header in hunk["content"].split("\n")[0]:
                if hunk not in new_hunks1_:
                    new_hunks1_.append(hunk)
                flag = True
                break
        if flag == False:
            USE_ORIGIN = True
            break


    if not USE_ORIGIN:
        matches = collect_parallel_hunks(new_hunks1,new_hunks1_,hunks2)
        for match in matches:
            #写到hunk_file中
            hunk2_ = gen_result(match[0]["content"],match[2]["content"],match[1]["content"],use_docker,MATCHER_ID,TREE_GENERATOR_ID)
            #应对未发生改动的情况
            if remove_whitespace(match[2]["content"]) != remove_whitespace(hunk2_):
                file2String = file2String.replace(match[2]["content"],hunk2_)
                file1String = file1String.replace(match[0]["content"],match[1]["content"])
        write_file(dir + "/" + "tmp2.cc",file2String)
        write_file(dir + "/" + "tmp1.cc",file1String)
        if remove_whitespace(file1_String) != remove_whitespace(file1String):
            gen_result(
                file1String,
                file2String,
                file1_String,
                use_docker=use_docker,
                MATCHER_ID=MATCHER_ID,
                TREE_GENERATOR_ID=TREE_GENERATOR_ID
                )
        else:
            write_file(dir + "/" + cfile_name2_,file2String)
    else:
        print("USING ORIGIN METHOD")
        gen_result(
                file1String,
                file2String,
                file1_String,
                use_docker=use_docker,
                MATCHER_ID=MATCHER_ID,#"gumtree-hybrid",
                TREE_GENERATOR_ID=TREE_GENERATOR_ID#"cs-srcml"
                )
    #store