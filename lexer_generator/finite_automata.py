epsilon = "€"

class DFA:
    def __init__(
        self,
        start_state: int,
        total_states: int,
        alphabet: list[str],
        accepting_states: list[int],
        table: list[list[list[int]]],
    ):
        self.start_state = start_state
        self.total_states = total_states
        assert 0 <= self.start_state < self.total_states

        self.alphabet = alphabet
        for i in range(0, len(alphabet)):
            for j in range(0, len(alphabet)):
                assert i == j or alphabet[i] != alphabet[j]
        assert len(table) == len(alphabet)

        self.reverse = {}
        for i in range(0, len(alphabet)):
            self.reverse[alphabet[i]] = i

        self.accepting_states = accepting_states
        assert len(self.accepting_states) > 0
        for i in range(0, len(self.accepting_states)):
            assert 0 <= self.accepting_states[i] < self.total_states

        self.table = table
        for i in range(0, len(table)):
            assert len(table[i]) == total_states
        for i in range(0, len(table)):
            for j in range(0, total_states):
                assert 0 <= len(table[i][j]) <= 1
                for m in range(0, len(table[i][j])):
                    assert 0 <= table[i][j][m] < self.total_states

    def next_state(self, char: str, actual: int):
        assert char in self.alphabet
        assert 0 <= actual < self.total_states
        if len(self.table[self.reverse[char]][actual]) == 0:
            return -1
        return self.table[self.reverse[char]][actual][0]

    def simulate(self, input: str):
        actual_state = self.start_state
        for i in range(0, len(input)):
            actual_state = self.next_state(input[i], actual_state)
            if actual_state == -1:
                return False
        return actual_state in self.accepting_states

class NFA:
    """
    specify epsilon transitions in the alfhabet with €
    """

    def __init__(
        self,
        start_state: int,
        total_states: int,
        alphabet: list[str],
        accepting_states: list[int],
        table: list[list[list[int]]],
    ):

        self.start_state = start_state
        self.total_states = total_states

        assert 0 <= self.start_state < self.total_states

        self.alphabet = alphabet
        for i in range(0, len(alphabet)):
            for j in range(0, len(alphabet)):
                assert i == j or alphabet[i] != alphabet[j]

        self.reverse = {}
        for i in range(0, len(alphabet)):
            self.reverse[alphabet[i]] = i

        self.accepting_states = accepting_states

        assert len(self.accepting_states) > 0
        for i in range(0, len(self.accepting_states)):
            assert 0 <= self.accepting_states[i] < self.total_states

        self.table = table
        assert len(table) == len(alphabet)
        for i in range(0, len(table)):
            assert len(table[i]) == total_states
        for i in range(0, len(alphabet)):
            for j in range(0, total_states):
                assert 0 <= len(table[i][j]) <= self.total_states
                for st in table[i][j]:
                    assert 0 <= st < self.total_states

    def next_stateS(self, char: str, actual: int):
        assert char in self.alphabet
        assert 0 <= actual < self.total_states
        return self.table[self.reverse[char]][actual]

    def dfs(self, state: int, visited: list[bool]):
        cr = [state]
        visited[state] = True
        for st in self.table[self.reverse[epsilon]][state]:
            if not visited[st]:
                more = self.dfs(st, visited)
                for rs in more:
                    if rs not in cr:
                        cr.append(rs)
        return cr

    def EpsilonClosure(self, state: int):
        assert 0 <= state < self.total_states
        visited = [False for _ in range(0, self.total_states)]
        return self.dfs(state, visited)

    def reachable(self, char: str, states: list[int]):
        assert char in self.alphabet
        rs = []
        for st in states:
            assert 0 <= st < self.total_states
            nextStates = self.next_stateS(char, st)
            for rst in nextStates:
                if rst not in rs:
                    rs.append(rst)
        return rs

    def ConvertBinary(self, set: list[int]):
        for i in range(0, len(set)):
            for j in range(0, len(set)):
                assert i == j or set[i] != set[j]
        rs = 0
        for i in range(0, len(set)):
            rs += 1 << set[i]
        return rs

    def ConvertSet(self, number: int):
        rs = []
        for i in range(0, self.total_states):
            if (number & (1 << i)) > 0:
                rs.append(i)
        return rs

    def ConvertNFA_DFA(self):
        start_state = self.ConvertBinary(self.EpsilonClosure(self.start_state)) - 1
        total_states = (1 << self.total_states) - 1
        alphabet = []
        for ch in self.alphabet:
            if ch != epsilon:
                alphabet.append(ch)
        accepting_states = []
        for i in range(0, 1 << self.total_states):
            for j in self.accepting_states:
                if (i & (1 << j)) > 0:
                    accepting_states.append(i - 1)
                    break

        table = []
        for ch in range(0, len(alphabet)):
            table.append([[] for i in range(1, 1 << self.total_states)])
            for set1 in range(1, 1 << self.total_states):
                set = self.ConvertSet(set1)
                reachable = self.reachable(alphabet[ch], set)
                partX = []
                for st in reachable:
                    for el in self.EpsilonClosure(st):
                        if el not in partX:
                            partX.append(el)
                binary_set = self.ConvertBinary(partX)
                if len(partX) > 0:
                    table[ch][set1 - 1].append(binary_set - 1)
        return DFA(start_state, total_states, alphabet, accepting_states, table)

