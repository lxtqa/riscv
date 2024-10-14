import re
from utils.patch_utils import *
def extract_block(file_lines,file_name=""):
    block_header_indices = []
    for i,line in enumerate(file_lines):
        if re.match(header_re,line):
            block_header_indices.append(i)
    if block_header_indices == [] or block_header_indices[0] != 0:
        block_header_indices = [0]+block_header_indices
    block_header_indices.append(INF)

    blocks = []
    for i in range(len(block_header_indices) - 1):
        block_lines = file_lines[block_header_indices[i]:block_header_indices[i + 1]]
        blocks.append({
                    "header": file_lines[block_header_indices[i]],
                    "content": block_lines,
                    "file": file_name
                })
    return blocks