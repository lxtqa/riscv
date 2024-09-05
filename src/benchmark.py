import os
import re
from utils.arch_utils import *
from utils.ast_utils import *
from utils.patch_utils import *
from block_result import block_result
import json
from tqdm import tqdm
import tempfile

arch_dic = {"arm":0,"arm64":1,"riscv32":2,"riscv64":3,"mips":4,"ia32":5,"x64":6,"loong":7,"s390":8,"ppc":9}

class Commit:
    def __init__(self,hash):
        self.hash = hash
        self.content = []


def modify_hex(cpp_code,reverse = False):
    if not reverse:
        pattern = r'0x[0-9a-fA-F]+(\'[0-9a-fA-F]+)*'
        replacer = lambda match: match.group().replace("'", '')
        processed_code = re.sub(pattern, replacer, cpp_code)
        return processed_code
    else:
        #TODO:reverse back
        pass

def remove_cpp_comments(file_content):
    # 正则表达式匹配 C++ 的注释
    pattern = r'//.*?$|/\*.*?\*/'

    # 使用 re.sub 替换掉匹配的注释内容，re.DOTALL 让 . 能匹配换行符，re.MULTILINE 处理多行注释
    cleaned_content = re.sub(pattern, '', file_content, flags=re.DOTALL | re.MULTILINE)

    return cleaned_content


def successfully_generate(file1,patch1,file2,patch2):

    modify_hex(file1)
    modify_hex(file2)

    with tempfile.NamedTemporaryFile(delete=True, mode='w', suffix='.cc') as cfile2, \
        tempfile.NamedTemporaryFile(delete=True, mode='w', suffix='.patch') as patchfile2:
            cfile2.write(file2)
            cfile2.flush()
            patchfile2.write("\n".join(patch2["patch"])+"\n")
            patchfile2.flush()
            output22_ = subprocess.run(["patch",cfile2.name,patchfile2.name,"--output=-"],capture_output=True,text = True)
            file2_String_std = output22_.stdout
    use_docker = True
    try:
        file2_String = block_result(file1,patch1,file2,use_docker=use_docker,MATCHER_ID="gumtree-hybrid",TREE_GENERATOR_ID="cpp-srcml")

        #除去所有的注释和空字符
        if remove_whitespace(remove_cpp_comments(file2_String_std)) == remove_whitespace(remove_cpp_comments(file2_String)):
            # print("生成成功!")
            return True
        else:
            # print("生成失败")
            return False
    except:
        return False


def construct_mapping_dict(mapping):
    mapping_dict = {}
    for key in mapping.keys():
        value = mapping[key]
        if key.split(" ")[0] == "name:" and value.split(" ")[0] == "name:":
            a,b = get_name(key),get_name(value)
            if a not in mapping_dict.keys():
                mapping_dict[a] = {b:1}
            else:
                if b not in mapping_dict[a].keys():
                    mapping_dict[a][b] = 1
                else:
                    mapping_dict[a][b] = mapping_dict[a][b] + 1
    return mapping_dict


sb1 = 1
sb2 = 17
sb3 = 0

def main():
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
    mapping = {}
    for version in versions:
        with open('match/match_' + version + '.json', 'r') as json_file:
            mapping[version] = json.load(json_file)

    with open("versions_diff_block.json") as jsonFile:
        versions_diff_block = json.load(jsonFile)
        for v,version in enumerate(versions_diff_block):

            # if v < sb1:
            #     continue

            vResult = []
            dir = "v8"
            os.chdir(dir)
            os.system("git -c advice.detachedHead=false  checkout "+version["versions"][0]+" > /dev/null 2>&1")
            print()
            m = -1
            mapping_dict = construct_mapping_dict(match_dic12)
            for t,type in enumerate(version["contents"]):
                print(str(t)+"/"+str(len(version["contents"])),end=" ",flush=True)
                Result = [0 for _ in range(10)]
                flag = False
                for i,file in enumerate(type):
                    arch = has_archwords(file["file"])
                    if arch == "riscv" or arch == "riscv64":
                        flag = True
                        with open(file["file"],"r") as f:
                            content2 = format(f.read(),"..")
                            patch2 = {"header":file["header"],"patch":file["patch"]}
                            patch2["patch"] = ["diff --git a/a.cc b/b.cc","--- a/a.cc","+++ b/b.cc"] + patch2["patch"]
                        break
                if not flag:
                    continue

                # m = m + 1
                # if m < 17:
                #     continue


                for j,file in enumerate(type):

                    # if arch_dic[has_archwords(file["file"])] != sb3:
                    #     continue

                    if j != i:
                        with open(file["file"],"r") as f:
                            content1 = format(f.read(),"..")
                            patch1 = {"header":file["header"],"patch":file["patch"]}
                            succeed = successfully_generate(content1,patch1,content2,patch2)
                            arch = has_archwords(file["file"])
                            if succeed:
                                Result[arch_dic[arch]] =  1
                            else:
                                Result[arch_dic[arch]] =  -1
                vResult.append(Result)
            print("")
            os.system("git -c advice.detachedHead=false checkout main > /dev/null 2>&1")
            print()
            os.chdir("..")
            # with open("result/result"+str(v)+"_.json","w") as f:
            #     json.dump(vResult,f,indent=4)

if __name__ == "__main__":
    main()
