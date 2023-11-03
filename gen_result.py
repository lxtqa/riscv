import os
from get_ast import get_ast, TreeNode
from gumtree_parser import gumtree_parser
from diff_parser import diff_parser,bfs_search
from get_cfile import get_cfile
from time import time
import sys


class Operation:
    def __init__(self, start, end, content):
        self.start = start
        self.end = end
        self.content = content
        self.rank = 0

def read_file(file_name):
    file = open(file_name,"r")
    file_string = file.read()
    file.close()
    return file_string

def get_start_end(string):
    [start,end] = string.split(" ")[-1][1:-1].split(",")
    return int(start), int(end)

def replace(text,operations):
    #排序
    operations = sorted(operations, key=lambda x:  (x.start, x.rank))
    # 排序先插入再删除
    offset = 0
    for op in operations:
        text = text[:op.start+offset] + op.content + text[op.end+offset:]
        offset += len(op.content) - op.end + op.start
    return text

def remove(lst,item):
    while item in lst:
        lst.remove(item)
    return lst

def mapping(diffOp,ast1,match_dic12,match_dic1_1,file1__string):
    #截取产生修改部分的补丁代码
    start,end = get_start_end(diffOp.source.value)
    temp_string = file1__string[start:end]
    #获取产生修改部分的补丁代码中需要进行映射的操作
    operations = []

    queue = [diffOp.source]
    while queue:
        node = queue.pop(0)
        stri = map(node.value,ast1,match_dic12,match_dic1_1)
        if stri:
            parts = node.value.split(" ")
            rank = parts[-1][1:-1].split(",")
            parts = stri.split(" ")
            operations.append(Operation(int(rank[0])-start,  int(rank[1])-start,  parts[1]))
        queue.extend(node.children)
    return replace(temp_string,operations)



def map(node,ast1,match_dic12,match_dic1_1):
    #对不同种类进行分类讨论，对有name的进行映射
    parts = node.split(" ")
    remove(parts,"")
    if parts[0] == "name:":
        same_name = find_same_name(parts[1],ast1)
        #找到了相同的变量
        if len(same_name) > 1:
            #多个候选node的处理方法
            for name in same_name:
                if name in match_dic1_1:
                    if match_dic1_1[name] in match_dic12:
                        mapped_node = match_dic12[match_dic1_1[name]]
                        return mapped_node
        #TODO: 找不到相同的变量，进行架构关键字的映射
        mapped_node = node.lstrip()
        return mapped_node
    else:
        return None

def find_same_name(name,ast):
    result = []
    if ast.value != "VAL":
        if ast.value.split(" ")[1] == name:
            result.append(ast.value)
            if ast.children != []:
                for child in ast.children:
                    result = result + find_same_name(name,child)
    return result


