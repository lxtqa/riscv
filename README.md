# README

## Javascript V8项目简介

是解析javascript语言的的虚拟机

V8引擎转换成字节码(bytecode)，此时是可以跨平台的，将字节码转化汇编指令，在不同环境的cpu下执行。

![image-20220822140358681](/Users/yuhaonan/Library/Application Support/typora-user-images/image-20220822140358681.png)

![image-20220822140344154](/Users/yuhaonan/Library/Application Support/typora-user-images/image-20220822140344154.png)

 由于公司项目的需求,现在主要是做脱Flash的工作(历史原因用AS3.0做的)!现在全部转为C++, 并且发布PC版与Web版。其中Web的版本就是使用的Wasm（WebAssembly技术）。
 WASM ，全称：WebAssembly ，是一种可以使用非 Java 编程语言编写代码并且能在浏览器上运行的技术方案，也是自 Web 诞生以来首个 Java 原生替代方案（ 程序本质上都是脚本程序，即由程序翻译指令并执行，而不是由本地机器CPU读取指令并执行，因此效率非常低。而Java的操作相对重复繁琐，在执行过程中耗时较长。）
 其实创建Wasm的初衷并非为了替代JavaScript，而是为了实现两者之间的补充和配合。随着WebAssembly的引入，现代web浏览器的虚拟机将同时运行JavaScript和Wasm代码。

![image-20220822154219022](/Users/yuhaonan/Library/Application Support/typora-user-images/image-20220822154219022.png)



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
