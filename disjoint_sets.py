from tqdm import tqdm
def find_disjoint_sets(lst, function , max_range = -1):
    parent = list(range(len(lst)))

    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]

    def union(x, y):
        root_x = find(x)
        root_y = find(y)
        if root_x != root_y:
            parent[root_y] = root_x

    # Iterate through the list and union elements based on the function
    for i in tqdm(range(len(lst))):
        # Limit the search scope within max_range.
        if max_range == -1 or i + max_range > len(lst):
            ending = len(lst)
        else:
            ending = i + max_range
        for j in range(i + 1, ending):
            if function(lst[i],lst[j]):
                union(i, j)
                

    # Collect sets
    sets = {}
    for i in range(len(lst)):
        root = find(i)
        if root not in sets:
            sets[root] = []
        sets[root].append(lst[i])

    return list(sets.values())