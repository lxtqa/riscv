#自动对含有riscv关键字的文件进行分类，分离出多个架构下进行了相似改动的文件，这个检测主要依赖于文件名相似性的检测
import re
import os
import codecs
from arc_utils import remove_arcwords,has_arcwords

def main(patch_path):
    patchname_list = os.listdir(patch_path)
    savepath = "./classified_patch"
    if not os.path.exists(savepath):
        os.mkdir(savepath)
    patchname_list.sort()
    for patchname in patchname_list:
        filename_list = []
        patchfile = codecs.open(patch_path + "/" + patchname,"r",errors="ignore")
        try:
            patch = patchfile.readlines()
            for line in patch:
                filename = re.findall(r"^diff --git a/(.+) b/(.+)$",line)
                if has_arcwords(filename[0]):
                    filename_list.append(filename[0])
            if len(filename_list) != 0:
                flag = False
                for i in range(len(filename_list)):
                    if flag:
                        break
                    for j in range(i+1,len(filename_list)):
                        if flag:
                            break
                        if remove_arcwords(filename_list[i]) == remove_arcwords(filename_list[j]):
                            flag = True
                if flag:
                    os.system("cp "+patch_path + patchname+" "+savepath)
        except:
            pass


if __name__=="__main__":
    main("./patches-origin")