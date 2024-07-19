import os 
import shutil

def get_cfile(commit_id,src_file1,dst_file1,src_file2,dst_file2,dst_file1_,dst_file2_):
    dir = "./v8"
    os.chdir(dir)
    os.system("git -c advice.detachedHead=false  checkout {}^".format(commit_id))
    print()
    if type(src_file1) == list:
        shutil.copy(src_file1[0],"../"+dst_file1)
        shutil.copy(src_file2[0],"../"+dst_file2)
        os.system("git -c advice.detachedHead=false  checkout {}".format(commit_id))
        print()
        shutil.copy(src_file1[1],"../"+dst_file1_)
        shutil.copy(src_file2[1],"../"+dst_file2_)
        os.system("git -c advice.detachedHead=false  checkout main")
        print()
        os.chdir("..")
    else:
        shutil.copy(src_file1,"../"+dst_file1)
        shutil.copy(src_file2,"../"+dst_file2)
        os.system("git -c advice.detachedHead=false  checkout {}".format(commit_id))
        print()
        shutil.copy(src_file1,"../"+dst_file1_)
        shutil.copy(src_file2,"../"+dst_file2_)
        os.system("git -c advice.detachedHead=false  checkout main")
        print()
        os.chdir("..")


if __name__ == "__main__":
    # .h文件按照.cc文件处理，挂载到镜像的.cc文件中

    commit_id = "0a110021d21a43a376f29a5ff1672ac6293c71cc"
    get_cfile(commit_id=commit_id,
              src_file1="src/compiler/backend/ppc/code-generator-ppc.cc",
              src_file2="src/compiler/backend/riscv64/code-generator-riscv64.cc",
              src_file1_="src/compiler/backend/ppc/code-generator-ppc.cc",
              )