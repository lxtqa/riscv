from gen_result import read_file,write_file,gen_result
import re
from extract_unit import extract_unit
import subprocess
from utils.arch_utils import *
from utils.patch_utils import *


#三元组, unit1, unit1_, unit2
def match_unit(units1, units1_, units2):
    match = []
    #去除所有未发生改动的部分
    for i in range(len(units1)-1,-1,-1):
        unit1 = units1[i]
        for unit1_ in units1_:
            if remove_whitespace(unit1["content"]) == remove_whitespace(unit1_["content"]):
                units1.pop(i)
                units1_.remove(unit1_)
                break

    for unit1 in units1:
        matchlist = []
        #首先匹配函数名
        for unit1_ in units1_:
            if remove_whitespace(unit1["name"]) == remove_whitespace(unit1_["name"]):
                matchlist.append(unit1_)
        if matchlist == []:
            continue
        if len(matchlist)>1:
            matchlist = []
            #在匹配到多个函数名的情况下比较除了函数体之外的部分
            for unit1_ in units1_:
                if remove_whitespace(unit1["name_and_para"]) == remove_whitespace(unit1_["name_and_para"]):
                    matchlist.append(unit1_)
            if matchlist == [] or len(matchlist)>1:
                continue

        assert(len(matchlist)==1)
        tmp = matchlist[0]
        matchlist = []

        for unit2 in units2:
            if remove_archwords(remove_whitespace(unit1["name"])) == remove_archwords(remove_whitespace(unit2["name"])):
                matchlist.append(unit2)
        if matchlist == []:
            continue
        if len(matchlist)>1:
            matchlist = []
            #在匹配到多个函数名的情况下比较除了函数体之外的部分
            for unit2 in units2:
                if remove_archwords(remove_whitespace(unit1["name_and_para"])) == remove_archwords(remove_whitespace(unit2["name_and_para"])):
                    matchlist.append(unit2)
            if matchlist == [] or len(matchlist)>1:
                continue
        assert(len(matchlist)==1)
        match.append([unit1,tmp,matchlist[0]])

    return match

def unit_result(dir,
                    cfile_name1,
                    cfile_name2,
                    cfile_name1_,
                    cfile_name2_,
                    rm_tempfile,
                    use_docker,
                    debugging,
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

    changed_unit_headers = read_patch(diff.stdout)

    units1 = extract_unit(file1String)
    units1_ = extract_unit(file1_String)
    units2 = extract_unit(file2String)

    USE_ORIGIN = False

    new_units1 = []
    new_units1_ = []

    for changed_unit_header in changed_unit_headers:
        flag = False
        for unit in units1:
            if changed_unit_header in unit["content"].split("\n")[0]:
                if unit not in new_units1:
                    new_units1.append(unit)
                flag = True
                break
        if flag == False:
            USE_ORIGIN = True
            break

    for changed_unit_header in changed_unit_headers:
        flag = False
        for unit in units1_:
            if changed_unit_header in unit["content"].split("\n")[0]:
                if unit not in new_units1_:
                    new_units1_.append(unit)
                flag = True
                break
        if flag == False:
            USE_ORIGIN = True
            break


    if not USE_ORIGIN:
        matches = match_unit(new_units1,new_units1_,units2)
        for match in matches:
            #写到unit_file中
            write_file("./test/unit1.cc",match[0]["content"])
            write_file("./test/unit1_.cc",match[1]["content"])
            write_file("./test/unit2.cc",match[2]["content"])
            gen_result("./test","unit1.cc","unit2.cc","unit1_.cc","unit2_.cc",rm_tempfile,use_docker,debugging,MATCHER_ID,TREE_GENERATOR_ID)
            #应对未发生改动的情况
            tmp_string = read_file("./test/unit2_.cc")
            if remove_whitespace(match[2]["content"]) != remove_whitespace(tmp_string):
                file2String = file2String.replace(match[2]["content"],tmp_string)
                file1String = file1String.replace(match[0]["content"],match[1]["content"])
        write_file(dir + "/" + "tmp2.cc",file2String)
        write_file(dir + "/" + "tmp1.cc",file1String)
        if remove_whitespace(file1_String) != remove_whitespace(file1String):
            gen_result(
                dir=dir,
                cfile_name1="tmp1.cc",
                cfile_name2="tmp2.cc",
                cfile_name1_=cfile_name1_,
                cfile_name2_=cfile_name2_,
                rm_tempfile=rm_tempfile,
                use_docker=use_docker,
                debugging=debugging,
                MATCHER_ID="gumtree-simple-id",#"gumtree-hybrid",
                TREE_GENERATOR_ID="cpp-srcml"#"cs-srcml"
                )
        else:
            write_file(dir + "/" + cfile_name2_,file2String)
    else:
        print("USING ORIGIN METHOD")
        gen_result(
                dir=dir,
                cfile_name1=cfile_name1,
                cfile_name2=cfile_name2,
                cfile_name1_=cfile_name1_,
                cfile_name2_=cfile_name2_,
                rm_tempfile=rm_tempfile,
                use_docker=use_docker,
                debugging=debugging,
                MATCHER_ID="gumtree-simple-id",#"gumtree-hybrid",
                TREE_GENERATOR_ID="cpp-srcml"#"cs-srcml"
                )