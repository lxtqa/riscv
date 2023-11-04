import os 
import shutil
import sys

def get_cfile(commit_id,src_file1,src_file2,src_file1_):
    dst_file1 = "test/test1.cc"
    dst_file1_ = "test/test1_.cc"
    dst_file2 = "test/test2.cc"
    dir = "./v8"
    os.chdir(dir)
    os.system("git -c advice.detachedHead=false  checkout {}^".format(commit_id))
    print()
    s = os.listdir()
    shutil.copy(src_file1,"../"+dst_file1)
    shutil.copy(src_file2,"../"+dst_file2)
    os.system("git -c advice.detachedHead=false  checkout {}".format(commit_id))
    print()
    shutil.copy(src_file1_,"../"+dst_file1_)
    os.system("git -c advice.detachedHead=false  checkout main")
    print()
    os.chdir("..")


if __name__ == "__main__":
    # .h文件按照.cc文件处理，挂载到镜像的.cc文件中
    
    commit_id = "1ff685d8b1a13794abaca3adf36cfd9838b1f6fc"
    get_cfile(commit_id=commit_id,
              src_file1="src/deoptimizer/x64/deoptimizer-x64.cc",
              src_file2="src/deoptimizer/riscv64/deoptimizer-riscv64.cc",
              src_file1_="src/deoptimizer/x64/deoptimizer-x64.cc",
              )

    # commit_id = "3ac59282af1ceb1930dd958f00e96fb0b27bcbaa"
    # get_cfile(commit_id=commit_id,
    #           src_file1="src/codegen/x64/assembler-x64-inl.h",
    #           src_file2="src/codegen/riscv64/assembler-riscv64-inl.h",
    #           src_file1_="src/codegen/x64/assembler-x64-inl.h",
    #           )
    
    # commit_id = "6c0716d8af6eb2cfebc0ac7bb87db768765fde24"
    # get_cfile(commit_id=commit_id,
    #           src_file1="src/wasm/baseline/ppc/liftoff-assembler-ppc.h",
    #           src_file2="src/wasm/baseline/s390/liftoff-assembler-s390.h",
    #           src_file1_="src/wasm/baseline/ppc/liftoff-assembler-ppc.h",
    #           )
    

    # commit_id = "0bd3033a54e5b42cd35395b495669be3ebf9b6c0"
    # get_cfile(commit_id=commit_id,
    #           src_file1="src/wasm/baseline/x64/liftoff-assembler-x64.h",
    #           src_file2="src/wasm/baseline/riscv/liftoff-assembler-riscv64.h",
    #           src_file1_="src/wasm/baseline/x64/liftoff-assembler-x64.h",
    #           )


    # commit_id = "3aec86ef6f7c358ec29700f27a50c67db6a56414"
    # get_cfile(commit_id=commit_id,
    #           src_file1="src/codegen/x64/assembler-x64-inl.h",
    #           src_file2="src/codegen/riscv/assembler-riscv-inl.h",
    #           src_file1_="src/codegen/x64/assembler-x64-inl.h",
    #           )
    

    #有问题
    # commit_id = "4a97c8c7e94b2aa4353896807079619ea8626892"
    # get_cfile(commit_id=commit_id,
    #           src_file1="src/wasm/baseline/x64/liftoff-assembler-x64.h",
    #           src_file2="src/wasm/baseline/riscv/liftoff-assembler-riscv64.h",
    #           src_file1_="src/wasm/baseline/x64/liftoff-assembler-x64.h",
    #           )

    #匹配失败
    # commit_id = "4ab70f6b218b719d9ba282a6a733c978216943d6"
    # get_cfile(commit_id=commit_id,
    #           src_file1="src/wasm/baseline/x64/liftoff-assembler-x64.h",
    #           src_file2="src/wasm/baseline/ia32/liftoff-assembler-ia32.h",
    #           src_file1_="src/wasm/baseline/x64/liftoff-assembler-x64.h",
    #           )

    # commit_id = "0a110021d21a43a376f29a5ff1672ac6293c71cc"
    # get_cfile(commit_id=commit_id,
    #           src_file1="src/compiler/backend/ppc/code-generator-ppc.cc",
    #           src_file2="src/compiler/backend/riscv64/code-generator-riscv64.cc",
    #           src_file1_="src/compiler/backend/ppc/code-generator-ppc.cc",
    #           )