# 导入os模块
import os
import codecs
import re
from tqdm import *
 
# path定义要获取的文件名称的目录
path = "../my_shell/patches-origin"
 
#res_1 = r"[\+\-].*[Rr](([Ii][Ss][Cc])|[Vv](32|64)).*"
res_1 = r"[\+\-].*(RISC|Risc|risc|RV64|RV32|rv64|rv32|Rv64|Rv32).*"

res_2 = r"diff --git [^ ]+(/[^ ]+)* [^ ]+(/[^ ]+)*"

res_3 = r".*//.*"
patches = os.listdir(path)
os.mkdir("../my_shell/parsered_patches_origin")
 
for patch in patches :
    patch_file = codecs.open(path+"/"+patch,"r",errors="ignore")
    patch_lines = patch_file.readlines()
    patch_file.close()
    found = False
    start = False
    i = 0
    while i < len(patch_lines) :
        if re.match(res_2,patch_lines[i]) :
            i+=4
            start = True
            continue
        if start :
            if re.match(res_1,patch_lines[i]):
                if not re.match(res_3,patch_lines[i]):
                    found = True
        i=i+1
    
    if found == True :
        os.system("cp "+path+"/"+patch+" ../my_shell/parsered_patches_origin")

                
    

