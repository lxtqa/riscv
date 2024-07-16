import json
import subprocess
from tqdm import tqdm
import re
import os

length = 1000
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

            commit["subject"] = subject
        f = open(subject_file,"w")
        f.write(json.dumps(commits))
        f.close()
with open(subject_file,"r") as f:
    subject = json.load(f)


        
                
        
        

    