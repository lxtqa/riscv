import json
import os
from gumtree_parser import gumtree_parser
from tqdm import tqdm
from arc_utils import remove_arcwords,has_arcwords

def main(scope):
    if not os.path.exists("../similarity/"):
        os.mkdir("../similarity/")

    MATCHER_ID="gumtree-simple-id"
    TREE_GENERATOR_ID="cs-srcml"
    with open('functions.json', 'r') as json_file:
        functions = json.load(json_file)
        target = {}
        arc_related_functions = []
        arc_not_related_functions = []
        for function in functions:
            if has_arcwords(function["file_name"]):
                arc_related_functions.append(function)
            else:
                arc_not_related_functions.append(function)

        
        
        if scope == "self_check":
            function_dic = {}
            for function in arc_related_functions:
                file_name_template = remove_arcwords(function["file_name"])
                function_name_template = remove_arcwords(function["name"])
                if file_name_template in function_dic.keys():
                    if function_name_template in function_dic[file_name_template]:
                        function_dic[file_name_template][function_name_template].append(function)
                    else:
                        function_dic[file_name_template][function_name_template] = [function]
                else:
                    function_dic[file_name_template] = {function_name_template:[function]}

            
            rank = 0
            for file_name_template in tqdm(function_dic.keys()):
                for function_name_template in tqdm(function_dic[file_name_template].keys()):
                    lst = []
                    function_set = function_dic[file_name_template][function_name_template]
                    total_r = 0
                    for i in range(len(function_set)):
                        target = function_set[i]
                        f = open("../test/target.cc","w")
                        f.write(target["content"])
                        f.close()
                        for j in range(i+1,len(function_set)):
                            function = function_set[j]
                            f = open("../test/tmp.cc","w")
                            f.write(function["content"])
                            f.close()
                            os.system("gumtree textdiff {} {} -m {} -g {} -M bu_minsim 0.5 > {}".format(
                                "../test/target.cc", "../test/tmp.cc", MATCHER_ID, TREE_GENERATOR_ID, "../test/diff.cc"))
                            matches, _= gumtree_parser("../test/diff.cc")
                            # unit总能匹配到
                            r = (len(matches) - 1) / ( target["astnode_num"] - (len(matches) - 1) + function["astnode_num"] )
                            if r > 1: 
                                continue
                            total_r += r
                            lst.append([r,i,j])
            
            
                    sorted_list = sorted(lst, key=lambda x: x[0],reverse=True)
                    f = open("../self_similarity/result{}.txt".format(rank),"w")
                    if len(function_set) != 1:
                        f.write("average_similarity = {}\n".format( total_r * 2 /  ( len(function_set) * (len(function_set) - 1 ) ) ) )
                    else:
                        f.write("average_similarity = {}\n".format( total_r ) )
                    for i in range(len(function_set)):
                        f.write("{} {} {} {} {}\n".format(i,function_set[i]["astnode_num"],function_set[i]["name"],function_set[i]["file_name"],function_set[i]["content"].replace("\n"," ")))
                    for item in sorted_list:
                        f.write("{} {} {}\n".format(item[0],item[1],item[2]))
                    f.close()
                    rank = rank+1

        
        else:
            i = 0
            for target in arc_related_functions:
                
                f = open("../test/target.cc","w")
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
                            f = open("../test/tmp.cc","w")
                            f.write(function["content"])
                            f.close()
                            os.system("gumtree textdiff {} {} -m {} -g {} -M bu_minsim 0.5 > {}".format(
                                "../test/target.cc", "../test/tmp.cc", MATCHER_ID, TREE_GENERATOR_ID, "../test/diff.cc"))
                            matches, _= gumtree_parser("../test/diff.cc")
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
                    f = open("../test/tmp.cc","w")
                    f.write(function["content"])
                    f.close()
                    os.system("gumtree textdiff {} {} -m {} -g {} -M bu_minsim 0.5 > {}".format(
                        "../test/target.cc", "../test/tmp.cc", MATCHER_ID, TREE_GENERATOR_ID, "../test/diff.cc"))
                    matches, _= gumtree_parser("../test/diff.cc")
                    # unit总能匹配到
                    r = (len(matches) - 1) / ( target["astnode_num"] - (len(matches) - 1) + function["astnode_num"] )
                    lst.append([r,function["file_name"],function["content"]])
                
                sorted_list = sorted(lst, key=lambda x: x[0],reverse=True)
                f = open("../similarity/result{}.txt".format(i),"w")
                f.write("{} {}\n".format(target["file_name"],target["content"].replace("\n"," ")))
                for item in sorted_list:
                    f.write("{} {} {}\n".format(item[0],item[1],item[2].replace("\n"," ")))
                f.close()
                i= i+1
        
        
if __name__ == "__main__":
    
    main("check")
                


