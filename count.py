import re
import codecs
from tqdm import *
import subprocess
from arc_utils import has_arcwords


res1 = r"^\s[/a-zA-Z0-9_.\-]+\.(.+)\s+\|\s+[0-9]+\s+[+-]+$"
res2 = r"[/a-zA-Z0-9_\-]+\.[a-zA-Z0-9]+"

def riscv():
    log_file = codecs.open("../log.txt","r",errors="ignore")
    log_lines = log_file.readlines()
    #res = r"[^ ]+(/[^ ]+)* +\| +\d+ [\+\-]+"
    #riscv,RISCV or rv32,rv64
    total_commit_num = 0
    hashs = []
    for log_line in tqdm(log_lines) :
        line_info = log_line.split(" ")
        changed_files = []
        if line_info[0] == "commit" :
            total_commit_num += 1
            hash = line_info[1]
            hash = hash.split("\n")[0]
            text = subprocess.run(["git","format-patch","-1",hash,"--stdout"],capture_output=True,text = True)
            lines = text.stdout.split("\n")
            for line in lines:
                if re.match(res1,line) != None:
                    file_name = re.findall(res2,line)[0]
                    if has_arcwords(file_name):
                        changed_files.append(file_name)
        if changed_files != []:
            hashs.append([hash,changed_files])
    for item in hashs:
        print(item)



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