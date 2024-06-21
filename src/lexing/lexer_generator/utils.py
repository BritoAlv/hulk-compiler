def UnionSets(A, B):
    C = []
    for c in A:
        C.append(c)
    for c in B:
        if c not in C:
            C.append(c)
    return C

def remove_repeated( listt : list):
    result = []
    for x in listt:
        if x not in result:
            result.append(x)
    return result
