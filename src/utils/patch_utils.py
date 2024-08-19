import re
import subprocess

INF = 2**31


def read_patch(output):
    R = r"^@@ -\d+,?\d* \+\d+,?\d* @@ (.*)$"
    changed_unit_header = []
    try:
        output = output.split("\n")
    except:
        pass
    for line in output:
        if re.match(R,line):
            changed_unit_header.append(re.findall(R,line)[0])

    return changed_unit_header

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


def format(code):
    """
        string
    """
    code = subprocess.run(["clang-format"],input=code.encode(),stdout=subprocess.PIPE)
    return code.stdout.decode()