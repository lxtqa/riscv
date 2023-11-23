def parse_diff_file(diff_file_path):
    changes = []

    with open(diff_file_path, 'r') as diff_file:
        current_change = None
        for line in diff_file:

            if line.startswith('---') or line.startswith('+++'):
                # 这是源文件路径的行，忽略它
                continue
            elif line.startswith('@@'):
                # 这是一个修改块的标头行
                if current_change:
                    changes.append(current_change)
                rank = int(line.strip().split(" ")[1].split(",")[0][1:])
                current_change = {'begining': -1, "ending": -1, "relative": rank}
            elif line.startswith('-'):
                if current_change['begining'] == -1:
                    current_change['begining'] = current_change['relative']
                current_change['ending'] = current_change['relative']
                current_change['relative'] += 1
            elif line.startswith('+'):
                if current_change['begining'] == -1:
                    current_change['begining'] = current_change['relative']
                current_change['ending'] = current_change['relative']
            else:
                if current_change:
                    current_change['relative'] += 1


        if current_change:
            changes.append(current_change)

    return changes


def to_rank(changes, source_file_path):
    ranks = []

    for change in changes:
        with open(source_file_path, 'r') as source_file:
            source_file = source_file.readlines()

            begining = 0
            ending = 0
            for i in range(len(source_file)):
                if i < change["begining"]-1:
                    begining += len(source_file[i])
                if i < change["ending"]-1:
                    ending += len(source_file[i])
            ranks.append({"begining":begining,"ending":ending})
    return ranks
    

def diff2rank(diff_file_path, source_file_path):
    changes = parse_diff_file(diff_file_path)
    ranks = to_rank(changes, source_file_path)
    return ranks

if __name__ == "__main__":
    diff_file_path = './test/patch.patch'
    source_file_path = './test/test1.cc'
    diff2rank(diff_file_path, source_file_path)


    
    


