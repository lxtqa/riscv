import re
import subprocess

INF = 2**31

def replace_header(old_string,new_header):
    R = r"^@@ -\d+,?\d* \+\d+,?\d* @@ (.*)$"
    if re.findall(R,old_string)!= []:
        old_header = re.findall(R,old_string)[0]
        new_string = old_string.replace(old_header,new_header)
        return new_string
    return old_string


def read_patch(output):
    R = r"^@@ -\d+,?\d* \+\d+,?\d* @@ (.*)$"
    changed_block_header = []
    try:
        output = output.split("\n")
    except:
        pass
    for line in output:
        if re.match(R,line):
            if re.findall(R,line)!= []:
                changed_block_header.append(re.findall(R,line)[0])
            else:
                changed_block_header.append("")

    return changed_block_header

def start_line(output):
    R = r"@@ -(\d+),?\d* \+(\d+),?\d* @@"

    # 搜索匹配
    match = re.search(R, output)

    if match:
        old_start = match.group(1)
        new_start = match.group(2)
        return int(old_start),int(new_start)
    else:
        return None, None


def format(code,cwd="."):
    """
        string
    """
    code = subprocess.run(["clang-format"],cwd=cwd,input=code.encode(),stdout=subprocess.PIPE)
    return code.stdout.decode()