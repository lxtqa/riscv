
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


if __name__ == "__main__":
    pass