import os

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


def get_ast(cpp_file_name,rm_tempfile):
    ast_file_name = "./ast.txt"
    os.system("docker run -v {}:/left.cc gumtreediff/gumtree parse /left.cc > {}".format(cpp_file_name,ast_file_name))
    ast_file = open(ast_file_name,"r");
    tree_text = ast_file.readlines()
    root = parse_tree_from_text(tree_text)
    if rm_tempfile:
        os.remove(ast_file_name)
    return root

if __name__ == "__main__":
    cpp_file_name = "./test1.cpp"
    rm_tempfile = False
    root = get_ast(cpp_file_name,rm_tempfile=rm_tempfile)
    print_tree(root)
