import os
import re
from utils.arch_utils import *
from utils.ast_utils import *
from utils.patch_utils import *
from block_result import block_result
import json
import tempfile
import signal
from gen_result import construct_mapping_dict

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
            file2_string_std = output22_.stdout
    use_docker = False
    file2_string = block_result(file1,patch1,file2,use_docker=use_docker,MATCHER_ID=MATCHER_ID,TREE_GENERATOR_ID=TREE_GENERATOR_ID,mapping_dict = mapping_dict)

    file2_string_std = remove_whitespace(remove_cpp_comments(file2_string_std))
    file2_string = remove_whitespace(remove_cpp_comments(file2_string))
    for i in range(len(file2_string_std)):
        if file2_string_std[i] != file2_string[i]:
            a = 0
    #除去所有的注释和空字符
    if file2_string_std == file2_string:
        # print("生成成功!")
        return True
    else:
        # print("生成失败")
        return False


#3,6,4 Sh sh
#4,1,7
#缺分号
sb1 = 4
sb2 = 26
sb3 = 1
F = True

def main():

    with open("versions_diff_block.json") as jsonFile:
        versions_diff_block = json.load(jsonFile)
        for v,version in enumerate(versions_diff_block):


            if F:
                pass
            if v != sb1:
                continue

            with open('mapping/mapping_' + version["versions"][0] + '.json', 'r') as json_file:
                jsonObject = json.load(json_file)
                mapping_dict = {}
                for [file_name,content] in jsonObject:
                    dic = [{} for _ in range(10)]
                    for block_dics in content:
                        for i,block_dic in enumerate(block_dics):
                            dic[i].update(block_dic)
                    mapping_dict[file_name] = dic
            for file_name in mapping_dict.keys():
                for i,item in enumerate(mapping_dict[file_name]):
                    mapping_dict[file_name][i] = construct_mapping_dict(item)

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

                # if t < 3:
                #     continue
                if F:
                    m = m + 1
                    if m != sb2:
                        continue


                for j,file in enumerate(type):
                    
                    if F:
                        pass
                        if arch_dic[has_archwords(file["file"])] != sb3:
                            continue

                    if j != i:
                        with open(file["file"],"r") as f:
                            content1 = format(f.read(),"..")
                            patch1 = {"header":file["header"],"patch":file["patch"]}
                            file_name = "./" + remove_archwords(file['file'])
                            arch = has_archwords(file["file"])
                            try:
                                succeed = successfully_generate(content1,patch1,content2,patch2,mapping_dict[file_name][arch_dic[arch]])
                            except:
                                succeed = False
                            if succeed:
                                result[arch_dic[arch]] =  1
                            else:
                                result[arch_dic[arch]] =  -1
                vresult.append(result)
            print("")
            os.system("git -c advice.detachedHead=false checkout main > /dev/null 2>&1")
            print()
            os.chdir("..")
            with open("result/result"+str(v)+"__2.json","w") as f:
                json.dump(vresult,f,indent=4)

if __name__ == "__main__":
    main()
