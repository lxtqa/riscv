import os
from get_ast import get_ast, TreeNode
from gumtree_parser import gumtree_parser
from AstDiffParser import diff_parser,bfs_search
from DiffParser import diff2rank
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
    if len(string.split(" ")) == 3:
        return string.split(" ")[1]
    else:
        return None

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
        if match_dic1_1 != None:
            if node in match_dic1_1.keys():
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
        else:
            if node in match_dic12.keys():
                return get_name(match_dic12[node])
            else:
                same_names = []
                for key in match_dic12.keys():
                    if get_name(node) == get_name(key):
                        same_names.append(match_dic12[key])
                #找到了相同的变量
                if len(same_names) > 1:
                    #TODO:多个候选node的处理方法，目前选择找到第一个后返回
                    for same_name in same_names:
                        return get_name(same_name)
        #TODO: 找不到相同的变量，进行架构关键字的映射
        mapped_node = node.lstrip()
        return get_name(mapped_node)
    else:
        return None


def simplify(cfile_name1,cfile_name1_,ast1,new_cfile_name1):
    # 不需要ast 而是直接进行文本级别的diff

    diff_file_name = "./test/patch.patch"
    file1String = read_file(cfile_name1)
    os.system("diff -up {} {} > {}".format(cfile_name1,cfile_name1_,diff_file_name))
    ranks = diff2rank(diff_file_name,cfile_name1)
    # for treeNode in ast1.children:
    #     start,end = get_start_end(treeNode.value)
    #     flag = False
    #     for rank in ranks:
    #         if not start > rank["ending"] and not end < rank["begining"]:
    #             flag = True
    #     if flag:
    #         tmp_string = tmp_string[:start] + file1String[start:end] + tmp_string[end:]
    
    '''
        TODO:以block_content/block/unit为平行结构的判断依据
    '''
    queue = [ast1]
    while queue:
        node = queue.pop(0)
        if node.value.split(" ")[0] == "unit" or node.value.split(" ")[0] == "block" or node.value.split(" ")[0] == "block_content":
            for child in node.children:
                start,end = get_start_end(child.value)
                flag = False
                for rank in ranks:
                    if not start > rank["ending"] and not end < rank["begining"]:
                        flag = True
                if flag:
                    queue.append(child)
                else:
                    file1String = file1String[:start] + " " * (end-start) + file1String[end:]
        else:
            queue.extend(node.children)
                
    f = open(new_cfile_name1,"w")
    f.write(file1String)
    f.close()


        

def gen_result(cfile_name1,cfile_name2,
               cfile_name1_,cfile_name2_,
               rm_tempfile,
               use_docker,
               simple,
               debugging,
               MATCHER_ID,
               TREE_GENERATOR_ID
               ):
    '''
    cfile_name1为架构a下的文件，cfile2_name2为架构b下的文件，cfile_name1_为cfile_name1修改后的文件
    取cfile1和cfile2的match部分，取cfile1与cfile1_的diff部分
    '''
    start_time = time()
    
    gumtreefile_name1 = "./test/gumtree_12.txt"
    gumtreefile_name2 = "./test/gumtree_11_.txt"
    
    ast1 = get_ast(cfile_name1,rm_tempfile=rm_tempfile,use_docker=use_docker,debugging=debugging,TREE_GENERATOR_ID=TREE_GENERATOR_ID)
    '''
    选择是否使用简化
    '''
    if simple:
        '''
        先对1和1_做text级别的diff, 根据diff结果删除无关的节点（目前进行的是简单删除，即删除unit节点下的无关节点）, 再进行astdiff 
        '''
        ast1_ = get_ast(cfile_name1_,rm_tempfile=rm_tempfile,use_docker=use_docker,debugging=debugging,TREE_GENERATOR_ID=TREE_GENERATOR_ID)

        simplify(cfile_name1,cfile_name1_,ast1,'./test/tmp1.cc')
        simplify(cfile_name1_,cfile_name1,ast1_,'./test/tmp1_.cc')

    ast2 = get_ast(cfile_name2,rm_tempfile=rm_tempfile,use_docker=use_docker,debugging=debugging,TREE_GENERATOR_ID=TREE_GENERATOR_ID)
    if not debugging:
        if use_docker:
            if simple:
                os.system("docker run -v {}:/left.cc -v {}:/right.cc gumtreediff/gumtree textdiff /left.cc  /right.cc -m {} -g {} > {}".format(
                    './test/tmp1.cc', './test/tmp1_.cc', MATCHER_ID, TREE_GENERATOR_ID, gumtreefile_name2))
            else:
                os.system("docker run -v {}:/left.cc -v {}:/right.cc gumtreediff/gumtree textdiff /left.cc /right.cc -m {} -g {} > {}".format(
                    cfile_name1, cfile_name1_, MATCHER_ID, TREE_GENERATOR_ID, gumtreefile_name1))
            os.system("docker run -v {}:/left.cc -v {}:/right.cc gumtreediff/gumtree textdiff /left.cc /right.cc -m {} -g {} > {}".format(
                cfile_name1, cfile_name2, MATCHER_ID, TREE_GENERATOR_ID, gumtreefile_name1))
        else:
            if simple:
                os.system("./gumtree/gumtree textdiff {} {} -m {} -g {} > {}".format(
                    './test/tmp1.cc', './test/tmp1_.cc', MATCHER_ID, TREE_GENERATOR_ID, gumtreefile_name2))
            else:
                os.system("./gumtree/gumtree textdiff {} {} -m {} -g {} > {}".format(
                    cfile_name1, cfile_name1_, MATCHER_ID, TREE_GENERATOR_ID, gumtreefile_name2))
            os.system("./gumtree/gumtree textdiff {} {} -m {} -g {} > {}".format(
                cfile_name1, cfile_name2, MATCHER_ID, TREE_GENERATOR_ID, gumtreefile_name1))
    
    print("生成ast及diff耗时: {}s".format(time()-start_time))
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
            # if diffOp.move == False:
            content = map(diffOp,match_dic12,match_dic1_1,file1_String)
            # else:
            #     content = map(diffOp,match_dic12,None,file1String)
            if diffOp.op == "insert-tree" or diffOp.source.value.split(":")[0]=="comment":
                if  diffOp.source.value.split(" ")[0] == "argument":
                    content = content + ", "
                else:
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
    print("生成修改后代码总耗时: {}s".format(end_time-start_time))
    
if __name__ == "__main__":
    rm_tempfile = False
    use_docker = False
    simple = False
    debugging = False
    
    gen_result(cfile_name1="./test/test1.cc",
                  cfile_name2="./test/test2.cc",
                  cfile_name1_="./test/test1_.cc",
                  cfile_name2_="./test/test2_.cc",
                  rm_tempfile=rm_tempfile,
                  use_docker=use_docker,
                  simple=simple,
                  debugging=debugging,
                  MATCHER_ID="gumtree-simple",
                  TREE_GENERATOR_ID="cs-srcml"
                  )
    