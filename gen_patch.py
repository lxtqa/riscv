import os
import codecs
from tqdm import *
#git format-patch -1 [commit id]
def main():
    hash_file = codecs.open("../GitHash-origin.txt","r",errors="ignore")
    hash_lines = hash_file.readlines()
    os.system("mkdir ../patches-origin")
    for hash_line in tqdm(hash_lines):
        hash = hash_line.split("\n")[0]
        os.system("git format-patch -1 " + hash + " --stdout > ../patches-origin/" + hash + ".patch")

if __name__ == "__main__" :
    main()