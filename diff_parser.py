from get_ast import parse_tree_from_text

class DiffOp:
    def __init__(self,op):
        self.op = op
        self.source = None
        self.desNode = ""
        self.update = ""
        self.desRank = 0

def bfs_search(root, target):
    queue = [root]
    while queue:
        node = queue.pop(0)
        if node.value == target:
            return node
        queue.extend(node.children)
        
def fun(diffOps):
    for i in range(len(diffOps)):
        if diffOps[i].desNode != "":
            for j in range(len(diffOps)):
                if diffOps[j].source != None:
                    ## TODO 这里只处理了迭代insert的情况，没有处理在insert中删除的情况（如move)
                    node =  bfs_search(diffOps[j].source,diffOps[i].desNode)
                    if node != None:
                        if diffOps[i].op == "insert-tree" or diffOps[i].op == "insert-node":
                            node.children.insert(diffOps[i].desRank,diffOps[i].source)
                            diffOps[j].op = "insert-tree";
                        elif diffOps[i].op == "update-tree" or diffOps[i].op == "update-node":
                            lst = node.value.split(" ")
                            lst[1] = diffOps[i].update
                            node.value = lst[0]
                            lst.pop(0)
                            while len(lst)!=0:
                                node.value = node.value + " " + lst[0]
                                lst.pop(0) 
                            a = 0                           
                        elif diffOps[i].op == "update-tree" or diffOps[i].op == "update-node":
                            exit(210)
                        diffOps.pop(i)
                        return diffOps,False
    return diffOps,True

def diff_parser(diffs,match,ast):
    diffOps = []
    for diff in diffs:
        if diff[0] == "insert-node" :
            diffOp = DiffOp("insert-node")
            diffOp.source = parse_tree_from_text(diff[2:-3])
            diffOp.desNode = diff[-2].strip()
            diffOp.desRank = int(diff[-1].split(" ")[-1])
            diffOps.append(diffOp)
        elif diff[0] == "insert-tree":
            diffOp = DiffOp("insert-tree")
            diffOp.source = parse_tree_from_text(diff[2:-3])
            diffOp.desNode = diff[-2].strip()
            diffOp.desRank = int(diff[-1].split(" ")[-1])
            diffOps.append(diffOp)
        elif diff[0] == "delete-node":
            diffOp = DiffOp("delete-node")
            diffOp.source = parse_tree_from_text(diff[2:])
            diffOps.append(diffOp)
        elif diff[0] == "delete-tree":
            diffOp = DiffOp("delete-tree")
            diffOp.source = parse_tree_from_text(diff[2:])
            diffOps.append(diffOp)
        elif diff[0] == "update-node":
            diffOp = DiffOp("update-node")
            diffOp.desNode = diff[2].strip()
            diffOp.update = diff[-1].split(" ")[-1]
            diffOps.append(diffOp)
        elif diff[0] == "move-node":
            diffOp1 = DiffOp("insert-node")
            diffOp1.source = bfs_search(ast,match[diff[2].strip()])
            diffOp1.desNode = diff[-2].strip()
            diffOp1.desRank = int(diff[-1].split(" ")[-1])
            diffOps.append(diffOp1)
            diffOp2 = DiffOp("delete-node")
            diffOp2.source = parse_tree_from_text(diff[2:-3])
            diffOps.append(diffOp2)
        elif diff[0] == "move-tree":
            diffOp2 = DiffOp("delete-tree")
            diffOp2.source = parse_tree_from_text(diff[2:-3])
            diffOps.append(diffOp2)
            diffOp1 = DiffOp("insert-tree")
            #替换为match后的值
            diffOp1.source = bfs_search(ast,match[diff[2].strip()])
            diffOp1.desNode = diff[-2].strip()
            diffOp1.desRank = int(diff[-1].split(" ")[-1])
            diffOps.append(diffOp1)
        else:
            exit(300)
    while(1):
        diffOps,Break = fun(diffOps)
        if Break:
            break
    return diffOps