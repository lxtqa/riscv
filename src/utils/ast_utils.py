import re
import subprocess

MATCHER_ID="gumtree-hybrid"
TREE_GENERATOR_ID="cpp-srcml"

def get_start_end(string):
    try:
        [start,end] = string.split(" ")[-1][1:-1].split(",")
        return int(start), int(end)
    except:
        try:
            string = string.value
            [start,end] = string.split(" ")[-1][1:-1].split(",")
            return int(start), int(end)
        except:
            pass

def get_name(string):
    try:
        if len(string.split(" ")) == 3:
            return string.split(" ")[1]
        else:
            return None
    except:
        try:
            string = string.value
            if len(string.split(" ")) == 3:
                return string.split(" ")[1]
            else:
                return None
        except:
            pass

def get_type(string):
    try:
        return string.split(" ")[0]
    except:
        try:
            return string.value.split(" ")[0]
        except:
            pass

def count_starting_spaces(s):
    return len(s) - len(s.lstrip())

class TreeNode:
    def __init__(self, value):
        self.value = value
        self.children = []

def parse_tree_from_text(text_lines):
    def build_tree_helper(lines, level):
        if not lines:
            return None

        line = lines[0]
        curr_level = count_starting_spaces(line) // 4

        if curr_level < level:
            return None

        node = TreeNode(line.strip())
        lines.pop(0)
        while lines and curr_level == level:
            child = build_tree_helper(lines, level + 1)
            if child:
                node.children.append(child)
            else:
                return node
        return node

    return build_tree_helper(text_lines, 0)

def print_tree(node, indent=0):
    print('    ' * indent + node.value)
    for child in node.children:
        print_tree(child, indent + 1)


def merge_lines(lines):
    i = 0
    merged = []
    tmp_line = ""
    while i < len(lines):
        line = lines[i]
        pattern = re.compile(r'.+\[\d+,\d+\]$')
        # 进行匹配
        tmp_line = tmp_line + line
        if pattern.match(line):
            merged.append(tmp_line)
            tmp_line = ""
        i = i+1
    return merged


def get_ast(cpp_file_name,use_docker,TREE_GENERATOR_ID):
    if use_docker:
        output = subprocess.run(["docker","run","--rm","-v",cpp_file_name+":/left.cc","gumtreediff/gumtree","parse","/left.cc","-g",TREE_GENERATOR_ID],capture_output=True,text = True)
    else:
        output = subprocess.run(["gumtree","parse",cpp_file_name,"-g",TREE_GENERATOR_ID],capture_output=True,text = True)
    tree_text = output.stdout.split("\n")
    root = parse_tree_from_text(merge_lines(tree_text))
    return root,len(tree_text)

def gumtree_parser(txtfile):
    '''
    对gumtree txtdiff生成的txt文件进行parse,获取match关系到一个list中, 获取diff关系到另一个list
    返回这两个list
    '''
    content=txtfile.split("\n")
    if content[-1] == "":
        content = content[:-1]
    line_rank = 0
    matches = []
    diffs = []
    operation = []
    while 1:
        if line_rank >= len(content):
            if operation!=[]:
                if operation[0] == 'match':
                    matches.append(operation.copy())
                else:
                    diffs.append(operation.copy())
                operation = []
            break
        line = content[line_rank].replace("\n","")
        if line == "===":
            if operation!=[]:
                if operation[0] == 'match':
                    matches.append(operation.copy())
                else:
                    diffs.append(operation.copy())
                operation = []
        else:
            operation.append(line)
        line_rank = line_rank+1
    return matches,diffs

