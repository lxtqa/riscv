import os
import re
from utils.arch_utils import *
from utils.patch_utils import *
from hunk_result import hunk_result
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
        file2_String = hunk_result(file1,patch1,file2,use_docker=use_docker,MATCHER_ID="gumtree-simple",TREE_GENERATOR_ID="cpp-srcml")

        #除去所有的注释和空字符
        if remove_whitespace(remove_cpp_comments(file2_String_std)) == remove_whitespace(remove_cpp_comments(file2_String)):
            # print("生成成功!")
            return True
        else:
            # print("生成失败")
            return False
    except:
        return False

def main():
    #TODO:如果能对一些变量名等进行映射，准确率会上涨？
    with open("versions_diff_hunk.json") as jsonFile:
        versions_diff_hunk = json.load(jsonFile)
        for v,version in enumerate(versions_diff_hunk):
            if v<12:
                continue
            vResult = []
            dir = "v8"
            os.chdir(dir)
            os.system("git -c advice.detachedHead=false  checkout {} > /dev/null 2>&1".format(version["versions"][0]))
            print()
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
                for j,file in enumerate(type):
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
            with open("result/result"+str(v)+".json","w") as f:
                json.dump(vResult,f,indent=4)

if __name__ == "__main__":
    main()
