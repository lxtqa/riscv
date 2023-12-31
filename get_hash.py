import os
import re
import codecs
from tqdm import *
def riscv():
    log_file = codecs.open("../GitLog-origin.txt","r",errors="ignore")
    log_lines = log_file.readlines()
    hash_file = open("../GitHash-origin.txt","w")
    #res = r"[^ ]+(/[^ ]+)* +\| +\d+ [\+\-]+"
    #riscv,RISCV or rv32,rv64
    res = r".*(RISC|Risc|risc|RV64|RV32|rv64|rv32|Rv64|Rv32).*"
    total_commit_num = 0
    for log_line in tqdm(log_lines) :
        line_info = log_line.split(" ")
        if line_info[0] == "commit" :
            total_commit_num += 1
            hash = line_info[1]
            hash = hash.split("\n")[0]
            os.system("git show " + hash +" > ../InfoFile-origin.txt")
            info_file = codecs.open("../InfoFile-origin.txt","r",encoding='utf-8',errors="ignore")
            info_lines = info_file.readlines()
            ## file name and path
            for info_line in info_lines:
                if re.match(res,info_line):
                #if "risc" in info_line or "Risc" in info_line or "RISC" in info_line:
                    hash_file.write(hash+'\n')
                    break
            ## 
            info_file.close()
            os.system("rm ../InfoFile-origin.txt")


def date():
    log_file = codecs.open("../GitLog-origin.txt","r",errors="ignore")
    log_lines = log_file.readlines()
    hash_file = open("../GitHash-origin.txt","w")
    total_commit_num = 0
    qualified_commit_num = 0
    for i in tqdm(range(len(log_lines))) :
        log_line = log_lines[i]
        line_info = log_line.split(" ")
        if line_info[0] == "commit" :
            total_commit_num += 1
            time = log_lines[i+2].split(" ")
            while "" in time:
                time.remove("")
            if int(time[5]) >= 2023:
                qualified_commit_num += 1
                hash = line_info[1]
                hash = hash.split("\n")[0]
                hash_file.write(hash+'\n')

    print("total commit number = {}".format(total_commit_num))
    print("qualified commit number = {}".format(qualified_commit_num))
    hash_file.close()

if __name__ == "__main__":
    riscv()
    # date()