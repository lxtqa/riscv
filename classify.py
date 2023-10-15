#自动对含有riscv关键字的文件进行分类，分离出多个架构下进行了相似改动的文件，这个检测主要依赖于文件名相似性的检测
import re
import sys
import os
import shutil


res1 = r"^\s[/a-zA-Z0-9_\-]+\.(.+)\s+\|\s+[0-9]+\s+[+-]+\n$"

res2 = r"[/a-zA-Z0-9_\-]+\.[a-zA-Z0-9]+"

res3 = r".*(mips|risc|ppc|ia32|s390|x86|arm|x64|loong).*"

def matchdir(dir1,dir2):
    dir1 = re.split('[\n\-./_]',dir1)
    while "" in dir1:
        dir1.remove("")
    dir2 = re.split('[\n\-./_]',dir2)
    while "" in dir2:
        dir2.remove("")
    if len(dir1) != len(dir2):
        return False
    for i in range(len(dir1)):
        matched1 = re.match(res3,dir1[i])
        matched2 = re.match(res3,dir2[i])
        if (matched1 != None and  matched2 == None) or (matched1 == None and  matched2 != None):
            continue
        else:
            if matched1:
                continue
            else:
                if dir1[i] != dir2[i]:
                    return False
    return True

def main(patch_path):
    patchname_list = os.listdir(patch_path)
    savepath = "./classified_patch"
    if not os.path.exists(savepath):
        os.mkdir(savepath)
    for patchname in patchname_list:
        filename_list = []
        patchfile = open(patch_path + patchname)
        patch = patchfile.readlines()
        for line in patch:
            matched = re.match(res1,line)
            if matched != None:
                filename = re.findall(res2,line)[0]
                if re.match(res3,filename):
                    filename_list.append(filename)
        if len(filename_list) != 0:
            flag = False
            for i in range(len(filename_list)):
                if flag:
                    break
                for j in range(i+1,len(filename_list)):
                    if flag:
                        break
                    if matchdir(filename_list[i],filename_list[j]):
                        flag = True
            if flag:
                os.system("cp "+patch_path + patchname+" "+savepath)


if __name__=="__main__":
    main("./patches-origin/")
    shutil.rmtree("./patches-origin/")