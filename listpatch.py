import os
import sys

def split_and_filter(input_file, dir):
    f = open(input_file)
    patches = f.readlines()
    result_file = "result.txt"
    re = open(result_file,'w')
    re.close()
    for hash in patches:
        #split
        hash = hash.split("\n")[0]
        patch_file = dir + "/" + hash + ".patch"
        os.system("echo \""+hash+"\" >> " + result_file)
        os.system("lsdiff " + patch_file + " >> "+ result_file)
            
    pass

if __name__ == "__main__":
    #创建tmp文件夹
    split_and_filter(sys.argv[1],sys.argv[2])