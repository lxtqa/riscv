from utils.ast_utils import *
from ast_diff_parser import diff_parser,bfs_search,bfs_search_father,get_start_end
from time import time
import sys
import re
import regex
import subprocess
import tempfile
from fuzzywuzzy import process
import xml.etree.ElementTree as ET
import copy


def modify_comma(xml_root):
    xml_nodes = [xml_root]
    while xml_nodes != []:
        xml_node = xml_nodes.pop()
        if xml_node.tag.endswith("parameter_list") or xml_node.tag.endswith("member_init_list") or xml_node.tag.endswith("super_list") or xml_node.tag.endswith("argument_list"):
            if len(xml_node)!=0:
                for i in range(len(xml_node)-1,-1,-1):
                    if not xml_node[i].tag.endswith("comment"):
                        xml_node[i].tail = None
                        for j in range(i-1,-1,-1):
                            if not xml_node[j].tag.endswith("comment"):
                                xml_node[j].tail = ", "
                        break
                
        xml_nodes.extend(xml_node)


def init_ast(ast_root,xml_root):
    ast_nodes = [ast_root]
    xml_nodes = [xml_root]
    while ast_nodes != []:
        ast_node = ast_nodes.pop()
        xml_node = xml_nodes.pop()
        if xml_node.text == "()":
            xml_node.text = "("
            if xml_node.tail != None:
                xml_node.tail = ")" + xml_node.tail
            else:
                xml_node.tail = ")"
        elif xml_node.text == "<>":
            xml_node.text = "<"
            if xml_node.tail != None:
                xml_node.tail = ">" + xml_node.tail
            else:
                xml_node.tail = ">"
        elif xml_node.text == "{}":
            xml_node.text = "{"
            if xml_node.tail != None:
                xml_node.tail = "}" + xml_node.tail
            else:
                xml_node.tail = "}"
        elif xml_node.text == "(" and ((xml_node.tail != None and not xml_node.tail.startswith(")")) or xml_node.tail == None):
            if len(xml_node) > 0:
                if xml_node[-1].tail == ")":
                    if xml_node[-1].text!="(":
                        xml_node[-1].tail = None
                    if xml_node.tail != None:
                        xml_node.tail=")" + xml_node.tail
                    else:
                        xml_node.tail = ")"
        elif xml_node.text == "<" and ((xml_node.tail != None and not xml_node.tail.startswith(">")) or xml_node.tail == None):
            if len(xml_node) > 0:
                if xml_node[-1].tail == ">":
                    if xml_node[-1].text!="<":
                        xml_node[-1].tail = None
                    if xml_node.tail != None:
                        xml_node.tail=">" + xml_node.tail
                    else:
                        xml_node.tail = ">"
        elif xml_node.text == "{" and ((xml_node.tail != None and not xml_node.tail.startswith("}")) or xml_node.tail == None):
            if len(xml_node) > 0:
                if xml_node[-1].tail == "}":
                    if xml_node[-1].text!="{":
                        xml_node[-1].tail = None
                    if xml_node.tail != None:
                        xml_node.tail="}" + xml_node.tail
                    else:
                        xml_node.tail = "}"
        ast_node.xml = xml_node
        ast_nodes.extend(ast_node.children)
        xml_nodes.extend(xml_node)



# def clean_parameter_list_in_file(file_content):
#     # 定义一个函数来处理括号内的参数列表
#     def clean_inside_parentheses(match):
#         inside = match[0]
#         # 删除连续的逗号（允许中间有空白字符）
#         inside = re.sub(r',(\s*,)+', ',', inside)
#         # 删除末尾逗号（允许逗号后有空白字符）
#         inside = re.sub(r',\s*\)', ')', inside)
#         # 删除开头逗号（允许逗号前有空白字符）
#         inside = re.sub(r'\(\s*,', '(', inside)
#         return f'{inside}'
    
#     # 匹配所有括号内的内容，并逐个进行处理
#     cleaned_content = regex.sub(r'\((?:[^()]*|(?R))*\)', clean_inside_parentheses, file_content, flags=re.DOTALL)
    
#     return cleaned_content

def construct_mapping_dict(mapping):
    mapping_dict = {}
    for key in mapping.keys():
        value = mapping[key]
        if key.split(" ")[0] == "name:" and value.split(" ")[0] == "name:":
            k,v = get_name(key),get_name(value)
            if k not in mapping_dict.keys():
                mapping_dict[k] = {v:1}
            else:
                if v not in mapping_dict[k].keys():
                    mapping_dict[k][v] = 1
                else:
                    mapping_dict[k][v] = mapping_dict[k][v] + 1
    return mapping_dict


