#自动对含有riscv关键字的文件进行分类，分离出多个架构下进行了相似改动的文件，这个检测主要依赖于文件名相似性的检测
import re
import os
import shutil
import codecs


res1 = r"^\s[/a-zA-Z0-9_.\-]+\.(.+)\s+\|\s+[0-9]+\s+[+-]+\n$"

res2 = r"[/a-zA-Z0-9_\-]+\.[a-zA-Z0-9]+"

res3 = r".*(mips|risc|ppc|ia32|s390|x86|arm|x64|loong).*"

res4 = r".*(harm).*"

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
    savepath = "../related_patch"
    file = open("related_patch.txt","w")
    if not os.path.exists(savepath):
        os.mkdir(savepath)
    patchname_list.sort()
    dic = {}
    matched_dic = {}
    for patchname in patchname_list:
        filename_list = []
        patchfile = codecs.open(patch_path + patchname,"r",errors="ignore")
        try:
            patch = patchfile.readlines()
            for line in patch:
                matched = re.match(res1,line)
                if matched != None:
                    filename = re.findall(res2,line)[0]
                    if re.match(res3,filename) and not re.match(res4,filename) :
                        filename_list.append(filename)
            if len(filename_list) != 0:
                for i in range(len(filename_list)):
                    if filename_list[i] in dic:
                        dic[filename_list[i]] += 1
                    else:
                        dic[filename_list[i]] = 1
                    for j in range(0,len(filename_list)):
                        if i==j:
                            continue
                        if matchdir(filename_list[i],filename_list[j]):
                            if filename_list[i] in matched_dic:
                                matched_dic[filename_list[i]] += 1
                            else:
                                matched_dic[filename_list[i]] = 1
                os.system("cp "+patch_path + patchname+" "+savepath)
        except:
            pass
    lst = []
    match_num = 0
    for key in dic:
        if key in matched_dic:
            match_num += 1
            lst.append([dic[key],matched_dic[key],key])
        else:
            lst.append([dic[key],0,key])
    lst.sort(reverse=True)
    total = 0
    ma = 0
    for item in lst:
        file.write("{} changed times = {}, matched times = {}\n".format(item[2],item[0],item[1]))
        total += item[0]
        ma += item[1]
    file.write("total changed times = {}, matched times = {},{}\n".format(total,ma))
            

    file.close()


if __name__=="__main__":
    main("../patches-origin/")