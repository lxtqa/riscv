# README

## 程序与脚本

### git_info.sh

将v8仓库中main分支的git信息读取到`GitLog-origin.txt`中

运行`get_hash.py`并将结果重定向到`GitHash-origin.txt`中

运行`gen_patch.py`，将每一个commit的结果输出到`patches-origin`文件夹下

移除`GitLog-origin.txt`与`GitHash-origin.txt`

### classify.py

读取`patches-origin`文件夹下的内容，自动对含有riscv关键字的文件进行分类，分离出多个架构下进行了相似改动的文件，这个检测主要依赖于文件名相似性的检测，输出到`classified_patch`中

### split_and_filter.py 

读取classified_patch中的内容，使用splitdiff，将分割并组织好的patch输出到tmp

### gumtree_parser.py

输入`gumtree diff`生成的txt文件名，将文件中的matches和diffs分别返回

### get_ast.py

利用`gumtree parse`命令生成ast到txt文件，并返回一个经过parse的抽象语法树

### generate_diff.py

依次输入三个cpp名称【架构1下代码，架构2下代码，架构1下修改后代码】，使用gumtree textdiff命令，获取match和diff，并进行映射操作

### diff_to_file.py

将diff操作实现到文件中

### init_vendor.py

初始化tree-sitter相关内容

## 库

### Splitdiff

```
splitdiff -a filename
OPTIONS are:
  -a              split out every single file-level patch
  -p N            pathname components to ignore
  -d              use output filenames like a_b.c.patch for a/b.c
  -D dir          create patches in subdirectory dir (implies -d)
  -E              don't use .patch filename extension
```

### gumtree

官方文档：https://github.com/GumTreeDiff/gumtree/wiki/Commands#overriding-properties

使用教程：https://blog.csdn.net/weixin_39278265/article/details/101427644

### tree-sitter

https://blog.csdn.net/qq_38808667/article/details/128052617?spm=1001.2101.3001.6650.6&utm_medium=distribute.pc_relevant.none-task-blog-2%7Edefault%7EBlogCommendFromBaidu%7ERate-6-128052617-blog-128006684.235%5Ev38%5Epc_relevant_sort&depth_1-utm_source=distribute.pc_relevant.none-task-blog-2%7Edefault%7EBlogCommendFromBaidu%7ERate-6-128052617-blog-128006684.235%5Ev38%5Epc_relevant_sort&utm_relevant_index=12

## 运行

在目录下运行exec.sh
