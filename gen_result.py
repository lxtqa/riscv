import os
from get_ast import get_ast, TreeNode
from gumtree_parser import gumtree_parser
from diff_parser import diff_parser,bfs_search
from time import time
import sys
import re


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

def get_name(string):
    return string.split(" ")[1]

def replace(text,operations):
    #排序
    operations = sorted(operations, key=lambda x:  (x.start, x.rank))
    # 排序先插入再删除
    offset = 0
    for op in operations:
        text = text[:op.start+offset] + op.content + text[op.end+offset:]
        offset += len(op.content) - op.end + op.start
    return text

def map(diffOp,match_dic12,match_dic1_1,fileString):
    #截取产生修改部分的补丁代码
    start,end = get_start_end(diffOp.source.value)
    temp_string = fileString[start:end]
    #获取产生修改部分的补丁代码中需要进行映射的操作
    operations = []
    queue = [diffOp.source]
    while queue:
        node = queue.pop(0)
        new_name = get_newname(node.value,match_dic12,match_dic1_1)
        if new_name:
            start_end = get_start_end(node.value)
            operations.append(Operation(start_end[0]-start,  start_end[1]-start,  new_name))
        queue.extend(node.children)
    return replace(temp_string,operations)



def get_newname(node,match_dic12,match_dic1_1):
    #对不同种类进行分类讨论，对有name的进行映射
    # 如果能直接进行1_->1->2的映射，则采用该映射
    # 如果不能则在1_中寻找同名变量，然后再进行上一步的映射
    if node.split(" ")[0] == "name:":
        if node in match_dic1_1:
            if match_dic1_1[node] in match_dic12:
                return get_name(match_dic12[match_dic1_1[node]])
        else:
            same_names = []
            for key in match_dic1_1.keys():
                if get_name(node) == get_name(key):
                    same_names.append(match_dic1_1[key])
            #找到了相同的变量
            if len(same_names) > 1:
                #TODO:多个候选node的处理方法，目前选择找到第一个后返回
                for same_name in same_names:
                    if same_name in match_dic12:
                        mapped_node = match_dic12[same_name]
                        return get_name(mapped_node)
        #TODO: 找不到相同的变量，进行架构关键字的映射
        mapped_node = node.lstrip()
        return get_name(mapped_node)
    else:
        return None



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
    # ast1_ = get_ast(cfile_name1_,rm_tempfile=rm_tempfile)
    print("生成ast及diff耗时：{}s".format(time()-start_time))
    # file1String =  read_file(cfile_name1)
    file2String = read_file(cfile_name2)
    file1_String = read_file(cfile_name1_)
    file2_ = open(cfile_name2_,"w")
    matches12, _= gumtree_parser(gumtreefile_name1)
    matches11_, diffs11_ = gumtree_parser(gumtreefile_name2)

    #parse match
    match_dic12 = {}
    match_dic1_1 = {}
    match_dic11_ = {}
    for match in matches12:
        if match[1]!="---":
            exit(201)
        match_dic12[match[2]] = match[3]
    for match in matches11_:
        if match[1]!="---":
            exit(201)
        match_dic1_1[match[3]] = match[2]
        match_dic11_[match[2]] = match[3]

    #位置，内容
    operations = []
    #先对diff操作进行parse
    diffOps = diff_parser(diffs11_,match_dic11_)
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
                print("Genaration Failed")
                exit(300)
                # start,_ = get_start_end(des2.value)
                # child_rank = 0
            des1.children.insert(child_rank,TreeNode("VAL"));
    
            #使用映射解决问题
            queue = [diffOp.source]
            while queue:
                node = queue.pop(0)
                if node.value in match_dic11_:
                    node.value = match_dic11_[node.value]
                queue.extend(node.children)
            
            #内容 需要找到存在于原代码片段的位置
            #进行简单的映射:先找到1_所有同名变量，进行 1_->1 的映射，再进行 1->2 的映射
            content = map(diffOp,match_dic12,match_dic1_1,file1_String)
            if diffOp.op == "insert-tree" or diffOp.source.value.split(":")[0]=="comment":
                content =  content + "\n"           
            
            # 删除单行注释
            content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
            # 删除多行注释
            content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
            # 删除空行
            content = re.sub(r'\n\s*\n',r'\n',content)
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
    
    file2__string = replace(file2String,operations)
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
    