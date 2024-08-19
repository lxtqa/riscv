#自动对含有riscv关键字的文件进行分类，分离出多个架构下进行了相似改动的文件，这个检测主要依赖于文件名相似性的检测
import re
import os
import codecs
from utils.arc_utils import has_arcwords,remove_arcwords

def main(patch_path):
    patchname_list = os.listdir(patch_path)
    savepath = "./related_patch"
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
                filename = re.findall(r"^diff --git a/(.+) b/(.+)$",line)
                if filename != []:
                    if has_arcwords(filename[0][0]):
                        filename_list.append(filename[0][0])
            if len(filename_list) != 0:
                for i in range(len(filename_list)):
                    if filename_list[i] in dic:
                        dic[filename_list[i]] += 1
                    else:
                        dic[filename_list[i]] = 1
                    for j in range(0,len(filename_list)):
                        if i==j:
                            continue
                        if remove_arcwords(filename_list[i]) == remove_arcwords(filename_list[j]):
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
    main("./patches-origin/")