STAR = "*"
UNION = "+"
EPSILON = "€"
QUESTION = "?"
CONCATENATE = ""

def UnionSets(A, B):
    C = []
    for c in A:
        C.append(c)
    for c in B:
        if c not in C:
            C.append(c)
    return C