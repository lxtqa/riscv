import os
import re
import codecs
from tqdm import *
import subprocess
import json
def has_arcwords(text):
    for keyword in ["arm64","Arm64","ARM64","arm32","Arm32","ARM32","arm","Arm","ARM", \
                    "x64","X64", \
                    "riscv64","Riscv64","RISCV64","riscv32","Riscv32","RISCV32","riscv","Riscv","RISCV",\
                    "s390","S390",\
                    "ia32","Ia32","IA32",\
                    "ppc64","Ppc64","PPC64","ppc32","Ppc32","PPC32","ppc","Ppc","PPC",\
                    "mips64","Mips64","MIPS64","mips32","Mips32","MIPS32","mips","Mips","MIPS",\
                    "loong64","Loong64","LOONG64","loong32","Loong32","LOONG32","loong","Loong","LOONG"]:
        if keyword in text:
            if keyword == "arm" and "harmony" in text:
                pass
            else:
                return True
    return False

def riscv():
    log_file = codecs.open("./GitLog-origin.txt","r",errors="ignore")
    log_lines = log_file.readlines()
    #res = r"[^ ]+(/[^ ]+)* +\| +\d+ [\+\-]+"
    #riscv,RISCV or rv32,rv64
    res = r"^diff --git a/(.+) b/(.+)$"
    total_commit_num = 0
    f = open("arch_related_commit_id.json","w")
    content = []
    for log_line in tqdm(log_lines) :
        line_info = log_line.split(" ")
        if line_info[0] == "commit" :
            total_commit_num += 1
            hash = line_info[1]
            hash = hash.split("\n")[0] 
            result = subprocess.run(["git","show",hash],cwd="./v8", stdout=subprocess.PIPE)
            output = result.stdout.decode('utf-8', errors='ignore')
            info_lines = output.split("\n")
            ## file name and path
            
            file_names = []
            for info_line in info_lines:
                file_name = re.findall(res,info_line)
                if file_name!=[]:
                    file_name = file_name[0]
                    if file_name[0] == file_name[1]:
                        if has_arcwords(file_name[0]):
                            file_names.append(file_name[0])
            if file_names != []:   
                dic = {"hash":hash,"file_names":file_names}
                content.append(dic)
    f.write(json.dumps(content))
    f.close()

if __name__ == "__main__":
    riscv()
    # date()