# class Operation:
#     def __init__(self, start, end, content):
#         self.start = start
#         self.end = end
#         self.content = content
#         self.rank = 0
#         self.offset = 0


# def replace(text,operations):
#     #排序
#     operations = sorted(operations, key=lambda x:  (x.start, x.rank))
#     # 排序先插入再删除
#     offset = 0
#     for op in operations:
#         text = text[:op.start+offset] + op.content + text[op.end+offset:]
#         offset += len(op.content) - op.end + op.start
#     return text

# def map_(node,mapping_dict,mapping_dic12,file_string):
#     #截取产生修改部分的补丁代码
#     start,end = get_start_end(node.value)
#     temp_string = file_string[start:end]
#     #获取产生修改部分的补丁代码中需要进行映射的操作

#     operations = []
#     queue = [node]
#     while queue:
#         node = queue.pop()
#         if node.value.split(" ")[0] == "name:":
#             new_name = get_newname(node.value,mapping_dict,mapping_dic12)
#             if new_name:
#                 start_end = get_start_end(node.value)
#                 operations.append(Operation(start_end[0]-start,  start_end[1]-start,  new_name))
#         queue.extend(node.children)
#     replaced = replace(temp_string,operations)
#     return replaced


def map(root,mapping_dict,mapping_dic12):
    #获取产生修改部分的补丁代码中需要进行映射的操作
    queue = [root]
    while queue:
        xml = queue.pop()
        if xml.tag.endswith("name") and xml.text !=  None:
            new_name = get_newname(xml.text,mapping_dict,mapping_dic12)
            if new_name:
                xml.text =  new_name
        queue.extend(xml)
    return root



def get_newname(node_name,mapping_dict,mapping_dic12):
    """
        对name节点进行映射
    """
    if node_name not in mapping_dict.keys():
        return node_name
    candidate = []
    current_max = 0
    if mapping_dic12 != {}:
        if node_name in mapping_dic12.keys():
            for item in mapping_dic12[node_name].keys():
                if item == node_name:
                    return item
                if mapping_dic12[node_name][item] > current_max:
                    current_max = mapping_dic12[node_name][item]
                    candidate = [item]
                elif mapping_dic12[node_name][item] == current_max:
                    candidate.append(item)
    if mapping_dic12 == {} or candidate == []:
        for item in mapping_dict[node_name].keys():
            if item == node_name:
                return item
            if mapping_dict[node_name][item] > current_max:
                current_max = mapping_dict[node_name][item]
                candidate = [item]
            elif mapping_dict[node_name][item] == current_max:
                candidate.append(item)

    matches = process.extract(node_name, candidate)
    return matches[0][0]


