import tree_sitter_cpp as tscpp
from tree_sitter import Language, Parser


def bfs_search(root,type):
    queue = []
    queue.extend(root.children)
    while queue:
        child_node = queue.pop()
        if child_node.type == type:
            return child_node
        else:
            queue.extend(child_node.children)
    return None

def byte2txt(byte):
    return str(byte,"utf-8")

def identifiers(node):
    if node == None:
        return None
    name = identifier(node)
    if not name:
        name = operator_name(node)
    if not name:
        name = operator_cast(node)
    if not name:
        name = qualified_identifier(node)
    if not name:
        name = field_identifier(node)
    return name

def declarators(node):
    if node == None:
        return None
    child = function_declarator(node)
    if not child:
        child = destructor_name(node)
    if not child:
        child = pointer_declarator(node)
    if not child:
        child = reference_declarator(node)
    return child

def identifier(node):
    if node == None:
        return None
    for child in node.children:
        if child.type == "identifier":
            return byte2txt(child.text)

def operator_name(node):
    if node == None:
        return None
    for child in node.children:
        if child.type == "operator_name":
            return byte2txt(child.text)

def operator_cast(node):
    if node == None:
        return None
    for child in node.children:
        if child.type == "operator_cast":
            return byte2txt(child.text)

def qualified_identifier(node):
    if node == None:
        return None
    for child in node.children:
        if child.type == "qualified_identifier":
            return byte2txt(child.text)

def field_identifier(node):
    if node == None:
        return None
    for child in node.children:
        if child.type == "field_identifier":
            return byte2txt(child.text)

def function_declarator(node):
    if node == None:
        return None
    for child in node.children:
        if child.type == "function_declarator":
            return child

def destructor_name(node):
    if node == None:
        return None
    for child in node.children:
        if child.type == "destructor_name":
            return child

def pointer_declarator(node):
    if node == None:
        return None
    for child in node.children:
        if child.type == "pointer_declarator":
            return child

def reference_declarator(node):
    if node == None:
        return None
    for child in node.children:
        if child.type == "reference_declarator":
            return child

def print_tree(node, depth, file):
    if node is None:
        return
    if node.children == []:
        file.write("  " * depth + str(node.type) + " " + byte2txt(node.text) + "\n")
    else:
        file.write("  " * depth + str(node.type) + "\n")

    for child in node.children:
        print_tree(child, depth + 1, file)


def save_tree_to_txt(root, filename):
    with open(filename, 'w') as file:
        print_tree(root, 0, file)



def extract_unit(code):
    CPP_LANGUAGE = Language(tscpp.language())

    parser = Parser(CPP_LANGUAGE)
    tree = parser.parse(bytes(code,"utf-8"))
    root_node = tree.root_node

    # save_tree_to_txt(root_node,"tree.txt")
    units = []
    # 为了确定起始行
    code = code.split("\n")
    queue = []
    queue.extend(root_node.children)
    while queue:
        node = queue.pop()
        if node.type == "function_definition":
            content = byte2txt(node.text)
            name = None
            name = identifiers(node)
            if not name:
                name = identifiers(declarators(node))
            if not name:
                name = identifiers(declarators(declarators(node)))
            if not name:
                name = identifiers(declarators(declarators(declarators(node))))
            if not name:
                name = identifiers(declarators(declarators(declarators(declarators(node)))))
            if not name:
                name = identifiers(declarators(declarators(declarators(declarators(declarators(node))))))
            if not name:
                exit(100)
            name_and_para = content.replace(str(node.children[-1].text,"utf-8"),"")
            units.append({"name":name,"content":content,"name_and_para":name_and_para})
        elif node.type == "class_specifier":
            try:
                name = byte2txt(node.children[1].text)
                content = byte2txt(node.text)
                units.append({"name":name,"content":content,"name_and_para":""})
            except:
                exit(100)
        elif node.type == "struct_specifier":
            try:
                name = byte2txt(node.children[1].text)
                content = byte2txt(node.text)
                units.append({"name":name,"content":content,"name_and_para":""})
            except:
                exit(100)

        elif node.type == "enum_specifier":
            try:
                name = byte2txt(node.children[1].text)
                if name == "class":
                    name = byte2txt(node.children[2].text)
                content = byte2txt(node.text)
                units.append({"name":name,"content":content,"name_and_para":""})
            except:
                exit(100)
        # elif node.type == "expression_statement":
        #     try:
        #         content = byte2txt(node.text)
        #         units.append({"type":"struct","name":content,"content":content,"name_and_para":content})
        #     except:
        #         exit(100)

        else:
            queue.extend(node.children)
    return units
