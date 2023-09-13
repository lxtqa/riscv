from tree_sitter import Language, Parser
import json


def tree_to_token_index(root_node,code):
    if (len(root_node.children) == 0 or root_node.type.find('string') != -1) and root_node.type != 'comment' and root_node.type != '\n':
        start_point = root_node.start_point
        end_point = root_node.end_point
        if start_point[0] == end_point[0]:
            s = code[start_point[0]][start_point[1]:end_point[1]]
        else:
            s = ""
            s += code[start_point[0]][start_point[1]:]
            for i in range(start_point[0]+1, end_point[0]):
                s += code[i]
            s += code[end_point[0]][:end_point[1]]
        start_rank = start_point[1]
        end_rank = end_point[1]
        for i in range(0,start_point[0]):
            start_rank += len(code[i])+1
        for i in range(0,end_point[0]):
            end_rank += len(code[i])+1
        return [root_node.type,s,(start_rank, end_rank)]
    elif root_node.type == 'comment':
        return []
    else:
        code_tokens = []
        for child in root_node.children:
            child_token_index = tree_to_token_index(child,code)
            if child_token_index != []:
                code_tokens.append(child_token_index)
        start_point = root_node.start_point
        end_point = root_node.end_point
        start_rank = start_point[1]
        end_rank = end_point[1]
        for i in range(0,start_point[0]):
            start_rank += len(code[i])+1
        for i in range(0,end_point[0]):
            end_rank += len(code[i])+1
        return [root_node.type,code_tokens,(start_rank, end_rank)]
        
def get_ast(cfile_name):
    # 声明CPP代码解析器
    CPP_LANGUAGE = Language('build/my-languages.so', 'cpp')
    cpp_parser = Parser()
    cpp_parser.set_language(CPP_LANGUAGE)

   # cfile_name = "/Users/yuhaonan/Desktop/cpps/V8/v8/src/wasm/baseline/arm/liftoff-assembler-arm.h"
    cfile = open(cfile_name,"r")
    cpp_code_snippet = cfile.read()
    cfile.close()

    # 完成解析，获取根节点
    tree = cpp_parser.parse(bytes(cpp_code_snippet, "utf8"))
    root_node = tree.root_node

    # 获取token对应的位置
    cpp_loc = cpp_code_snippet.split('\n')
    tokens_index = tree_to_token_index(root_node,cpp_loc)

    return json.dumps(tokens_index)
        
if __name__ == '__main__':
    # 声明CPP代码解析器
    CPP_LANGUAGE = Language('build/my-languages.so', 'cpp')
    cpp_parser = Parser()
    cpp_parser.set_language(CPP_LANGUAGE)

   # cfile_name = "/Users/yuhaonan/Desktop/cpps/V8/v8/src/wasm/baseline/arm/liftoff-assembler-arm.h"
    cfile_name = "./test1_.cpp"
    cfile = open(cfile_name,"r")
    cpp_code_snippet = cfile.read()
    cfile.close()

    # 完成解析，获取根节点
    tree = cpp_parser.parse(bytes(cpp_code_snippet, "utf8"))
    root_node = tree.root_node

    # 获取token对应的位置
    cpp_loc = cpp_code_snippet.split('\n')
    tokens_index = tree_to_token_index(root_node,cpp_loc)

    file = open("ast.txt","w")
    file.write(json.dumps(tokens_index))
    file.close()

