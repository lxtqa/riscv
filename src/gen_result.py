import os
from utils.ast_utils import *
from ast_diff_parser import diff_parser,bfs_search,bfs_search_father
from time import time
import sys
import re
import subprocess
import tempfile


class Operation:
    def __init__(self, start, end, content):
        self.start = start
        self.end = end
        self.content = content
        self.rank = 0
        self.offset = 0

def read_file(file_name):
    file = open(file_name,"r")
    file_string = file.read()
    file.close()
    return file_string

def write_file(file_name,content):
    directory = os.path.dirname(file_name)

    # 如果目录不存在，则创建它
    if not os.path.exists(directory):
        os.makedirs(directory)

    file = open(file_name,"w")
    file.write(content)
    file.close()



def replace(text,operations):
    #排序
    operations = sorted(operations, key=lambda x:  (x.start, x.rank))
    # 排序先插入再删除
    offset = 0
    for op in operations:
        text = text[:op.start+offset] + op.content + text[op.end+offset:]
        offset += len(op.content) - op.end + op.start
    return text

def arch_keyword_replace(string):
    # # 定义正则表达式模式
    # pattern = re.compile(r'(arm64|Arm64|ARM64)')
    # # 使用sub()函数进行替换，保留原始字符串的大小写格式
    # replaced = pattern.sub(lambda match: match.group().replace('arm', 'riscv').replace('Arm', 'Riscv').replace('ARM', 'RISCV'), string)
    # return replaced
    return string

def map(node,match_dic12,match_dic1_1,fileString):
    #截取产生修改部分的补丁代码
    start,end = get_start_end(node.value)
    temp_string = fileString[start:end]
    #获取产生修改部分的补丁代码中需要进行映射的操作

    operations = []
    queue = [node]
    while queue:
        node = queue.pop(0)
        new_name = get_newname(node.value,match_dic12,match_dic1_1)
        if new_name:
            start_end = get_start_end(node.value)
            operations.append(Operation(start_end[0]-start,  start_end[1]-start,  new_name))
        queue.extend(node.children)
    replaced = replace(temp_string,operations)
    replaced = arch_keyword_replace(replaced)
    return replaced



def get_newname(node,match_dic12,match_dic1_1):
    #对不同种类进行分类讨论，对有name的进行映射
    # 如果能直接进行1_->1->2的映射，则采用该映射
    # 如果不能则在1_中寻找同名变量，然后再进行上一步的映射
    if node.split(" ")[0] == "name:":
        if match_dic1_1 != None:
            if node in match_dic1_1.keys():
                if get_name(node) != get_name(match_dic1_1[node]):
                    return None
                if match_dic1_1[node] in match_dic12:
                    return get_name(match_dic12[match_dic1_1[node]])
            # else:
            #     same_names = []
            #     for key in match_dic1_1.keys():
            #         if get_name(node) == get_name(key):
            #             same_names.append(match_dic1_1[key])
            #     #找到了相同的变量
            #     if len(same_names) > 1:
            #         #TODO:多个候选node的处理方法，目前选择找到第一个后返回
            #         for same_name in same_names:
            #             if same_name in match_dic12:
            #                 mapped_node = match_dic12[same_name]
            #                 return get_name(mapped_node)
        else:
            if node in match_dic12.keys():
                return get_name(match_dic12[node])
            # else:
            #     same_names = []
            #     for key in match_dic12.keys():
            #         if get_name(node) == get_name(key):
            #             same_names.append(match_dic12[key])
            #     #找到了相同的变量
            #     if len(same_names) > 1:
            #         #TODO:多个候选node的处理方法，目前选择找到第一个后返回
            #         for same_name in same_names:
            #             return get_name(same_name)
        #TODO: 找不到相同的变量，进行架构关键字的映射
        mapped_node = node.lstrip()
        return get_name(mapped_node)
    else:
        return None






