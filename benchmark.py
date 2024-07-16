import os
import re
from get_cfile import get_cfile
from unit_result import unit_result

class Commit:
    def __init__(self,hash):
        self.hash = hash
        self.content = []


def modify_hex(file_path,reverse = False):
    
    if not reverse:
        with open(file_path, 'r') as file:
            cpp_code = file.read()
            pattern = r'0x[0-9a-fA-F]+(\'[0-9a-fA-F]+)*'
            replacer = lambda match: match.group().replace("'", '')
            processed_code = re.sub(pattern, replacer, cpp_code)
        with open(file_path, 'w') as file:
            file.write(processed_code)
    else:
        #TODO:reverse back
        pass


def successfully_generate(hash,file1,file2,num):
    if not os.path.exists("./benchmark/"+str(num)):
        os.mkdir("./benchmark/"+str(num))
    dst_file1 = "./benchmark/"+str(num)+"/test1.cc"
    dst_file2 = "./benchmark/"+str(num)+"/test2.cc"
    dst_file1_ = "./benchmark/"+str(num)+"/test1_.cc"
    dst_file2_ = "./benchmark/"+str(num)+"/test2__.cc" # 与下面gen_result的结果不同，输出原始结果
    # get_cfile(hash,src_file1=file1,dst_file1=dst_file1,
    #           src_file2=file2,dst_file2=dst_file2,
    #           dst_file1_=dst_file1_,
    #           dst_file2_=dst_file2_)
    os.system("diff -up {} {} > ./benchmark/{}/1_patch.patch".format(dst_file1,dst_file1_,num))
    os.system("diff -up {} {} > ./benchmark/{}/2_patch.patch".format(dst_file2,dst_file2_,num))
    modify_hex(dst_file1)
    modify_hex(dst_file1_)
    modify_hex(dst_file2)
    modify_hex(dst_file2_)
    
    rm_tempfile = False
    use_docker = False
    debugging = False
    try:
        unit_result(
                dir="./benchmark/"+str(num),
                cfile_name1="test1.cc",
                cfile_name2="test2.cc",
                cfile_name1_="test1_.cc",
                cfile_name2_="test2_.cc",
                rm_tempfile=rm_tempfile,
                use_docker=use_docker,
                debugging=debugging,
                MATCHER_ID="gumtree-simple-id",#"gumtree-hybrid",
                TREE_GENERATOR_ID="cpp-srcml"#"cs-srcml"
                )
        print("成功生成!")
        os.system("diff -up {} {} > {}/new_patch.patch".format("./benchmark/"+str(num) + "/" + "test2.cc","./benchmark/"+str(num) + "/" + "test2_.cc","./benchmark/"+str(num)))
    except:
        print("生成失败")
        
    
def main():
    num = 0
    tmp_path = "./tmp"
    hashs = os.listdir(tmp_path)
    commits = []
    for hash in hashs:
        commit = Commit(hash)
        if hash == ".DS_Store":
            continue
        types = os.listdir(tmp_path+"/"+hash)
        for type in types:
            if type == ".DS_Store":
                continue
            files = os.listdir(tmp_path+"/"+hash+"/"+type)
            lst = []
            for file_name in files:
                file = open(tmp_path+"/"+hash+"/"+type+"/"+file_name)
                line = file.readline()
                try:
                    name = line.split(" ")[2][2:]
                    name_ = line.split(" ")[3][2:-1]
                except:
                    continue
                lst.append([name,name_])
            commit.content.append(lst)
        commits.append(commit)

    if not os.path.exists("./benchmark"):
            os.mkdir("./benchmark")

    for commit in commits:
        
        for type in commit.content:
            arm64_file = None
            riscv64_file = None
            # 判断是否具有arm和riscv两个架构，如果没有则返回
            for file_name in type:
                if "arm64" in file_name[0]:
                    arm64_file = file_name
                elif "riscv64" in file_name[0]:
                    riscv64_file = file_name
                
                if arm64_file != None and riscv64_file != None:
                    num = num + 1
                    if num > 54:
                        print("---------------{}--------------".format(num))
                        successfully_generate(commit.hash,arm64_file,riscv64_file,num)
                        print("---------------{}--------------".format(num))
                    if num == 55:
                        return
                    break
                    
        
if __name__ == "__main__":
    main()
