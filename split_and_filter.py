import os
import sys
import re
import shutil

res = r".*(mips|risc|ppc|ia32|s390|x86|arm|x64|loong).*"

def match_pattern(tomatch,pattern):
    if len(tomatch) != len(pattern):
        return False
    for i in range(len(tomatch)):
        if not re.match(res,tomatch[i]):
            if tomatch[i] != pattern[i]:
                return False
    return True


def split_and_filter(dir):
    patches = os.listdir(dir)
    for item in patches:
        hash = item.split('.')[0]
        #split
        patch_file = dir + "/" + item
        path = "./tmp/"+hash
        if not os.path.exists(path):
            os.mkdir(path)
            #os.system("mkdir " + path)
        os.system("splitdiff -D " + path+ " -a " + patch_file)
        #filter
        patches_list = os.listdir(path)
        patterns = []
        for patch in patches_list:
            filename = path + "/" + patch
            p = os.popen("lsdiff " + filename,"r")
            changed_file = p.read()
            p.close()
            if re.match(res,changed_file):
                if len(patterns) == 0:
                    pattern = re.split('[\n.\-/]', changed_file)
                    while "" in pattern:
                        pattern.remove("")
                    newdir = path + "/patch_type" + str(len(patterns))
                    if not os.path.exists(newdir):
                        os.mkdir(newdir)
                        #os.system("mkdir " + newdir)
                    shutil.move(filename,newdir)
                    #os.system("mv " + filename + " " + newdir)
                    patterns.append(pattern)
                    #创建新文件夹并将此条patch移动到文件夹中
                else:
                    matched = False
                    for i in range(len(patterns)):
                        tomatch = re.split('[\n.\-/]', changed_file)
                        while "" in tomatch:
                            tomatch.remove("")
                        matched = match_pattern(tomatch,patterns[i])
                        if matched:
                            newdir = path + "/patch_type" + str(i)
                            if os.path.exists(newdir):
                                shutil.rmtree(newdir)
                            shutil.move(filename,newdir)
                            #os.system("mv " + filename + " " + newdir)
                            #移动到文件夹
                            break
                    if matched == False:
                        #加入新的pattern
                        pattern = re.split('[\n.\-/]', changed_file)
                        while "" in pattern:
                            pattern.remove("")
                        newdir = path + "/patch_type" + str(len(patterns))
                        if not os.path.exists(newdir):
                            os.mkdir(newdir)
                            #os.system("mkdir " + newdir)
                        shutil.move(filename,newdir)
                        #os.system("mv " + filename + " " + newdir)
                        patterns.append(pattern)
            if os.path.exists(filename):
                os.remove(filename)
                #os.system("rm " + filename)
        #如果某个文件夹中只有一个文件，那么说明匹配失败，将它删除
        dirlist = os.listdir(path)
        for item in dirlist:
            if item != ".DS_Store":
                if not os.path.isfile(item):
                    filelist = os.listdir(path + "/" + item)
                    if len(filelist) < 2:
                        shutil.rmtree(path + "/" + item)
                else:
                    print("ERROR:FLIE EXISTS")
                    exit(100)
        dirlist = os.listdir(path)
        dirlist.sort(key=lambda arr: (arr[:10], int(arr[10:])))
        rank = 0
        for item in dirlist:
            if item != ".DS_Store":
                shutil.move(path+"/"+item,path+"/patch_type"+str(rank))
                rank = rank+1
    #shutil.rmtree(dir)
            

if __name__ == "__main__":
    #创建tmp文件夹
    if not os.path.exists("./tmp"):
        os.mkdir("./tmp")
        #os.system("mkdir ./tmp")
    #split_and_filter("./classified_patch")
    split_and_filter(sys.argv[1])