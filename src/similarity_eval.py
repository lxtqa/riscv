import json
import os
from gumtree_parser import gumtree_parser
from tqdm import tqdm
from utils.arc_utils import remove_arcwords,has_arcwords

def bfs_get_num(root):
    queue = [root]
    num = 0
    while queue:
        node = queue.pop(0)
        queue.extend(node.children)
        num = num + 1
    return num

def main():
    if not os.path.exists("./similarity/"):
        os.mkdir("./similarity/")

    MATCHER_ID="gumtree-simple-id"
    TREE_GENERATOR_ID="cs-srcml"
    with open('hunks.json', 'r') as json_file:
        functions = json.load(json_file)
        target = {}
        arc_related_functions = []
        arc_not_related_functions = []
        for function in functions:
            if has_arcwords(function["file_name"]):
                arc_related_functions.append(function)
            else:
                arc_not_related_functions.append(function)

            i = 0
            for target in arc_related_functions:
                f = open("./test/target.cc","w")
                f.write(target["content"])
                f.close()
                lst = []
                min_r = 1
                found = False
                for function in arc_related_functions:
                    if function["file_name"] != target["file_name"]:
                        #需要去除架构关键词然后评判
                        if remove_arcwords(function["name"]) == remove_arcwords(target["name"]):
                            found = True
                            f = open("./test/tmp.cc","w")
                            f.write(function["content"])
                            f.close()
                            os.system("gumtree textdiff {} {} -m {} -g {} -M bu_minsim 0.5 > {}".format(
                                "./test/target.cc", "./test/tmp.cc", MATCHER_ID, TREE_GENERATOR_ID, "./test/diff.cc"))
                            matches, _= gumtree_parser("./test/diff.cc")
                            # unit总能匹配到
                            r = (len(matches) - 1) / ( target["astnode_num"] - (len(matches) - 1) + function["astnode_num"] )
                            if r < min_r:
                                min_r = r

                if not found:
                    continue
                print(target["file_name"])

                for function in tqdm(functions):
                    if function["astnode_num"] > target["astnode_num"]:
                        if target["astnode_num"] / function["astnode_num"] < min_r:
                            continue
                    else:
                        if function["astnode_num"] / target["astnode_num"] < min_r:
                            continue
                    f = open("./test/tmp.cc","w")
                    f.write(function["content"])
                    f.close()
                    os.system("gumtree textdiff {} {} -m {} -g {} -M bu_minsim 0.5 > {}".format(
                        "./test/target.cc", "./test/tmp.cc", MATCHER_ID, TREE_GENERATOR_ID, "./test/diff.cc"))
                    matches, _= gumtree_parser("./test/diff.cc")
                    # unit总能匹配到
                    r = (len(matches) - 1) / ( target["astnode_num"] - (len(matches) - 1) + function["astnode_num"] )
                    lst.append([r,function["file_name"],function["content"]])

                sorted_list = sorted(lst, key=lambda x: x[0],reverse=True)
                f = open("./similarity/result{}.txt".format(i),"w")
                f.write("{} {}\n".format(target["file_name"],target["content"].replace("\n"," ")))
                for item in sorted_list:
                    f.write("{} {} {}\n".format(item[0],item[1],item[2].replace("\n"," ")))
                f.close()
                i= i+1

if __name__ == "__main__":
    main()



