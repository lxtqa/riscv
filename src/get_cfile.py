import os
import shutil


def get_cfile(commit_id,src_file1,dst_file1,src_file2,dst_file2,dst_file1_,dst_file2_):
    dir = "./v8"
    os.chdir(dir)
    os.system("git -c advice.detachedHead=false  checkout {}^".format(commit_id))
    print()
    shutil.copy(src_file1,"./"+dst_file1)
    shutil.copy(src_file2,"./"+dst_file2)
    os.system("git -c advice.detachedHead=false  checkout {}".format(commit_id))
    print()
    shutil.copy(src_file1,"./"+dst_file1_)
    shutil.copy(src_file2,"./"+dst_file2_)
    os.system("git -c advice.detachedHead=false  checkout main")
    print()
    os.chdir("..")


def get_cfile(commit_id,src_file1,src_file2):
    dir = "./v8"
    os.system("git -c advice.detachedHead=false  checkout {}^".format(commit_id))
    print()
    with open(dir+'/'+src_file1,"r") as f:
        content1 = f.read()
    with open(dir+'/'+src_file2,"r") as f:
        content2 = f.read()
    return content1,content2
