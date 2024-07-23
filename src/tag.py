import subprocess
import re
import os
from tqdm import tqdm
import json

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

if __name__ == "__main__":
    tags = get_tags("./tags.json")
    if not os.path.exists("./tags_diff"):
        os.mkdir("./tags_diff")
    for i in tqdm(range(len(tags[:-1]))):
        result = subprocess.run(["git","diff",tags[i],tags[i+1]],cwd="./v8", stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8', errors='ignore')
        with open("./tags_diff/"+tags[i]+"_"+tags[i+1]+".patch","w") as f:
            f.write(output)
            f.close()