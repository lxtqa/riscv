import os 
import shutil

def get_cfile(commit_id,src_file,dst_file):
    dir = "./v8"
    os.chdir(dir)
    os.system("git checkout {}".format(commit_id))
    shutil.move(src_file,"../"+dst_file)
    os.system("git checkout main")
    os.chdir("..")