def parse_diff(diff,ast1,ast1_,ast2,match_dic11_,match_dic12,mapping_dict):
    if diff[0] == "insert-node" or diff[0] == "insert-tree":
        source = parse_tree_from_text(diff[2:-3])
        des_node = parse_tree_from_text([diff[-2]])
        if des_node.value + "_" in match_dic12.keys() or des_node.value in match_dic12.keys():
            if des_node.value + "_" in match_dic12.keys():
                des_node.value = des_node.value + "_"
            desRank = int(diff[-1].split(" ")[-1])
            father1 = bfs_search(ast1,des_node.value)
            source = copy.deepcopy(bfs_search(ast1_,source.value))
            queue = [source]
            while queue:
                node = queue.pop()
                node.value = node.value + "_"
                queue.extend(node.children)
            if diff[0] == "insert-node":
                for i in range(len(source.xml)-1,-1,-1):
                    source.xml.remove(source.xml[i])
                source.children = []
            father1.xml.insert(desRank,source.xml)
            father1.children.insert(desRank,source)

            #不在father中找,而是直接找前后关系

            #father2 = bfs_search(ast2,match_dic12[des_node.value])

            new_source = copy.deepcopy(source)

            for i in range(desRank-1,-1,-1):
                if father1.children[i].value in match_dic12:
                    father2 = bfs_search_father(ast2,match_dic12[father1.children[i].value])
                    for j,child in enumerate(father2.children):
                        if match_dic12[father1.children[i].value] == child.value:
                            queue = [new_source]
                            while queue:
                                node = queue.pop()
                                match_dic12[node.value] = node.value
                                queue.extend(node.children)
                            father2.xml.insert(j+1,map(new_source.xml,mapping_dict,{}))
                            father2.children.insert(j+1,new_source)
                            return
            for i in range(desRank+1,len(father1.children)):
                if father1.children[i].value in match_dic12:
                    father2 = bfs_search_father(ast2,match_dic12[father1.children[i].value])
                    for j,child in enumerate(father2.children):
                        if match_dic12[father1.children[i].value] == child.value:
                            queue = [new_source]
                            while queue:
                                node = queue.pop()
                                match_dic12[node.value] = node.value
                                queue.extend(node.children)
                            father2.xml.insert(j,map(new_source.xml,mapping_dict,{}))
                            father2.children.insert(j,new_source)
                            return
            father2 = bfs_search(ast2,match_dic12[des_node.value])
            queue = [new_source]
            while queue:
                node = queue.pop()
                match_dic12[node.value] = node.value
                queue.extend(node.children)
            father2.xml.insert(0,map(new_source.xml,mapping_dict,{}))
            father2.children.insert(0,new_source)
            return
    elif diff[0] == "delete-node" or diff[0] == "delete-tree":
        des_node = parse_tree_from_text(diff[2:])
        if des_node.value in match_dic12.keys():
            # find des_node in ast1
            father1 = bfs_search_father(ast1,des_node.value)
            des1 = bfs_search(father1,des_node.value)
            father1.children.remove(des1)
            father1.xml.remove(des1.xml)
            # find parral node in ast2
            father2 = bfs_search_father(ast2,match_dic12[des_node.value])
            des2 = bfs_search(father2,match_dic12[des_node.value])
            father2.children.remove(des2)
            father2.xml.remove(des2.xml)
            return
    elif diff[0] == "update-node":
        des_node = diff[2].strip()
        source = diff[-1].split(" by ")[-1]
        if des_node in match_dic12.keys():
            # find des_node in ast1
            des1 = bfs_search(ast1,des_node)
            # find parral node in ast2
            des2 = bfs_search(ast2,match_dic12[des_node])
            # update text in ast1
            des1.xml.text = source
            # update text in ast2
            des2.xml.text = get_newname(source,mapping_dict,{})
            return
    elif diff[0] == "move-node" or diff[0] == "move-tree":
        source = parse_tree_from_text(diff[2:-3])
        des_node = parse_tree_from_text([diff[-2]])
        if (des_node.value + "_" in match_dic12.keys() or des_node.value in match_dic12.keys()) and source.value in match_dic12.keys():
            if des_node.value + "_" in match_dic12.keys():
                des_node.value = des_node.value + "_"
            new_source = bfs_search(ast2,match_dic12[source.value])
            desRank = int(diff[-1].split(" ")[-1])
            source = bfs_search(ast1,source.value)
            source_ = bfs_search(ast1_,match_dic11_[source.value])
            father1 = bfs_search_father(ast1,source.value)
            father1.xml.remove(source.xml)
            father1.children.remove(source)
            father2 = bfs_search_father(ast2,match_dic12[source.value])
            father2.xml.remove(new_source.xml)
            father2.children.remove(new_source)

            #插入需要找到前后能够产生映射的地方
            if source.xml.tail != source_.xml.tail:
                source.xml.tail = source_.xml.tail
                new_source.xml.tail = source_.xml.tail
            
            des1 = bfs_search(ast1,des_node.value)
            des1.xml.insert(desRank,source.xml)
            des1.children.insert(desRank,source)
            #des2 = bfs_search(ast2,match_dic12[des_node.value])

            for i in range(desRank-1,-1,-1):
                if des1.children[i].value in match_dic12:
                    des2 = bfs_search_father(ast2,match_dic12[des1.children[i].value])
                    for j,child in enumerate(des2.children):
                        if match_dic12[des1.children[i].value] == child.value:
                            des2.xml.insert(j+1,new_source.xml)
                            des2.children.insert(j+1,new_source)
                            return
            for i in range(desRank+1,len(des1.children)):
                if des1.children[i].value in match_dic12:
                    des2 = bfs_search_father(ast2,match_dic12[des1.children[i].value])
                    for j,child in enumerate(des2.children):
                        if match_dic12[des1.children[i].value] == child.value:
                            des2.xml.insert(j,new_source.xml)
                            des2.children.insert(j,new_source)
                            return
            des2 = bfs_search(ast2,match_dic12[des_node.value])
            des2.xml.insert(0,new_source.xml)
            des2.children.insert(0,new_source)
            return



