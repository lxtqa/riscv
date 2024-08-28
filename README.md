# README

## 运行方法

命令行执行`python script.py`

```
usage: script.py [-h] [-D] [-s] [-r] [-d] [-o OUTPUT_DIRECTORY] [-m MATCHER_ID] [-g TREE_GENERATOR_ID]
                 input_directory1 input_directory2 input_directory1_

命令行参数处理程序

positional arguments:
  input_directory1      输入文件目录1
  input_directory2      输入文件目录2
  input_directory1_     输入文件目录1_

options:
  -h, --help            show this help message and exit
  -D, --debugging       启用调试模式
  -s, --simple          使用简单模式
  -r, --rm_tempfile     删除临时文件
  -d, --use_docker      使用Docker
  -o OUTPUT_DIRECTORY, --output_directory OUTPUT_DIRECTORY
                        指定输出文件目录
  -m MATCHER_ID, --matcher_id MATCHER_ID
                        指定MATCHER_ID，默认为gumtree
  -g TREE_GENERATOR_ID, --tree_generator_id TREE_GENERATOR_ID
                        指定TREE_GENERATOR_ID，默认为cs-srcml
```

## 环境部署

本项目python部分使用到的库均为常用库，遇到未安装的库直接使用`pip install XXXX`即可。

gumtree：见[库/gumtree](# gumtree)部分的介绍

## 程序与脚本

### 获取历史commit部分代码

#### get_patch.py

读取v8仓库中`git log`的输出，获取所有出现过riscv关键词/某个日期前的commit的哈希值到`GitHash-origin.txt`中，将每一个commit的结果输出到`patches-origin`文件夹下

#### classify.py

读取`patches-origin`文件夹下的内容，分离出多个架构下进行了相似改动的文件，这个检测主要依赖于文件名相似性的检测，输出到`classified_patch`中

#### split_and_filter.py 

读取`/classified_patch`中的内容，使用splitdiff，将分割并组织好的patch输出到`/tmp`

#### get_history_patch.sh

```shell
python3 get_patch.py
python3 classify.py
python3 split_and_filter.py ./classified_patch
```

运行以上代码

#### gen_statistics.py

生成历史中的统计信息，统计各个代码文件被修改了多少次

#### get_cfile.py

从v8项目的commit历史中获取某个commit下的文件，并拷贝到`/test`目录下的`testx.xx`

### 生成新patch部分代码

#### ast_utils.py

利用`gumtree parse`命令生成ast到txt文件，并返回一个经过parse的抽象语法树，以及其他的ast相关工具

#### arc_utils.py

包括has_archwords和remove_archwords两个函数

#### disjoint_sets.py

并查集

#### ast_diff_parser.py

处理diff操作，将原始diff进行合并处理

#### gen_result.py

将【架构1下代码，架构2下代码，架构1下修改后代码，指定架构2下修改后代码输出目录】作为参数，使用docker镜像中的gumtree textdiff命令，获取match和diff，基于ast方法生成代码文件，直接生成架构2下修改后的代码文件。

#### extract_unit.py

从代码中分离出不同的unit

#### unit_result.py

代码单元为粒度的结果生成

#### exec.sh

执行gen_result.py

#### show_diff.sh

在http://localhost:4567上展示两个文件的diff结果。

####  script.py

执行脚本

## 库

### V8

[v8仓库]( https://github.com/v8/v8.git) 

V8是解析javascript语言的的虚拟机,V8引擎转换成字节码(bytecode)，此时是可以跨平台的，将字节码转化汇编指令，在不同环境的cpu下执行。

![image-20220822140358681](./img/image-20220822140358681.png)

![image-20220822140344154](./img/image-20220822140344154.png)

 由于公司项目的需求,现在主要是做脱Flash的工作(历史原因用AS3.0做的)!现在全部转为C++, 并且发布PC版与Web版。其中Web的版本就是使用的Wasm（WebAssembly技术）。
 WASM ，全称：WebAssembly ，是一种可以使用非 Java 编程语言编写代码并且能在浏览器上运行的技术方案，也是自 Web 诞生以来首个 Java 原生替代方案（ 程序本质上都是脚本程序，即由程序翻译指令并执行，而不是由本地机器CPU读取指令并执行，因此效率非常低。而Java的操作相对重复繁琐，在执行过程中耗时较长。）
 其实创建Wasm的初衷并非为了替代JavaScript，而是为了实现两者之间的补充和配合。随着WebAssembly的引入，现代web浏览器的虚拟机将同时运行JavaScript和Wasm代码。

![image-20220822154219022](./img/image-20220822154219022.png)

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

*** 配置方法：***

```shell
git clone https://github.com/GumTreeDiff/gumtree.git
cd gumtree
./gradlew build -x test
cd dist/build/distributions
unzip gumtree-4.0.0-beta3-SNAPSHOT.zip
```

在`.bashrc`文件中加入如下内容

```bash
# add gumtree
export gumtree=你的gumtree路径/dist/build/distributions/gumtree-4.0.0-beta3-SNAPSHOT
export PATH=${gumtree}/bin:$PATH
```

在命令行执行

```shell
source .bashrc
```

[官方文档](https://github.com/GumTreeDiff/gumtree/wiki/Commands#overriding-properties)

[Docker使用教程](https://github.com/GumTreeDiff/gumtree/tree/main/docker)

下载镜像：`docker pull gumtreediff/gumtree`

[Gumtree参数介绍](https://github.com/GumTreeDiff/gumtree/blob/089b3d5aaddb1c31385862440e889f4b90776b85/core/src/main/java/com/github/gumtreediff/matchers/ConfigurationOptions.java#L58)

### tree-sitter

tree-sitter加入系统路径`export PATH="你的tree-sitter仓库路径/tree-sitter-parser:$PATH"`

[tree-sitter使用方法](https://blog.csdn.net/qq_38808667/article/details/128052617?spm=1001.2101.3001.6650.6&utm_medium=distribute.pc_relevant.none-task-blog-2%7Edefault%7EBlogCommendFromBaidu%7ERate-6-128052617-blog-128006684.235%5Ev38%5Epc_relevant_sort&depth_1-utm_source=distribute.pc_relevant.none-task-blog-2%7Edefault%7EBlogCommendFromBaidu%7ERate-6-128052617-blog-128006684.235%5Ev38%5Epc_relevant_sort&utm_relevant_index=12)
