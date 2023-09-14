# README

### git_info.sh

将v8仓库中main分支的git信息读取到GitLog-origin.txt中

运行get_hash.py并将结果重定向到GitHash-origin.txt中

运行gen_patch.py，将每一个commit的结果输出到patches-origin文件夹下

移除GitLog-origin.txt与GitHash-origin.txt

### classify.py

读取patches-origin文件夹下的内容，自动对含有riscv关键字的文件进行分类，分离出多个架构下进行了相似改动的文件，这个检测主要依赖于文件名相似性的检测，输出到classified_patch中

### split_and_filter.py 

读取classified_patch中的内容，使用splitdiff，将分割并组织好的patch输出到tmp

splitdiff的使用方法和参数位于splitdiff_options.txt中

使用`run_split_and_filter.sh`运行

### gumtree

官方文档：https://github.com/GumTreeDiff/gumtree/wiki/Commands#overriding-properties

### gumtree_parser.py

输入gumtree diff生成的txt文件名，将文件中的matches和diffs分别返回





