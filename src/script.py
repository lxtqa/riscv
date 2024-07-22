import argparse
import sys
from unit_result import unit_result

def script():
    parser = argparse.ArgumentParser(description='命令行参数处理程序')

    # 添加必选项输入文件目录
    parser.add_argument('input_directory1', type=str, help='输入文件目录1')
    parser.add_argument('input_directory2', type=str, help='输入文件目录2')
    parser.add_argument('input_directory1_', type=str, help='输入文件目录1_')

    # 添加可选项输出文件目录和其他选项
    parser.add_argument('-D', '--debugging', action='store_true', help='启用调试模式')
    parser.add_argument('-d', '--use_docker', action='store_true', help='使用Docker')
    parser.add_argument('-o', '--output_directory', type=str, help='指定输出文件目录')
    parser.add_argument('-m', '--matcher_id', type=str, default='gumtree', help='指定MATCHER_ID，默认为gumtree')
    parser.add_argument('-g', '--tree_generator_id', type=str, default='cs-srcml', help='指定TREE_GENERATOR_ID，默认为cs-srcml')

    # 解析命令行参数
    args = parser.parse_args()

    # 根据参数执行相应操作
    if args.debugging:
        print('启用调试模式')
        # 在这里执行调试模式的相关操作
    if args.simple:
        print('使用简单模式')
        # 在这里执行简单模式的相关操作
    if args.rm_tempfile:
        print('删除临时文件')
        # 在这里执行删除临时文件的相关操作
    if args.use_docker:
        print('使用Docker')
        # 在这里执行使用Docker的相关操作
    if not args.output_directory:
        print('错误：未指定输出文件目录。请使用 -o 或 --output_directory 选项指定输出目录。')
        sys.exit(1)
        # 在这里执行输出文件目录的相关操作

    # 输出必选项输入文件目录
    print('输入文件目录1:', args.input_directory1)
    print('输入文件目录2:', args.input_directory2)
    print('输入文件目录1_:', args.input_directory1_)
    unit_result(dir = "",cfile_name1 = args.input_directory1,
               cfile_name2 = args.input_directory2,
               cfile_name1_ = args.input_directory1_,
               cfile_name2_ = args.output_directory,
               rm_tempfile = args.rm_tempfile,
               use_docker = args.use_docker,
               debugging = args.debugging,
               MATCHER_ID = args.matcher_id,
               TREE_GENERATOR_ID=args.tree_generator_id
               )

if __name__ == '__main__':
    script()