def Union(A, B):
    C = []
    for c in A:
        C.append(c)
    for c in B:
        if c not in C:
            C.append(c)
    return C


def NFAfor_char(char: str):
    return NFA(0, 2, [char], [1], [[[1], []]])

def ConcatenateNFA(A: NFA, B: NFA):
    start_state = A.start_state
    total_states = A.total_states + B.total_states
    alphabet = Union(A.alphabet, B.alphabet)
    accepting_states = [x + A.total_states for x in B.accepting_states]
    table = []
    for i in range(0, len(alphabet)):
        # they could be either from A or either from B or from both.
        table.append([[] for j in range(0, total_states)])
        if alphabet[i] in A.alphabet:
            for j in range(0, A.total_states):
                table[i][j] = A.table[A.reverse[alphabet[i]]][j]
        if alphabet[i] in B.alphabet:
            for j in range(0, B.total_states):
                table[i][j + A.total_states] = [
                    x + A.total_states for x in B.table[B.reverse[alphabet[i]]][j]
                ]
    if epsilon not in alphabet:
        alphabet.append(epsilon)
        table.append([[] for j in range(0, total_states)])

    for t in range(0, len(alphabet)):
        if alphabet[t] == epsilon:
            for st in A.accepting_states:
                table[t][st].append(B.start_state + A.total_states)

    return NFA(start_state, total_states, alphabet, accepting_states, table)

def UnionDFA(A: NFA, B: NFA):
    start_state = A.total_states + B.total_states
    final_state = A.total_states + B.total_states + 1
    total_states = A.total_states + B.total_states + 2
    alphabet = Union(A.alphabet, B.alphabet)
    accepting_states = [final_state]
    table = []
    for i in range(0, len(alphabet)):
        # they could be either from A or either from B or from both.
        table.append([[] for j in range(0, total_states)])
        if alphabet[i] in A.alphabet:
            for j in range(0, A.total_states):
                table[i][j] = A.table[A.reverse[alphabet[i]]][j]
        if alphabet[i] in B.alphabet:
            for j in range(0, B.total_states):
                table[i][j + A.total_states] = [
                    x + A.total_states for x in B.table[B.reverse[alphabet[i]]][j]
                ]
    if epsilon not in alphabet:
        alphabet.append(epsilon)
        table.append([[] for j in range(0, total_states)])

    for t in range(0, len(alphabet)):
        if alphabet[t] == epsilon:
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
        # they could be either from A or either from B or from both.
        table.append([[] for j in range(0, total_states)])
        for j in range(0, A.total_states):
            table[i][j] = A.table[A.reverse[alphabet[i]]][j]
    if epsilon not in alphabet:
        alphabet.append(epsilon)
        table.append([[] for j in range(0, total_states)])

    for t in range(0, len(alphabet)):
        if alphabet[t] == epsilon:
            table[t][start_state].append(final_state)
            table[t][start_state].append(A.start_state)
            for st in A.accepting_states:
                table[t][st].append(final_state)
                table[t][st].append(A.start_state)
    return NFA(start_state, total_states, alphabet, accepting_states, table)