def gen_result(file_string1,
                file_string2,
                file_string1_,
                mapping_dict,
                use_docker,
                MATCHER_ID,
                TREE_GENERATOR_ID
                ):
    '''
    cfile_name1为架构a下的文件, cfile2_name2为架构b下的文件, cfile_name1_为cfile_name1修改后的文件
    取cfile1和cfile2的match部分, 取cfile1与cfile1_的diff部分
    '''
    start_time = time()

    with tempfile.NamedTemporaryFile(delete=True, mode='w', suffix='.cpp') as cfile1, \
        tempfile.NamedTemporaryFile(delete=True, mode='w', suffix='.cpp') as cfile1_, \
        tempfile.NamedTemporaryFile(delete=True, mode='w', suffix='.cpp') as cfile2:

        cfile1.write(file_string1)
        cfile1.flush()
        cfile1_.write(file_string1_)
        cfile1_.flush()
        cfile2.write(file_string2)
        cfile2.flush()

        ast1, _ = get_ast(cfile1.name,use_docker=use_docker,TREE_GENERATOR_ID=TREE_GENERATOR_ID)

        ast1_, _  = get_ast(cfile1_.name,use_docker=use_docker,TREE_GENERATOR_ID=TREE_GENERATOR_ID)

        ast2, _  = get_ast(cfile2.name,use_docker=use_docker,TREE_GENERATOR_ID=TREE_GENERATOR_ID)

        if use_docker:
            output11_ = subprocess.run(["docker","run","--rm","-v",cfile1.name+":/left.cc","-v",cfile1_.name+":/right.cc","gumtreediff/gumtree","textdiff","/left.cc", "/right.cc",
                                        "-m",MATCHER_ID,"-g", TREE_GENERATOR_ID],
                                        capture_output=True,text = True).stdout
            output12 = subprocess.run(["docker","run","--rm","-v",cfile1.name+":/left.cc","-v",cfile2.name+":/right.cc","gumtreediff/gumtree","textdiff","/left.cc", "/right.cc",
                                        "-m",MATCHER_ID,"-g", TREE_GENERATOR_ID],
                                        capture_output=True,text = True).stdout
        else:
            output11_ = subprocess.run(["gumtree","textdiff",cfile1.name, cfile1_.name,
                                        "-m",MATCHER_ID,"-g", TREE_GENERATOR_ID],
                                        capture_output=True,text = True).stdout
            output12 = subprocess.run(["gumtree","textdiff",cfile1.name, cfile2.name,
                                        "-m",MATCHER_ID,"-g", TREE_GENERATOR_ID],
                                        capture_output=True,text = True).stdout
            
        with tempfile.NamedTemporaryFile(delete=True, mode='w', suffix='.cpp') as xmlfile1, \
            tempfile.NamedTemporaryFile(delete=True, mode='w', suffix='.cpp') as xmlfile1_, \
            tempfile.NamedTemporaryFile(delete=True, mode='w', suffix='.cpp') as xmlfile2:
            
            subprocess.run(["srcml",cfile1.name,"-o",xmlfile1.name])
            xmlfile1.flush()
            xml_tree1 = ET.parse(xmlfile1.name).getroot()
            subprocess.run(["srcml",cfile1_.name,"-o",xmlfile1_.name])
            xmlfile1_.flush()
            xml_tree1_ = ET.parse(xmlfile1_.name).getroot()
            subprocess.run(["srcml",cfile2.name,"-o",xmlfile2.name])
            xmlfile2.flush()
            xml_tree2 = ET.parse(xmlfile2.name).getroot()
            init_ast(ast1,xml_tree1)
            init_ast(ast1_,xml_tree1_)
            init_ast(ast2,xml_tree2)

            # print("生成ast及diff耗时: {}s".format(time()-start_time))
            matches11_, diffs11_ = gumtree_parser(output11_)
            matches12, _= gumtree_parser(output12)
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
            #TODO：通过2—>1->1_的过程来补充能够映射到的节点的tail
            # mapping_dict12 = construct_mapping_dict(match_dic12)
            for diff in diffs11_:
                parse_diff(diff,ast1,ast1_,ast2,match_dic11_,match_dic12,mapping_dict)


            modify_comma(ast2.xml)


            with tempfile.NamedTemporaryFile(delete=True, mode='w', suffix='.xml') as xmlfile2_:
                ET.ElementTree(ast2.xml).write(xmlfile2_.name, encoding="utf-8", xml_declaration=True)
                xmlfile2_.flush()
                end_time = time()
                print("耗时: {}s".format(int(end_time-start_time)),end=" ")
                sys.stdout.flush()

                return subprocess.run(["srcml",xmlfile2_.name], capture_output=True,text = True).stdout




        # operations = []
        # #先对diff操作进行parse
        # diffOps = diff_parser(diffs11_,match_dic11_,ast1_)


        # diffOp_i = 0
        # while diffOp_i < len(diffOps):
        #     diffOp = diffOps[diffOp_i]
        #     diffOp_i = diffOp_i + 1
        #     if op == "insert-node" or op == "insert-tree":
        #         #位置
        #         if des_node in match_dic12:
        #             des = match_dic12[des_node]
        #         else:
        #             continue
        #         #在ast1,2中找到pos,根据其child找到位置
        #         des_node = bfs_search(ast1,des_node)

        #         # 找到插入节点的后一个节点, 进行映射, 如果能映射到, 则插入到后一个节点的前面
        #         # 找不到, 则找到插入节点的前一个节点, 进行映射, 如果能映射到, 则插入到前一个节点的后面
        #         # 全都找不到, 就放在最前面
        #         child_rank = desRank
        #         child_rank2 = -1
        #         start = -1
        #         for i in range(child_rank-1,-1,-1):
        #             if des_node.children[i].value != "VAL":
        #                 if des_node.children[i].value in match_dic12:
        #                     _,start = get_start_end(match_dic12[des_node.children[i].value])
        #                     break
        #         if start == -1:
        #             for i in range(child_rank,len(des_node.children)):
        #                 if des_node.children[i].value != "VAL":
        #                     if des_node.children[i].value in match_dic12:
        #                         start,_ = get_start_end(match_dic12[des_node.children[i].value])
        #                         break
        #         if start ==-1:
        #             start,_ = get_start_end(des)

        #         #处理向空参数列表中插入会插入在括号外的情况
        #         if des_node.children == [] and (get_type(des) == "parameter_list" or get_type(des) == "argument_list"):
        #             start = start + 1

        #         if move == False:
        #             #内容 需要找到存在于原代码片段的位置
        #             #进行简单的映射:先找到1_的同名变量, 进行 1->2 的映射
        #             content = map(bfs_search(ast1_,source.value),mapping_dict,{},file_string1_)
        #         else:
        #             # move本来的操作应该是copy file2中的内容到这里, 但是由于可能会对被move的内容进行操作, 所以不能简单地复制粘贴
        #             content = map(source,mapping_dict,mapping_dict12,file_string1_)
        #         if op == "insert-tree" or source.value.split(":")[0]=="comment":
        #             if get_type(source.value) == "argument" or get_type(source.value) == "parameter":
        #                     content =  ", " + content + ", "

        #             elif get_type(des_node)== "block" or get_type(des_node) == "unit" or get_type(des_node) == "block_content":
        #                 content =  "\n" + content + "\n"
        #             else:
        #                 content =  " " + content + " "

        #         des_node.children.insert(child_rank,TreeNode("VAL"))

        #         # 删除单行注释
        #         content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
        #         # 删除多行注释
        #         content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)

        #         operation = Operation(start,start,content)
        #         operation.rank = child_rank2
        #         operations.append(operation)
        #     elif op == "delete-node" or op == "delete-tree":
        #         if source.value in match_dic12:
        #             #删除结点
        #             des_node = bfs_search_father(ast1,source.value)
        #             r = 0
        #             des = match_dic12[source.value]
        #             for i in range(len(des_node.children)):
        #                 if des_node.children[i].value == source.value:
        #                     r = i

        #             start,end = get_start_end(des)
        #             operation = Operation(start,end,"")
        #             operation.rank = sys.maxsize
        #             operations.append(operation)
        #             # 在ast中删除节点
        #             des_node.children.pop(r)
        #         else:
        #             if diffOp_i < len(diffOps):
        #                 if diffOps[diffOp_i].id == id:
        #                     diffOp_i = diffOp_i + 1
        #     elif op == "update-node":
        #         if des_node in match_dic12:
        #             if re.match(r'//.*$',source) or re.match(r'/\*.*?\*/',source):
        #                 continue
        #             des = match_dic12[des_node]
        #             start,end = get_start_end(des)
        #             new_name = get_newname("name: "+source+" []",mapping_dict,mapping_dict12)
        #             if new_name != None:
        #                 operation = Operation(start,end,new_name)
        #             else:
        #                 operation = Operation(start,end,source)
        #             operations.append(operation)
        #     else:
        #         exit(206)
        # file_string2_ = replace(file_string2,operations)

        # # 处理整个文件中的 "," 相关的内容
        # file_string2_  = clean_parameter_list_in_file(file_string2_)


        # #删除所有以 “\”结尾的空行
        # file_string2_ = re.sub(r'^\s*\\\s*$', '', file_string2_,flags=re.MULTILINE)

        # end_time = time()
        # print("耗时: {}s".format(int(end_time-start_time)),end=" ")
        # sys.stdout.flush()

        # return file_string2_
