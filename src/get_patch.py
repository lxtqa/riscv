import subprocess
import re
import codecs
from tqdm import *
import subprocess
import os

HASH_PATH = "./GitHash-origin.txt"


def riscv():
    result = subprocess.run(["git","log"],cwd="./v8",stdout=subprocess.PIPE)
    log_lines = result.stdout.decode('utf-8', errors='ignore').split("\n")
    hash_file = open(HASH_PATH,"w")
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
            result = subprocess.run(["git","show",hash],cwd="./v8",stdout=subprocess.PIPE)
            info_lines = result.stdout.decode('utf-8', errors='ignore').split("\n")
            ## file name and path
            for info_line in info_lines:
                if re.match(res,info_line):
                #if "risc" in info_line or "Risc" in info_line or "RISC" in info_line:
                    hash_file.write(hash+'\n')
                    break


def date():
    result = subprocess.run(["git","log"],cwd="./v8",stdout=subprocess.PIPE)
    log_lines = result.stdout.decode('utf-8', errors='ignore').split("\n")
    hash_file = open(HASH_PATH,"w")
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


#git format-patch -1 [commit id]
def gen_patches():
    hash_file = codecs.open(HASH_PATH,"r",errors="ignore")
    hash_lines = hash_file.readlines()
    os.system("mkdir ./patches-origin")
    for hash_line in tqdm(hash_lines):
        hash = hash_line.split("\n")[0]
        os.system("git format-patch -1 " + hash + " --stdout > ./patches-origin/" + hash + ".patch")


if __name__ == "__main__":
    if not os.path.exists(HASH_PATH):
        riscv()
    gen_patches()
    # date()