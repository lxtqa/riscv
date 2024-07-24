import json
import subprocess
from tqdm import tqdm
import re
import os
from fuzzywuzzy import fuzz
from arc_utils import remove_arcwords
from disjoint_sets import find_disjoint_sets
from unit_result import read_patch

subject_file = "subject.json"
if not os.path.exists(subject_file):
    with open('arch_related_commit_id.json', 'r') as json_file:
        commits = json.load(json_file)
        for commit in tqdm(commits):
            hash = commit["hash"]
            result = subprocess.run(["git","format-patch","-1",hash,"--stdout"],cwd="./v8",stdout=subprocess.PIPE)
            output = result.stdout.decode('utf-8', errors='ignore').split("\n")
            flag  = 0
            subject = ""
            for line in output:
                if flag == 1:
                    if line != "" and line[0] == " ":
                        subject = subject + line
                    else:
                        break
                if re.match(r"^Subject:.*",line):
                    flag = 1
                    subject = line[8:]

            for line in output:
                if line[:5] == "Date:":
                    commit["time"] = line.split(" ")[1:5]
                    break

            commit["subject"] = subject
            commit["units"] = read_patch(output)

        f = open(subject_file,"w")
        f.write(json.dumps(commits))
        f.close()


with open(subject_file,"r") as f:
    subjects = json.load(f)
    def same_subject(a,b):
        if fuzz.ratio(remove_arcwords(a["subject"]),remove_arcwords(b["subject"]))>95:#subject相似度
            if fuzz.token_sort_ratio((remove_arcwords(x) for x in a["file_names"]),(remove_arcwords(x) for x in b["file_names"])) > 95:#修改文件相似度
                if fuzz.token_sort_ratio((remove_arcwords(x) for x in a["units"]),(remove_arcwords(x) for x in b["units"])) > 95:#修改unit相似度
                    return True
        else:
            return False
    result = sorted(find_disjoint_sets(subjects,same_subject,50),key=len,reverse = True)
    with open("inter_commit.txt","w") as f1:
        for i in result:
            if len(i) >= 2:
                for j in i:
                    if j["time"][-1] == "2023":
                        f1.write("{" + j["hash"]+"  "+j["subject"]+ " " +j["time"][-1]+"}\t")
                f1.write("\n")