import json
from utils.ast_utils import *
from tqdm import tqdm
from utils.ast_utils import MATCHER_ID,TREE_GENERATOR_ID
import tempfile
import subprocess

def bfs_get_num(root):
    queue = [root]
    num = 0
    while queue:
        node = queue.pop(0)
        queue.extend(node.children)
        num = num + 1
    return num


def modify_hex(cpp_code,reverse = False):
    if not reverse:
        pattern = r'0x[0-9a-fA-F]+(\'[0-9a-fA-F]+)*'
        replacer = lambda match: match.group().replace("'", '')
        processed_code = re.sub(pattern, replacer, cpp_code)
        return processed_code

def main(hash):
    with open('match/match_'+hash+'.json', 'r') as json_file:
        block_sets = json.load(json_file)
        similarity = []
        #riscv64
        j = 0
        for [file_type,files,content] in tqdm(block_sets):
            # no riscv64 in matches
            if files[3] == "":
                continue
            similar = []
            ast_nodenum = [0 for _ in range(10)]
            for i,file_content in enumerate(files):
                if file_content != "":
                    with tempfile.NamedTemporaryFile(delete=True, mode='w', suffix='.cpp') as file:
                        file.write(modify_hex(file_content))
                        file.flush()
                        _, ast_nodenum[i] = get_ast(file.name,use_docker=False,TREE_GENERATOR_ID=TREE_GENERATOR_ID)


            for block_set in content:
                if block_set[3] == []:
                    continue
                with tempfile.NamedTemporaryFile(delete=True, mode='w', suffix='.cpp') as riscv_block:
                    riscv_block.write("\n".join(block_set[3]))
                    riscv_block.flush()
                    _, ast1_nodenum = get_ast(riscv_block.name,use_docker=False,TREE_GENERATOR_ID=TREE_GENERATOR_ID)
                    simi = []
                    for i,block in enumerate(block_set):
                        if i != 2 and i != 3:
                            with tempfile.NamedTemporaryFile(delete=True, mode='w', suffix='.cpp') as other_block:
                                if block != []:
                                    other_block.write("\n".join(block))
                                    other_block.flush()
                                    _, ast2_nodenum = get_ast(other_block.name,use_docker=False,TREE_GENERATOR_ID=TREE_GENERATOR_ID)
                                    result = subprocess.run(["gumtree","textdiff",riscv_block.name, other_block.name,
                                        "-m",MATCHER_ID,"-g", TREE_GENERATOR_ID],
                                        capture_output=True,text = True)
                                    matches, _= gumtree_parser(result.stdout)
                                    # unit总能匹配到
                                    if ast1_nodenum - 1 + ast2_nodenum - 1 - (len(matches) - 1) == 0:
                                        r = 0
                                    else:
                                        r = (len(matches) - 1) / ( ast1_nodenum - 1 + ast2_nodenum - 1 - (len(matches) - 1) )
                                else:
                                    r = 0
                                simi.append(r)
                        else:
                            simi.append(1.0)
                similar.append([ast1_nodenum,simi])
            similarity.append([file_type,ast_nodenum,similar])
            j = j+1
        with open("similarity.json","w") as simFile:
            json.dump(similarity,simFile,indent=4)



if __name__ == "__main__":
    hash = "519ee9d66cd"
    main(hash)



