import os 
import shutil

def get_cfile(commit_id,src_file1,dst_file1,src_file2,dst_file2,src_file1_,dst_file1_):
    dir = "./v8"
    os.chdir(dir)
    os.system("git checkout {}^".format(commit_id))
    shutil.move(src_file1,"../"+dst_file1)
    shutil.move(src_file2,"../"+dst_file2)
    os.system("git checkout {}".format(commit_id))
    shutil.move(src_file1_,"../"+dst_file1_)
    os.system("git checkout main")
    os.chdir("..")