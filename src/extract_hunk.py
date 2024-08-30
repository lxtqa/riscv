import re
from utils.patch_utils import *
def extract_hunk(file_lines,file_name=""):
    hunk_header_indices = [0]
    header_re = r"^((::[\[:space:]]*)?[A-Za-z_].*)$"
    for i,line in enumerate(file_lines):
        if re.match(header_re,line):
            hunk_header_indices.append(i)
    hunk_header_indices.append(INF)

    hunks = []
    for i in range(len(hunk_header_indices) - 1):
        hunk_lines = file_lines[hunk_header_indices[i]:hunk_header_indices[i + 1]]
        hunks.append({
                    "header": file_lines[hunk_header_indices[i]],
                    "content": hunk_lines,
                    "file": file_name
                })
    return hunks