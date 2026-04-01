def permutations(set_of_items):
    list_of_perms = []
    if set_of_items == []:
        return [[]]
    else:
        for song in set_of_items:
            playlist = set_of_items.copy()
            curr = playlist.pop(playlist.index(song))
            sub_perms = permutations(playlist)
            temp = []
            for item in sub_perms:
                temp.append([curr] + item)
            list_of_perms.extend(temp)
        return list_of_perms
print(permutations([1,2,3]))
print(8*7*6*5*4*3*2*1)


