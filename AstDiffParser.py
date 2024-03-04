from get_ast import parse_tree_from_text
import copy

class DiffOp:
    def __init__(self,op):
        self.op = op
        self.source = None
        self.desNode = ""
        self.update = ""
        self.desRank = 0
        self.move = False
        self.id = -1

def bfs_search(root, target):
    queue = [root]
    while queue:
        node = queue.pop(0)
        if node.value == target:
            return node
        queue.extend(node.children)

def get_start_end(string):
    [start,end] = string.split(" ")[-1][1:-1].split(",")
    return int(start), int(end)

def fun(diffOps,match):
    for i in range(len(diffOps)):
        if diffOps[i].desNode != "":
            for j in range(len(diffOps)):
                if diffOps[j].source != None and (diffOps[j].op == "insert-tree" or diffOps[j].op == "insert-node"):
                    ## 没有处理在insert中delete的情况
                    node =  bfs_search(diffOps[j].source,diffOps[i].desNode)
                    if node != None:
                        if diffOps[i].op == "insert-tree" or diffOps[i].op == "insert-node":
                            node.children.insert(diffOps[i].desRank,diffOps[i].source)
                            diffOps[j].op = "insert-tree";
                        elif diffOps[i].op == "update-tree" or diffOps[i].op == "update-node":
                            if diffOps[i].desNode in match:
                                node.value = match[diffOps[i].desNode]
                        elif diffOps[i].op == "delete-tree" or diffOps[i].op == "delete-node":
                            exit(210)
                        diffOps.pop(i)
                        return diffOps,False
                    if diffOps[i].desNode in match:
                        node = bfs_search(diffOps[j].source,match[diffOps[i].desNode])
                        if node != None:
                            if diffOps[i].op == "update-tree" or diffOps[i].op == "update-node":
                                pass
                            else:
                                exit(220)
                            diffOps.pop(i)
                            return diffOps,False
                        
    for i in range(len(diffOps)):
        if diffOps[i].source != None and (diffOps[i].op == "delete-tree" or diffOps[i].op == "delete-node"):
            for j in range(len(diffOps)):
                if j != i and diffOps[j].source != None and (diffOps[j].op == "delete-tree" or diffOps[j].op == "delete-node"):
                    s1,e1 = get_start_end(diffOps[i].source.value)
                    s2,e2 = get_start_end(diffOps[j].source.value)
                    if s2<=s1 and e1<=e2:
                        diffOps.pop(i)
                        return diffOps,False
    return diffOps,True

def diff_parser(diffs,match):
    diffOps = []
    id = 0
    for diff in diffs:
        if diff[0] == "insert-node" :
            diffOp = DiffOp("insert-node")
            diffOp.source = parse_tree_from_text(diff[2:-3])
            diffOp.desNode = diff[-2].strip()
            diffOp.desRank = int(diff[-1].split(" ")[-1])
            diffOp.id = id
            diffOps.append(diffOp)
        elif diff[0] == "insert-tree":
            diffOp = DiffOp("insert-tree")
            diffOp.source = parse_tree_from_text(diff[2:-3])
            diffOp.desNode = diff[-2].strip()
            diffOp.desRank = int(diff[-1].split(" ")[-1])
            diffOp.id = id
            diffOps.append(diffOp)
        elif diff[0] == "delete-node":
            diffOp = DiffOp("delete-node")
            diffOp.source = parse_tree_from_text(diff[2:])
            diffOp.id = id
            diffOps.append(diffOp)
        elif diff[0] == "delete-tree":
            diffOp = DiffOp("delete-tree")
            diffOp.source = parse_tree_from_text(diff[2:])
            diffOp.id = id
            diffOps.append(diffOp)
        elif diff[0] == "update-node":
            diffOp = DiffOp("update-node")
            diffOp.desNode = diff[2].strip()
            diffOp.update = diff[-1].split(" by ")[-1]
            diffOp.id = id
            diffOps.append(diffOp)
        elif diff[0] == "move-node":
            diffOp2 = DiffOp("delete-node")
            diffOp2.source = parse_tree_from_text(diff[2:-3])
            diffOp2.id = id
            diffOps.append(diffOp2)
            diffOp1 = DiffOp("insert-node")
            diffOp1.source = copy.deepcopy(diffOp2.source)
            queue = [diffOp1.source]
            while queue:
                node = queue.pop(0)
                if node.value in match:
                    node.value = match[node.value]
                queue.extend(node.children)
            diffOp1.desNode = diff[-2].strip()
            diffOp1.desRank = int(diff[-1].split(" ")[-1])
            diffOp1.id = id
            diffOps.append(diffOp1)
        elif diff[0] == "move-tree":
            diffOp2 = DiffOp("delete-tree")
            diffOp2.source = parse_tree_from_text(diff[2:-3])
            diffOp2.id = id
            diffOps.append(diffOp2)
            diffOp1 = DiffOp("insert-tree")
            diffOp1.source = copy.deepcopy(diffOp2.source)
            queue = [diffOp1.source]
            while queue:
                node = queue.pop(0)
                if node.value in match:
                    node.value = match[node.value]
                queue.extend(node.children)
            diffOp1.desNode = diff[-2].strip()
            diffOp1.desRank = int(diff[-1].split(" ")[-1])
            diffOp1.move = True
            diffOp1.id = id
            diffOps.append(diffOp1)
        else:
            exit(300)
        id = id + 1
    while(1):
        diffOps,Break = fun(diffOps,match)
        if Break:
            break
    return diffOps