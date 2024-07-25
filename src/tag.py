import subprocess
import re
import os
from tqdm import tqdm
import json
from arc_utils import has_arcwords

def get_tags(tag_path):
    try:
        tags = json.load(open(tag_path,"r"))
        return tags
    except:
        result = subprocess.run(["git","tag"],cwd="./v8", stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8', errors='ignore')
        tags = output.split("\n")
        num_tags = []
        for tag in tqdm(tags):
            if re.match(r"^\d+(\.\d+)*$",tag):
                result = subprocess.run(['git','show','--format="%ci"',tag],cwd="./v8", stdout=subprocess.PIPE)
                output = result.stdout.decode('utf-8', errors='ignore')
                time = output.split("\n")[0][1:-1]
                if time[0:4] == "2022" or time[0:4] == "2023":
                    num_tags.append(tag)
        tags = sorted(num_tags, key=lambda x: tuple(map(int, x.split('.'))))
        with open(tag_path,'w') as json_file:
            json_file.write(json.dumps(tags))
        return tags

def get_commits(adjacent_tag):
    result = subprocess.run(["git","log","--format=%H","--decorate" ,adjacent_tag[0]+".."+adjacent_tag[1]],cwd="./v8", stdout=subprocess.PIPE)
    output = result.stdout.decode('utf-8', errors='ignore')
    commits = output.split("\n")
    while "" in commits:
        commits.remove("")
    return commits


def parse_version(version):
    parts = version.split('.')
    major = int(parts[0])
    minor = int(parts[1]) if len(parts) > 1 else 0
    build = int(parts[2]) if len(parts) > 2 else 0
    patch = int(parts[3]) if len(parts) > 3 else 0
    return (major, minor, build, patch)

def are_adjacent(v1, v2):
    major1, minor1, build1, patch1 = parse_version(v1)
    major2, minor2, build2, patch2 = parse_version(v2)
    if major1 == major2:
        if minor1 == minor2:
            if build1 == build2:
                return abs(patch1 - patch2) == 1
            elif abs(build1 - build2) == 1 and patch1 == 0 and patch2 == 0:
                return True
        elif abs(minor1 - minor2) == 1 and build1 == 0 and build2 == 0 and patch1 == 0 and patch2 == 0:
            return True
    elif abs(major1 - major2) == 1 and minor1 == 0 and minor2 == 0 and build1 == 0 and build2 == 0 and patch1 == 0 and patch2 == 0:
        return False
    return False

def find_adjacent_tags(tag_list):
    adjacent_tags = []
    for i in range(len(tag_list) - 1):
        if are_adjacent(tag_list[i], tag_list[i + 1]):
            adjacent_tags.append((tag_list[i], tag_list[i + 1]))
    return adjacent_tags


if __name__ == "__main__":
    tags = get_tags("./tags.json")
    adjacent_tags = find_adjacent_tags(tags)
    target_tags = []
    if not os.path.exists("./tags_diff"):
        os.mkdir("./tags_diff")
    for adjacent_tag in tqdm(adjacent_tags):
        result = subprocess.run(["git","diff",adjacent_tag[0],adjacent_tag[1]],cwd="./v8", stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8', errors='ignore')
        patch = output.split("\n")
        filtered_patchs ={"commits":[],"contents":[]}
        filtered_patch = []
        tmp_filename = None
        for line in patch:
            filename = re.findall(r"^diff --git a/(.+) b/(.+)$",line)
            if filename != []:
                if filtered_patch != []:
                    filtered_patchs["contents"].append([tmp_filename,filtered_patch])
                    filtered_patch = []
                if has_arcwords(filename[0][0]):
                    tmp_filename = filename[0][0]
                    target_tags.append(adjacent_tag)
                else:
                    tmp_filename = None
            if tmp_filename:
                filtered_patch.append(line)
        if filtered_patchs["contents"] != []:
            filtered_patchs["commits"] = get_commits(adjacent_tag)
            with open("./tags_diff/"+adjacent_tag[0]+"_"+adjacent_tag[1]+".json","w") as f:
                json.dumps(filtered_patchs,f,indent=4)
    # TODO: 对照subject的结果，看看文件修改有没有缺失