def gen_result(file1String,
                file2String,
                file1_String,
                use_docker,
                MATCHER_ID,
                TREE_GENERATOR_ID
                ):
    '''
    cfile_name1为架构a下的文件，cfile2_name2为架构b下的文件，cfile_name1_为cfile_name1修改后的文件
    取cfile1和cfile2的match部分，取cfile1与cfile1_的diff部分
    '''
    start_time = time()

    with tempfile.NamedTemporaryFile(delete=True, mode='w', suffix='.cpp') as cfile1, \
        tempfile.NamedTemporaryFile(delete=True, mode='w', suffix='.cpp') as cfile1_, \
        tempfile.NamedTemporaryFile(delete=True, mode='w', suffix='.cpp') as cfile2:

        cfile1.write(file1String)
        cfile1.flush()
        cfile1_.write(file1_String)
        cfile1_.flush()
        cfile2.write(file2String)
        cfile2.flush()

        ast1,ast1Nodenum = get_ast(cfile1.name,use_docker=use_docker,TREE_GENERATOR_ID=TREE_GENERATOR_ID)
        ast1_,ast1_Nodenum  = get_ast(cfile1_.name,use_docker=use_docker,TREE_GENERATOR_ID=TREE_GENERATOR_ID)

        # ast2 = get_ast(cfile_name2,rm_tempfile=rm_tempfile,use_docker=use_docker,debugging=debugging,TREE_GENERATOR_ID=TREE_GENERATOR_ID)

        if use_docker:
            output11_ = subprocess.run(["docker","run","--rm","-v",cfile1.name+":/left.cc","-v",cfile1_.name+":/right.cc","gumtreediff/gumtree","textdiff","/left.cc", "/right.cc",
                                        "-m",MATCHER_ID,"-g", TREE_GENERATOR_ID],#,"-M","bu_minsim","0.5"],
                                        capture_output=True,text = True)
            output12 = subprocess.run(["docker","run","--rm","-v",cfile1.name+":/left.cc","-v",cfile2.name+":/right.cc","gumtreediff/gumtree","textdiff","/left.cc", "/right.cc",
                                        "-m",MATCHER_ID,"-g", TREE_GENERATOR_ID],#,"-M","bu_minsim","0.5"],
                                        capture_output=True,text = True)
        else:
            output11_ = subprocess.run(["gumtree","textdiff",cfile1.name, cfile1_.name,
                                        "-m",MATCHER_ID,"-g", TREE_GENERATOR_ID],#,"-M","bu_minsim","0.5"],
                                        capture_output=True,text = True)
            output12 = subprocess.run(["gumtree","textdiff",cfile1.name, cfile2.name,
                                        "-m",MATCHER_ID,"-g", TREE_GENERATOR_ID],#,"-M","bu_minsim","0.5"],
                                        capture_output=True,text = True)

        print("生成ast及diff耗时: {}s".format(time()-start_time))
        matches11_, diffs11_ = gumtree_parser(output11_.stdout)
        matches12, _= gumtree_parser(output12.stdout)

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


        operations = []
        #如果相似度低于某个阈值，则直接替换：
        similarity = len(match_dic11_)/(ast1Nodenum + ast1_Nodenum - len(match_dic11_))
        if similarity < 0.2:
            print("Similary too low!")
            return arch_keyword_replace(file1_String)

        #先对diff操作进行parse
        diffOps = diff_parser(diffs11_,match_dic11_)

        diffOp_i = 0
        while diffOp_i < len(diffOps):
            diffOp = diffOps[diffOp_i]
            diffOp_i = diffOp_i + 1
            if diffOp.op == "insert-node" or diffOp.op == "insert-tree":
                #位置
                if diffOp.desNode in match_dic12:
                    des = match_dic12[diffOp.desNode]
                else:
                    continue
                #在ast1,2中找到pos,根据其child找到位置
                desNode = bfs_search(ast1,diffOp.desNode)

                # 找到插入节点的后一个节点，进行映射，如果能映射到，则插入到后一个节点的前面
                # 找不到，则找到插入节点的前一个节点，进行映射，如果能映射到，则插入到前一个节点的后面
                # 全都找不到，就放在最前面
                child_rank = diffOp.desRank
                child_rank2 = -1
                start = -1
                for i in range(child_rank-1,-1,-1):
                    if desNode.children[i].value != "VAL":
                        if desNode.children[i].value in match_dic12:
                            _,start = get_start_end(match_dic12[desNode.children[i].value])
                            break
                if start == -1:
                    for i in range(child_rank,len(desNode.children)):
                        if desNode.children[i].value != "VAL":
                            if desNode.children[i].value in match_dic12:
                                start,_ = get_start_end(match_dic12[desNode.children[i].value])
                                break
                if start ==-1:
                    start,_ = get_start_end(des)
                    if get_type(des) == "parameter_list":
                        start = start+1

                #内容 需要找到存在于原代码片段的位置
                #进行简单的映射:先找到1_所有同名变量，进行 1_->1 的映射，再进行 1->2 的映射
                # if diffOp.move == False:
                content = map(bfs_search(ast1_,diffOp.source.value),match_dic12,match_dic1_1,file1_String)
                # else:
                #     content = map(diffOp,match_dic12,None,file1String)
                if diffOp.op == "insert-tree" or diffOp.source.value.split(":")[0]=="comment":
                    if get_type(diffOp.source.value) == "argument" or get_type(diffOp.source.value) == "parameter":
                        if len(desNode.children) != 0:
                            if diffOp.desRank == len(desNode.children):
                                content =  ", " + content
                            elif diffOp.desRank == 0:
                                content =  content + ", "
                            else:
                                content =  ", " + content + ", "

                    elif get_type(diffOp.desNode)== "block" or get_type(diffOp.desNode) == "unit" or get_type(diffOp.desNode) == "block_content":
                        content =  "\n" + content + "\n"
                    else:
                        content =  " " + content + " "

                desNode.children.insert(child_rank,TreeNode("VAL"))

                # 删除单行注释
                content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
                # 删除多行注释
                content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)

                operation = Operation(start,start,content)
                operation.rank = child_rank2
                operations.append(operation)
            elif diffOp.op == "delete-node" or diffOp.op == "delete-tree":
                if diffOp.source.value in match_dic12:
                    #删除结点
                    desNode = bfs_search_father(ast1,diffOp.source.value)
                    r = 0
                    des = match_dic12[diffOp.source.value]
                    for i in range(len(desNode.children)):
                        if desNode.children[i].value == diffOp.source.value:
                            r = i

                    start,end = get_start_end(des)
                    try:
                        if get_type(des) == "argument" or get_type(des) == "parameter":
                            if r == len(desNode.children)-1:
                                #向前找到逗号删除
                                while r-1>0 and desNode.children[r-1].value == "VAL":
                                    r = r-1
                                _,start = get_start_end(match_dic12[desNode.children[r-1].value])
                            else:
                                #向后找到逗号删除
                                while r+1 < len(desNode.children) and desNode.children[r+1].value == "VAL":
                                    r = r+1
                                end,_ = get_start_end(match_dic12[desNode.children[r+1].value])
                    except:
                        pass
                    operation = Operation(start,end,"")
                    operation.rank = sys.maxsize
                    operations.append(operation)
                    # 在ast中删除节点
                    desNode.children.pop(r)
                else:
                    if diffOp_i < len(diffOps):
                        if diffOps[diffOp_i].id == diffOp.id:
                            diffOp_i = diffOp_i + 1
            elif diffOp.op == "update-node":
                if diffOp.desNode in match_dic12:
                    if re.match(r'//.*$',diffOp.source) or re.match(r'/\*.*?\*/',diffOp.source):
                        continue
                    des = match_dic12[diffOp.desNode]
                    start,end = get_start_end(des)
                    operation = Operation(start,end,arch_keyword_replace(diffOp.source))
                    operations.append(operation)
            else:
                exit(206)
        file2_String = replace(file2String,operations)
        #删除所有两个连着的逗号
        file2_String = re.sub(r',(\s*,)+', ', ', file2_String)

        #删除所有以 “\”结尾的空行
        file2_String = re.sub(r'^\s*\\\s*$', '', file2_String,flags=re.MULTILINE)

        end_time = time()
        print("生成修改后代码总耗时: {}s".format(end_time-start_time))

        return file2_String
