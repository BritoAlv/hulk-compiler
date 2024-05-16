from common import EPSILON, UnionSets
from finite_automata import NFA

def NFAfor_char(char: str):
    return NFA(0, 2, [char], [1], [[[1], []]])

def ConcatenateNFA(A: NFA, B: NFA):
    start_state = A.start_state
    total_states = A.total_states + B.total_states
    alphabet = UnionSets(A.alphabet, B.alphabet)
    accepting_states = [x + A.total_states for x in B.accepting_states]
    table = []
    for i in range(0, len(alphabet)):
        # they could be either from A or either from B or from both.
        table.append([[] for j in range(0, total_states)])
        if alphabet[i] in A.alphabet:
            for j in range(0, A.total_states):
                table[i][j] = A.table[A.reverse[alphabet[i]]][j].copy()
        if alphabet[i] in B.alphabet:
            for j in range(0, B.total_states):
                table[i][j + A.total_states] = [
                    x + A.total_states for x in B.table[B.reverse[alphabet[i]]][j]
                ].copy()
    if EPSILON not in alphabet:
        alphabet.append(EPSILON)
        table.append([[] for j in range(0, total_states)])

    for t in range(0, len(alphabet)):
        if alphabet[t] == EPSILON:
            for st in A.accepting_states:
                table[t][st].append(B.start_state + A.total_states)

    return NFA(start_state, total_states, alphabet, accepting_states, table)


def UnionNFA(A: NFA, B: NFA):
    start_state = A.total_states + B.total_states
    final_state = A.total_states + B.total_states + 1
    total_states = A.total_states + B.total_states + 2
    alphabet = UnionSets(A.alphabet, B.alphabet)
    accepting_states = [final_state]
    table = []
    for i in range(0, len(alphabet)):
        # they could be either from A or either from B or from both.
        table.append([[] for j in range(0, total_states)])
        if alphabet[i] in A.alphabet:
            for j in range(0, A.total_states):
                table[i][j] = A.table[A.reverse[alphabet[i]]][j].copy()
        if alphabet[i] in B.alphabet:
            for j in range(0, B.total_states):
                table[i][j + A.total_states] = [
                    x + A.total_states for x in B.table[B.reverse[alphabet[i]]][j]
                ]
    if EPSILON not in alphabet:
        alphabet.append(EPSILON)
        table.append([[] for j in range(0, total_states)])

    for t in range(0, len(alphabet)):
        if alphabet[t] == EPSILON:
            for st in A.accepting_states:
                table[t][st].append(final_state)
            for st in B.accepting_states:
                table[t][st + A.total_states].append(final_state)
            table[t][B.total_states + A.total_states] += [
                A.start_state,
                B.start_state + A.total_states,
            ]

    return NFA(start_state, total_states, alphabet, accepting_states, table)


def Star(A: NFA):
    start_state = A.total_states
    final_state = A.total_states + 1
    total_states = A.total_states + 2
    alphabet = A.alphabet
    accepting_states = [final_state]
    table = []
    for i in range(0, len(alphabet)):
        table.append([[] for j in range(0, total_states)])
        for j in range(0, A.total_states):
            table[i][j] = A.table[A.reverse[alphabet[i]]][j].copy()
    if EPSILON not in alphabet:
        alphabet.append(EPSILON)
        table.append([[] for j in range(0, total_states)])

    for t in range(0, len(alphabet)):
        if alphabet[t] == EPSILON:
            table[t][start_state].append(final_state)
            table[t][start_state].append(A.start_state)
            for st in A.accepting_states:
                table[t][st].append(final_state)
                table[t][st].append(A.start_state)
    return NFA(start_state, total_states, alphabet, accepting_states, table)

def Question(A: NFA):
    start_state = A.start_state
    total_states = A.total_states
    alphabet = A.alphabet.copy()
    accepting_states = A.accepting_states.copy()
    if start_state not in accepting_states:
        accepting_states.append(start_state)
    table = []
    for i in range(0, len(alphabet)):
        table.append([[] for j in range(0, total_states)])
        for j in range(0, A.total_states):
            table[i][j] = A.table[A.reverse[alphabet[i]]][j].copy()
    return NFA(start_state, total_states, alphabet, accepting_states, table)