import json
from utils.ast_utils import *
from tqdm import tqdm
from utils.arch_utils import remove_archwords,has_archwords
import tempfile
import subprocess
import os

versions = ["519ee9d66cd", # 9.10.0
        "dc97b450587", # 10.0
        "d571cf7c2f4", # 10.1.0
        "a0204ff9aea", # 10.2.0
        "01af3a6529a", # 10.3.0.1
        "24226735269", #10.4.0.1
        "e9d54c53d14", #10.5.0.2
        "6df7f9e416d", # 10.6.0
        "cfe9945828d", # 10.7.0
        "78dc1fc670f", #10.8.0
        "5be28a22d10", #10.9.0
        "d7f28a43690", # 11.0.0
        "5b84df0b994", # 11.1.0
        "d60b62b0afb", # 11.2.0
        "49a080e6ff5", # 11.3.0
        "6038c5bb8a8", # 11.4.0
        "ae4d3975ab0", # 11.5.0
        "6dcdb718b6d", # 11.6.0
        "2dcf2bc02cc", # 11.7.0
        "78017dccc38", # 11.8.0
        "8997fd159a8", # 11.9.0
        "ef0e120e97a", # 12.0.0
        "811b7e772fa", # 12.1.0
        "3130a66a9d9", # 12.2.0
        "40d669e1505", # 12.3.0
        "8ddb5aeb866", # 12.4.0
        "6c1c3de6422", # 12.5.0
        "a56fcee3ed5", # 12.6.0
        "ca4889a4ab8", # 12.7.0
        "4699435f7bb", # 12.8.0
        "70ccb6965dd", # 12.9.0
        ]
MATCHER_ID="gumtree-hybrid"
TREE_GENERATOR_ID="cpp-srcml"
mapping = {}
if not os.path.exists("mapping"):
    os.mkdir("mapping")
for version in versions:
    with open('match/match_' + version + '.json', 'r') as json_file:
        block_sets = json.load(json_file)
        arch_dic = {"arm":0,"arm64":1,"riscv32":2,"riscv64":3,"mips":4,"ia32":5,"x64":6,"loong":7,"s390":8,"ppc":9}

        similarity = []
        #riscv64
        j = 0
        for [file_type,content] in tqdm(block_sets):
            similar = []
            for set in tqdm(content):
                with tempfile.NamedTemporaryFile(delete=True, mode='w', suffix='.cpp') as riscv_block:
                    if set[3] == []:
                        continue
                    riscv_block.write("\n".join(set[3]))
                    riscv_block.flush()
                    # _, ast1_nodenum = get_ast(riscv_block.name,use_docker=True,TREE_GENERATOR_ID=TREE_GENERATOR_ID)
                    # if ast1_nodenum == 1:
                    #     a = 0
                    simi = [{} for _ in range(10)]
                    for i,block in enumerate(set):
                        if i != 2 and i != 3 and block != []:
                            with tempfile.NamedTemporaryFile(delete=True, mode='w', suffix='.cpp') as other_block:

                                other_block.write("\n".join(block))
                                other_block.flush()
                                result = subprocess.run(["gumtree","textdiff",other_block.name, riscv_block.name,
                                                                        "-m",MATCHER_ID,"-g", TREE_GENERATOR_ID],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
                                
                                # _, ast2_nodenum = get_ast(other_block.name,use_docker=True,TREE_GENERATOR_ID=TREE_GENERATOR_ID)
                                # result = subprocess.run(["docker","run","--rm","-v",other_block.name+":/left.cc","-v",riscv_block.name+":/right.cc","gumtreediff/gumtree","textdiff","/left.cc","/right.cc","-m",MATCHER_ID,"-g",TREE_GENERATOR_ID],
                                #     stdout=subprocess.PIPE,
                                #     stderr=subprocess.PIPE)
                                matches, _ = gumtree_parser(result.stdout.decode())
                                match_dic = {}
                                for match in matches:
                                    if match[1]!="---":
                                        exit(201)
                                    match_dic[match[2]] = match[3]
                                simi[i] = match_dic
                similar.append(simi)
            similarity.append([file_type,similar])
        with open('mapping/mapping_'+version+'.json', 'w') as json_file:
            json.dump(similarity,json_file,indent=4)