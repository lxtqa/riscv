import os
import re
from utils.arch_utils import *
from utils.ast_utils import *
from utils.patch_utils import *
from utils.version_hash import versions
from block_result import block_result
import json
import tempfile
import signal
from gen_result import construct_mapping_dict

# 定义超时处理函数
def timeout_handler(signum, frame):
    raise TimeoutError("程序超时")



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


def successfully_generate(file1,patch1,file2,patch2,mapping_dict):

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
    use_docker = False
    file2_String = block_result(file1,patch1,file2,use_docker=use_docker,MATCHER_ID=MATCHER_ID,TREE_GENERATOR_ID=TREE_GENERATOR_ID,mapping_dict = mapping_dict)

    file2_String_std = remove_whitespace(remove_cpp_comments(file2_String_std))
    file2_String = remove_whitespace(remove_cpp_comments(file2_String))
    # for i in range(len(file2_String_std)):
    #     if file2_String[i] != file2_String_std[i]:
    #         a = 0  
    #除去所有的注释和空字符
    if file2_String_std == file2_String:
        # print("生成成功!")
        return True
    else:
        # print("生成失败")
        return False




F = True

def main(sb1,sb2,sb3):

    with open("versions_diff_block.json") as jsonFile:
        versions_diff_block = json.load(jsonFile)
        for v,version in enumerate(versions_diff_block):


            if F:
                pass
                if v < sb1:
                    continue

            # with open('mapping/mapping_' + version["versions"][0] + '.json', 'r') as json_file:
            #     jsonObject = json.load(json_file)
            #     mapping_dict = {}
            #     for [file_name,content] in jsonObject:
            #         dic = [{} for _ in range(10)]
            #         for block_dics in content:
            #             for i,block_dic in enumerate(block_dics):
            #                 dic[i].update(block_dic)
            #         mapping_dict[file_name] = dic
            # for file_name in mapping_dict.keys():
            #     for i,item in enumerate(mapping_dict[file_name]):
            #         mapping_dict[file_name][i] = construct_mapping_dict(item)

            vresult = []
            dir = "v8"
            os.chdir(dir)
            os.system("git -c advice.detachedHead=false  checkout "+version["versions"][0])
            print()
            m = -1
            for t,type in enumerate(version["contents"]):
                print(str(t)+"/"+str(len(version["contents"])),end=" ",flush=True)
                result = [0 for _ in range(10)]
                flag = False
                for i,file2 in enumerate(type):
                    arch = has_archwords(file2["file"])
                    if arch == "riscv" or arch == "riscv64":
                        flag = True
                        with open(file2["file"],"r") as f:
                            content2 = format(f.read(),"..")
                            patch2 = {"header":file2["header"],"patch":file2["patch"]}
                            patch2["patch"] = ["diff --git a/a.cc b/b.cc","--- a/a.cc","+++ b/b.cc"] + patch2["patch"]
                        break
                if not flag:
                    continue

                # if t < sb2:
                #     continue
                if F:
                    m = m + 1
                    if m < sb2:
                        continue


                for j,file1 in enumerate(type):
                    
                    if F:
                        pass
                        if arch_dic[has_archwords(file1["file"])] != sb3:
                            continue

                    if j != i:
                        with open(file1["file"],"r") as f:
                            content1 = format(f.read(),"..")
                            patch1 = {"header":file1["header"],"patch":file1["patch"]}
                            file_name = "./" + remove_archwords(file1['file'])
                            arch = has_archwords(file1["file"])
                                # 设置超时信号


                            c = {
                                    "version":version["versions"],
                                    "file1":file1["file"],
                                    "patch1":patch1["patch"],
                                    "file2":file2["file"],
                                    "patch2":patch2["patch"],
                                }
                            os.chdir("..")
                            with open("fault/"+str(sb1)+"_"+str(sb2)+"_"+str(sb3)+".json","w") as f:
                                json.dump(c,f,indent=4)
                            return
                                # succeed = successfully_generate(content1,patch1,content2,patch2,mapping_dict[file_name][arch_dic[arch]])
                        
            

if __name__ == "__main__":
    with open("fault.txt") as f:
        faults = f.readlines()
        for fault in faults:
            fault = fault[:-1]
            fault = fault.split(" ")
            fault[0],fault[1],fault[2] = int(fault[0]),int(fault[1]),int(fault[2])
            main(fault[0],fault[1],fault[2])
