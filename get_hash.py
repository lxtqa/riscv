import os
import re
import codecs
from tqdm import *
def main():
    log_file = codecs.open("../my_shell/GitLog-origin.txt","r",errors="ignore")
    log_lines = log_file.readlines()
    hash_file = open("../my_shell/GitHash-origin.txt","w")
    #res = r"[^ ]+(/[^ ]+)* +\| +\d+ [\+\-]+"
    #riscv,RISCV or rv32,rv64
    res = r".*(RISC|Risc|risc|RV64|RV32|rv64|rv32|Rv64|Rv32).*"
    for log_line in tqdm(log_lines) :
        line_info = log_line.split(" ")
        if line_info[0] == "commit" :
            hash = line_info[1]
            hash = hash.split("\n")[0]
            os.system("git show " + hash +" > ../my_shell/InfoFile-origin.txt")
            #os.system("git show --stat " + hash +" > ../my_shell/StatFile.txt")
            info_file = codecs.open("../my_shell/InfoFile-origin.txt","r",encoding='utf-8',errors="ignore")
            #stat_file = codecs.open("../my_shell/StatFile.txt","r",encoding='utf-8',errors="ignore")
            info_lines = info_file.readlines()
#            stat_lines = stat_file.readlines()
            ## file name and path
            for info_line in info_lines:
                if re.match(res,info_line):
                #if "risc" in info_line or "Risc" in info_line or "RISC" in info_line:
                    hash_file.write(hash+'\n')
                    break
                            # for stat_line in stat_lines:
                            #     if re.search(res,stat_line) != None:
            ## 
            info_file.close()
            #stat_file.close()

if __name__ == "__main__":
    main()