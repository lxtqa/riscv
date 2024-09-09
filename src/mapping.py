import json
from utils.ast_utils import *
from tqdm import tqdm
from utils.arch_utils import remove_archwords,has_archwords
import tempfile
import subprocess
import os
from utils.version_hash import versions
from utils.ast_utils import MATCHER_ID,TREE_GENERATOR_ID

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

                                # _, ast2_nodenum = get_ast(other_block.name,use_docker=True,TREE_GENERATOR_ID=TREE_GENERATOR_ID)
                                result = subprocess.run(["docker","run","--rm","-v",other_block.name+":/left.cc","-v",riscv_block.name+":/right.cc","gumtreediff/gumtree","textdiff","/left.cc","/right.cc","-m",MATCHER_ID,"-g",TREE_GENERATOR_ID],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
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