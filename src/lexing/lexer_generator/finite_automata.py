from const import EPSILON, UnionSets

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

        self = Remove_Equal(self)
        self = Remove_Disconnected(self)

    def next_state(self, char: str, actual: int):
        assert 0 <= actual < self.total_states
        if (
            char not in self.alphabet
            or len(self.table[self.reverse[char]][actual]) == 0
        ):
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

        self = Remove_Equal(self)
        self = Remove_Disconnected(self)

    def next_stateS(self, char: str, actual: int):
        assert char in self.alphabet
        assert 0 <= actual < self.total_states
        return self.table[self.reverse[char]][actual]

    def EpsilonClosure(self, state: int):
        assert 0 <= state < self.total_states
        visited = [False for _ in range(0, self.total_states)]
        return dfs(state, visited, [EPSILON], self)

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
            if ch != EPSILON:
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

def dfs(state: int, visited: list[bool], choices: list[str], FA: NFA | DFA):
    cr = [state]
    visited[state] = True
    for choice in choices:
        assert choice in FA.alphabet
        for st in FA.table[FA.reverse[choice]][state]:
            if not visited[st]:
                more = dfs(st, visited, choices, FA)
                for rs in more:
                    if rs not in cr:
                        cr.append(rs)
    return cr

def Remove_Disconnected(FA : NFA | DFA):
    # print("STARTS WITH " + str(FA.total_states))
    reachable = dfs(FA.start_state, [False for _ in range(0, FA.total_states)], FA.alphabet, FA)
    # print(reachable)
    #print(FA.start_state)
    remove = []
    for i in range(FA.total_states-1, -1, -1):
        if i not in reachable:
            remove.append(i)
    for x in remove:
        remove_state(FA, x)
    #print("ENDS WITH " + str(FA.total_states))
    return FA
        
def remove_state(FA : NFA | DFA, st : int):
    if FA.start_state > st:
        FA.start_state -= 1
    if st in FA.accepting_states:
        FA.accepting_states.remove(st)
    for z in range(0, len(FA.accepting_states)):
        if FA.accepting_states[z] > st:
            FA.accepting_states[z] -= 1
    for z in range(0, len(FA.alphabet)):
        for q in range(0, FA.total_states):
            if st in FA.table[z][q]:
                FA.table[z][q].remove(st)
            for d in range(0, len(FA.table[z][q])):
                if FA.table[z][q][d] > st:
                    FA.table[z][q][d] -= 1
    for z in range(0, len(FA.alphabet)):
        del FA.table[z][st]
    FA.total_states -= 1
    return FA

def Remove_Equal(FA: NFA | DFA):
    #print("STARTS WITH " + str(FA.total_states))
    dict = {}
    hashes = [compute_hash(i, FA) for i in range(0, FA.total_states)]
    for i in range(0, FA.total_states):
        hash = hashes[i]
        flag = i in FA.accepting_states
        if (hash, flag) not in dict:
            dict[(hash, flag)] = []
        dict[(hash, flag)].append(i)

    keys = list(dict.keys())
    map_keys = {}
    for i in range(0, len(keys)):
        map_keys[keys[i]] = i
    start_state = map_keys[
        (hashes[FA.start_state], FA.start_state in FA.accepting_states)
    ]
    total_states = len(keys)
    alphabet = FA.alphabet
    accepting_states = [
        map_keys[(hashes[x], x in FA.accepting_states)] for x in FA.accepting_states
    ]
    accepting_states = list(set(accepting_states))
    table = [[] for _ in range(0, len(FA.alphabet))]
    for z in range(0, len(FA.alphabet)):
        for j in range(0, total_states):
            table[z].append([])
    for z in range(0, len(FA.alphabet)):
        for i in range(0, FA.total_states):
            mapped_i = map_keys[(hashes[i], i in FA.accepting_states)]
            for j in range(0, len(FA.table[z][i])):
                mapped_j = map_keys[(hashes[FA.table[z][i][j]], FA.table[z][i][j] in FA.accepting_states)]
                if mapped_j not in table[z][mapped_i]:
                    table[z][mapped_i].append(mapped_j)
    FA.table = table
    FA.accepting_states = accepting_states
    FA.total_states = total_states
    FA.alphabet = alphabet
    FA.start_state = start_state
    #print("ENDS WITH " + str(FA.total_states))
    return FA

def print_row(FA: NFA | DFA, i: int):
    print("BEGIN")
    for z in range(0, len(FA.alphabet)):
        print(FA.alphabet[z], FA.table[z][i])
    print("END")

def equal_rows(FA: NFA | DFA, i: int, j: int):
    for z in range(0, len(FA.alphabet)):
        FA.table[z][i].sort()
        FA.table[z][j].sort()
        if FA.table[z][i] != FA.table[z][j]:
            return False
    return True

def compute_hash(st: int, FA: NFA | DFA):
    MOD = 1000000007
    rs = 0
    for i in range(0, len(FA.alphabet)):
        FA.table[i][st].sort()
        M = ord(FA.alphabet[i])
        M %= MOD
        M *= hash(tuple(FA.table[i][st])) % MOD
        M %= MOD
        rs += M
    return rs