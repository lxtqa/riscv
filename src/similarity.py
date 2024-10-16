import json

with open('similarity.json', 'r') as json_file:
    similarity = json.load(json_file)
    #riscv64
    m = [[0,0] for _ in range(10)]
    lst = [[0,0] for _ in range(10)]
    for file in similarity:
        file_name = file[0]
        for block_sets in file[2]:
            astnodenum = block_sets[0] - 1
            if astnodenum == 0:
                continue
            # if block_sets[1][4] < 0.5:
            #     c = 0
            for i,sim in enumerate(block_sets[1]):
                if i != 2 and i != 3:
                    m[i][1] = m[i][1] + sim * astnodenum
                    lst[i][1] = (lst[i][1] * lst[i][0] + sim * astnodenum) / (lst[i][0] + astnodenum)
                    lst[i][0] = lst[i][0] + astnodenum
        for i,total_astnodenum in enumerate(file[1]):
            m[i][0] = m[i][0]+total_astnodenum
        # m.append([file_name,lst])
    # with open("file_similarity.json","w") as f:
    #     json.dump(m,f,indent=4)
with open("total_similarity.json","w") as f:
    json.dump(m,f,indent=4)