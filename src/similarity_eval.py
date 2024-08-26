import json
from gumtree_parser import gumtree_parser
from utils.ast_utils import get_ast
from tqdm import tqdm
from utils.arc_utils import remove_arcwords,has_arcwords
import tempfile
import subprocess
import os

def bfs_get_num(root):
    queue = [root]
    num = 0
    while queue:
        node = queue.pop(0)
        queue.extend(node.children)
        num = num + 1
    return num

def main():
    MATCHER_ID="gumtree-simple-id"
    TREE_GENERATOR_ID="cs-srcml"
    if not os.path.exists("./similarity"):
        os.mkdir("./similarity")
    with open('match.json', 'r') as json_file:
        hunk_sets = json.load(json_file)
        arch_dic = {"arm":0,"arm64":1,"riscv32":2,"riscv64":3,"mips":4,"ia32":5,"x64":6,"loong":7,"s390":8,"ppc":9}
        chart = []

        for hunk_set in hunk_sets:
            file_type = remove_arcwords(hunk_set[0][0])
            content = []
            for hunks in hunk_set[1]:
                lst = [[] for _ in range(10)]
                for hunk in hunks:
                    if has_arcwords(hunk["file"]) == "riscv":
                        lst[2]=hunk["content"]
                        lst[3]=hunk["content"]
                    else:
                        lst[arch_dic[has_arcwords(hunk["file"])]]=hunk["content"]
                content.append(lst)
            chart.append([file_type,content])


        similarity = []
        #riscv64
        j = 0
        for [file_type,content] in tqdm(chart):
            similar = []
            for set in tqdm(content):
                with tempfile.NamedTemporaryFile(delete=True, mode='w', suffix='.cpp') as riscv_hunk:
                    riscv_hunk.write("\n".join(set[3]))
                    riscv_hunk.flush()
                    _, ast1_nodenum = get_ast(riscv_hunk.name,use_docker=True,TREE_GENERATOR_ID=TREE_GENERATOR_ID)
                    if ast1_nodenum == 1:
                        a = 0
                    simi = []
                    for i,hunk in enumerate(set):
                        if i != 2 and i != 3:
                            with tempfile.NamedTemporaryFile(delete=True, mode='w', suffix='.cpp') as other_hunk:

                                other_hunk.write("\n".join(hunk))
                                other_hunk.flush()

                                _, ast2_nodenum = get_ast(other_hunk.name,use_docker=True,TREE_GENERATOR_ID=TREE_GENERATOR_ID)
                                result = subprocess.run(["docker","run","--rm","-v",riscv_hunk.name+":/left.cc","-v",other_hunk.name+":/right.cc","gumtreediff/gumtree","textdiff","/left.cc","/right.cc","-m",MATCHER_ID,"-g",TREE_GENERATOR_ID,"-M","bu_minsim","0.5"],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
                                matches, _= gumtree_parser(result.stdout.decode())
                                # unit总能匹配到
                                if ast1_nodenum - 1 + ast2_nodenum - 1 - (len(matches) - 1) == 0:
                                    r = 0
                                else:
                                    r = (len(matches) - 1) / ( ast1_nodenum - 1 + ast2_nodenum - 1 - (len(matches) - 1) )
                                simi.append(r)
                        else:
                            simi.append(1.0)
                similar.append([ast1_nodenum,simi])
            similarity.append([file_type,similar])
            # with open("./similarity/"+str(j)+".json","w") as simFile:
            #     json.dump(similar,simFile,indent=4)
            j = j+1
    # with open("similarity.json","w") as simFile:
    #     json.dump(similarity,simFile,indent=4)



if __name__ == "__main__":
    main()