def generate_diff(cfile_name1,cfile_name2,cfile_name1_,cfile_name2_,rm_tempfile):
    '''
    cfile_name1为架构a下的文件，cfile2_name2为架构b下的文件，cfile_name1_为cfile_name1修改后的文件
    取cfile1和cfile2的match部分，取cfile1与cfile1_的diff部分
    '''
    start_time = time()
    gumtreefile_name1 = "gumtree_12.txt"
    gumtreefile_name2 = "gumtree_11_.txt"
    os.system("docker run -v {}:/left.cc -v {}:/right.cc gumtreediff/gumtree textdiff /left.cc /right.cc -m gumtree-simple-id  > {}".format(
        cfile_name1, cfile_name2, gumtreefile_name1))
    os.system("docker run -v {}:/left.cc -v {}:/right.cc gumtreediff/gumtree textdiff /left.cc  /right.cc -m gumtree-simple-id > {}".format(
        cfile_name1, cfile_name1_, gumtreefile_name2))
    ast1 = get_ast(cfile_name1,rm_tempfile=rm_tempfile)
    ast2 = get_ast(cfile_name2,rm_tempfile=rm_tempfile)
    ast1_ = get_ast(cfile_name1_,rm_tempfile=rm_tempfile)
    print("生成ast及diff耗时：{}s".format(time()-start_time))
    # file1_string =  read_file(cfile_name1)
    file2_string = read_file(cfile_name2)
    file1__string = read_file(cfile_name1_)
    file2_ = open(cfile_name2_,"w")
    matches12, _= gumtree_parser(gumtreefile_name1)
    matches11_, diffs11_ = gumtree_parser(gumtreefile_name2)

    #parse match
    match_list = []
    match_dic12 = {}
    match_dic1_1 = {}
    match_dic11_ = {}

    for match in matches12:
        if match[1]!="---":
            exit(201)
        match_dic12[match[2]] = match[3]
        match_list.append([match[2],match[3]])
    for match in matches11_:
        if match[1]!="---":
            exit(201)
        match_dic1_1[match[3]] = match[2]
    for match in matches11_:
        if match[1]!="---":
            exit(201)
        match_dic11_[match[2]] = match[3]
    #位置，内容
    operations = []
    #先对diff操作进行parse
    diffOps = diff_parser(diffs11_,match_dic11_,ast1_)


    for diffOp in diffOps:
        if diffOp.op == "insert-node" or diffOp.op == "insert-tree":
            #位置
            if diffOp.desNode in match_dic12:
                des = match_dic12[diffOp.desNode]
            else:
                continue
            #在ast1,2中找到pos,根据其child找到位置
            des1 = bfs_search(ast1,diffOp.desNode)
            des2 = bfs_search(ast2,des)

            # 找到插入节点的后一个节点，进行映射，如果能映射到，则插入到后一个节点的前面
            # 找不到，则找到插入节点的前一个节点，进行映射，如果能映射到，则插入到前一个节点的后面
            # 全都找不到，就放在最前面
            child_rank = diffOp.desRank
            child_rank2 = -1
            last_node = None
            next_node = None
            start = -1
            for i in range(child_rank,len(des1.children)):
                if des1.children[i].value != "VAL":
                    if des1.children[i].value in match_dic12:
                        next_node = match_dic12[des1.children[i].value]
                        for j in range(len(des2.children)):
                            if des2.children[j].value == next_node:
                                child_rank2 = j
                                start,_ = get_start_end(des2.children[j].value)
                                break
                        break
            if start == -1:
                for i in range(child_rank-1,-1,-1):
                    if des1.children[i].value != "VAL":
                        if des1.children[i].value in match_dic12:
                            last_node = match_dic12[des1.children[i].value]
                            for j in range(len(des2.children)):
                                if des2.children[j].value == last_node:
                                    child_rank2 = j + 1
                                    _,start = get_start_end(des2.children[j].value)
                                    break
                            break
            
            if start == -1:
                start,_ = get_start_end(des2.value)
                child_rank = 0
            des1.children.insert(child_rank,TreeNode("VAL"));
    
            #内容 需要找到存在于原代码片段的位置
            #进行简单的映射:先找到1_所有同名变量，进行 1_->1 的映射，再进行 1->2 的映射
            content = mapping(diffOp,ast1,match_dic12,match_dic1_1,file1__string)
            if diffOp.op == "insert-tree" or diffOp.source.value.split(":")[0]=="comment":
                content =  content + "\n"           
            operation = Operation(start,start,content)
            operation.rank = child_rank2
            operations.append(operation)

        elif diffOp.op == "delete-node" or diffOp.op == "delete-tree":
            #位置 可以改map
            if diffOp.source.value in match_dic12:
                #删除结点
                des = match_dic12[diffOp.source.value]
                start,end = get_start_end(des)
                operation = Operation(start,end,"")
                operation.rank = sys.maxsize
                operations.append(operation)
        elif diffOp.op == "update-node":
            if diffOp.desNode in match_dic12:
                des = match_dic12[diffOp.desNode]
                start,end = get_start_end(des)
                operation = Operation(start,end,diffOp.update)
                operations.append(operation)
        else:
            exit(206)
    
    file2__string = replace(file2_string,operations)
    file2_.write(file2__string)
    file2_.close()
    os.system("diff -up {} {} > test/new_patch.patch".format(cfile_name2,cfile_name2_))

    if rm_tempfile:
        os.system("rm " + gumtreefile_name1)
        os.system("rm " + gumtreefile_name2)
    end_time = time()
    print("生成修改后代码总耗时：{}s".format(end_time-start_time))
    
if __name__ == "__main__":
    rm_tempfile = False
    if not os.path.exists("./test"):
        os.mkdir("./test")
    
    # generate_diff("./test/test1.cc",
    #               "./test/test2.cc",
    #               "./test/test1_.cc",
    #               "./test/test2_.cc",
    #               rm_tempfile,
    #               )
    generate_diff(sys.argv[1],
                  sys.argv[2],
                  sys.argv[3],
                  sys.argv[4],
                  rm_tempfile,
                  )
    