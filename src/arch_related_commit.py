import os
import re
import codecs
from tqdm import *
import subprocess
import json
from utils.arch_utils import has_archwords

def riscv():
    log_file = codecs.open("./GitLog-origin.txt","r",errors="ignore")
    log_lines = log_file.readlines()
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
            file_names = []
            for info_line in info_lines:
                file_name = re.findall(r"^diff --git a/(.+) b/(.+)$",info_line)
                if file_name!=[]:
                    file_name = file_name[0]
                    if file_name[0] == file_name[1]:
                        if has_archwords(file_name[0]):
                            file_names.append(file_name[0])
            if file_names != []:
                dic = {"hash":hash,"file_names":file_names}
                content.append(dic)
    json.dump(content,f,indent=4)
    f.close()

if __name__ == "__main__":
    riscv()