import os
from get_ast import get_ast
from gumtree_parser import gumtree_parser


def generate_tree(diff):
    def get_indent(string):
        count = 0
        for i in range(len(string)):
            if string[i] == " ":
                count+=1
            else:
                if count - count // 4 * 4 != 0:
                    exit(500)
                return count//4,string.lstrip()
    def gtree(indent,diff,rank):
        nodes = []
        nodes.append([diff[rank]])
        ind = indent[rank]
        rank = rank + 1
        while 1:
            if rank >= len(indent):
                return nodes,rank
            if indent[rank] == ind:
                nodes.append([diff[rank]])
            elif indent[rank] < ind:
                return nodes,rank -1
            else:
                subtree, rank=gtree(indent,diff,rank)
                nodes[-1].append(subtree)
            rank = rank+1
    diff = diff[2:-3].copy()
    indent = []
    for j in range(len(diff)):
        ind,result = get_indent(diff[j])
        diff[j] = result
        indent.append(ind)
    return gtree(indent,diff,0)

def mapping(node,ast1_,match_dic12,match_dic1_1):
    #对不同种类进行分类讨论，对有name的进行映射
    parts = node.split(" ")
    if parts[0] == "name:":
        same_name = find_same_name(parts[1],ast1_)
        #找到了相同的变量
        if len(same_name) > 1:
            #多个候选node的处理方法
            for name in same_name:
                if name in match_dic1_1:
                    if match_dic1_1[name] in match_dic12:
                        mapped_node = match_dic12[match_dic1_1[name]]
        #找不到相同的变量，进行架构关键字的映射
        else:
            pass
    else:
        mapped_node = node
    return mapped_node

def find_same_name(name,ast):
    result = []
    if ast.value.split(" ")[1] == name:
        result.append(ast.value)
    if ast.children != []:
        for child in ast.children:
            result = result + find_same_name(name,child)
    return result

def generate_diff(cfile_name1,cfile_name2,cfile_name1_):
    '''
    cfile_name1为架构a下的文件，cfile2_name2为架构b下的文件，cfile_name1_为cfile_name1修改后的文件
    取cfile1和cfile2的match部分，取cfile1与cfile1_的diff部分
    '''
    gumtreefile_name1 = "gumtree_12.txt"
    gumtreefile_name2 = "gumtree_11_.txt"
    os.system("./gumtree/gumtree textdiff " + cfile_name1 + " " + cfile_name2 + " > " + gumtreefile_name1)
    os.system("./gumtree/gumtree textdiff " + cfile_name1 + " " + cfile_name1_ + " > " + gumtreefile_name2)
    ast1 = get_ast(cfile_name1)
    ast2 = get_ast(cfile_name2)
    ast1_ = get_ast(cfile_name1_)
    matches12, _= gumtree_parser(gumtreefile_name1)
    matches11_, diffs11_ = gumtree_parser(gumtreefile_name2)
    print()
    print("Origin DIFFs:")
    print(diffs11_)  
    #parse match
    match_list = []
    match_dic12 = {}
    match_dic1_1 = {}
    for match in matches12:
        if match[1]!="---":
            exit(201)
        match_dic12[match[2]] = match[3]
        match_list.append([match[2],match[3]])
    for match in matches11_:
        if match[1]!="---":
            exit(201)
        match_dic1_1[match[3]] = match[2]
    #位置，内容
    for i in range(len(diffs11_)):
        diff = diffs11_[i]
        if diff[0] == "insert-node":
            if diff[1] != "---":
                exit(202)
            #内容 需要找到存在于原代码片段的位置
            if diff[2] in match_dic12:
                diff[2] = match_dic12[diff[2]]
            else:
                #进行简单的映射:先找到1_所有同名变量，进行 1_->1 的映射，再进行 1->2 的映射
                diff[2] = mapping(diff[2],ast1_,match_dic12,match_dic1_1)
                pass
            #位置
            diff[4] = match_dic12[diff[4]]
        elif diff[0] == "insert-tree":
            if diff[1] != "---":
                exit(203)
            #获取树
            tree,_ = generate_tree(diff)
            #对树进行映射
            a = 0
            pass
        elif diff[0] == "delete-node":
            if diff[1] != "---":
                exit(201)
            #位置 可以改map
            for j in range(len(match_list)):
                if match_list[j][0] == diff[2]:
                    diff[2] = match_list[j][1]
                    break
        elif diff[0] == "delete-tree":
            exit(204)
        elif diff[0] == "update-node":
            exit(205)
        else:
            exit(206)
        diffs11_[i] = diff 
    print()
    print("Parsed DIFFs:")
    print(diffs11_)
    os.system("rm "+gumtreefile_name1)
    os.system("rm "+gumtreefile_name2)
    pass

if __name__ == "__main__":
    generate_diff("test1.cpp","test2.cpp","test1_.cpp")