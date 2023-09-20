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


def get_ast(cpp_file_name,ast_file_name):
    os.system("./gumtree/gumtree parse "+cpp_file_name+" > " + ast_file_name)
    ast_file = open(ast_file_name,"r");
    # 示例用法
    # tree_text = [
    #     "Root",
    #     "    Child 1",
    #     "        Grandchild 1",
    #     "        Grandchild 2",
    #     "    Child 2",
    #     "        Grandchild 3",
    #     "        Grandchild 4",
    #     "            Great Grandchild 1",
    #     "    Child 3",
    # ]
    tree_text = ast_file.readlines()
    root = parse_tree_from_text(tree_text)
    os.remove(ast_file_name)
    return root

if __name__ == "__main__":
    ast_file_name = "./ast_tree.txt"
    cpp_file_name = "./test1.cpp"
    root = get_ast(cpp_file_name,ast_file_name)
    print_tree(root)
