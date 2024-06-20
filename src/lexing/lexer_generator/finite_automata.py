from os import listxattr
# from tkinter import NO
from lexing.lexer_generator.const import EPSILON, UnionSets

def remove_repeated( listt : list):
    result = []
    for x in listt:
        if x not in result:
            result.append(x)
    return result

class DFA:
    def __init__(
        self,
        start_state: int,
        total_states: int,
        alphabet: list[str],
        accepting_states: list[int],
        table: list[list[list[int]]],
        additional_info=None,
        reduce: bool = True,
    ):
        self.start_state = start_state
        self.total_states = total_states
        self.reduce = reduce
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

        self.additional_info = additional_info
        if self.additional_info == None:
            self.additional_info = [[] for _ in range(0, self.total_states)]
        else:
            assert(self.total_states == len(self.additional_info))
        assert len(self.additional_info) == total_states
        if reduce:
            self = Remove_Equal(self)
            self = Remove_Disconnected(self)

    def next_state(self, char: str, actual: int) -> int:
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
        additional_info = None,
        reduce: bool = True,
    ):

        self.start_state = start_state
        self.total_states = total_states
        self.reduce = reduce
        assert 0 <= self.start_state < self.total_states

        self.alphabet = alphabet
        for i in range(0, len(alphabet)):
            for j in range(0, len(alphabet)):
                assert i == j or alphabet[i] != alphabet[j]

        self.reverse = {}
        for i in range(0, len(alphabet)):
            self.reverse[alphabet[i]] = i

        self.accepting_states = accepting_states

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

        self.additional_info = additional_info
        if self.additional_info == None:
            self.additional_info = [[] for _ in range(0, self.total_states)]
        else:
            assert(self.total_states == len(self.additional_info))
        if self.reduce:
            self = Remove_Equal(self)
            self = Remove_Disconnected(self)

    def next_stateS(self, char: str, actual: int):
        assert char in self.alphabet
        assert 0 <= actual < self.total_states
        return self.table[self.reverse[char]][actual]

    def EpsilonClosure(self, state: int):
        assert 0 <= state < self.total_states
        if EPSILON not in self.alphabet:
            return [state]
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

        pending = []
        mapped = {}
        transitions = []
        accepting_states = []
        additional_info = []

        alphabet = []
        for ch in self.alphabet:
            if ch != EPSILON:
                alphabet.append(ch)

        def get_closure_state(old_state: int) -> int:
            return self.ConvertBinary(self.EpsilonClosure(old_state))

        def check_accept_state(new_state: int):
            for st in self.ConvertSet(new_state):
                if st in self.accepting_states and st not in accepting_states:
                    accepting_states.append(mapped[new_state])

        def reachable_closure(letter: str, state: int):
            reachable = self.reachable(letter, self.ConvertSet(next))
            reachable_closure = []
            for x in reachable:
                for y in self.EpsilonClosure(x):
                    if y not in reachable_closure:
                        reachable_closure.append(y)
            return reachable_closure

        def add_new_state(new_state: int):
            mapped[new_state] = len(mapped)
            additional_info.append([])
            for st in self.ConvertSet(new_state):
                additional_info[-1] += self.additional_info[st]
                additional_info[-1] = remove_repeated(additional_info[-1])
            check_accept_state(new_state)
            pending.append(new_state)

        start_state = get_closure_state(self.start_state)
        add_new_state(start_state)

        while len(pending) > 0:
            next = pending.pop(0)
            for i in range(0, len(alphabet)):
                ch = alphabet[i]
                result_state = self.ConvertBinary(reachable_closure(ch, next))
                if result_state > 0:  # this state has outgoing transitions.
                    if result_state not in mapped:
                        add_new_state(result_state)
                    transitions.append((i, mapped[next], mapped[result_state]))

        table = []
        total_states = len(mapped)
        for ch in range(0, len(alphabet)):
            table.append([[] for i in range(0, total_states)])
        for tr in transitions:
            assert len(table[tr[0]][tr[1]]) == 0
            table[tr[0]][tr[1]].append(tr[2])

        dfa = DFA(
            0,
            total_states,
            alphabet,
            accepting_states,
            table,
            additional_info,
            self.reduce,
        )
        return dfa


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


def Remove_Disconnected(FA: NFA | DFA):
    # print("STARTS WITH " + str(FA.total_states))
    reachable = dfs(
        FA.start_state, [False for _ in range(0, FA.total_states)], FA.alphabet, FA
    )
    # print(reachable)
    # print(FA.start_state)
    remove = []
    for i in range(FA.total_states - 1, -1, -1):
        if i not in reachable:
            remove.append(i)
    for x in remove:
        remove_state(FA, x)
    # print("ENDS WITH " + str(FA.total_states))
    return FA


def remove_state(FA: NFA | DFA, st: int):
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
    FA.additional_info.pop(st)
    FA.total_states -= 1
    assert(len(FA.additional_info) == FA.total_states) # type: ignore
    return FA


def Remove_Equal(FA: NFA | DFA):
    assert(FA.total_states == len(FA.additional_info)) # type: ignore
    # print("STARTS WITH " + str(FA.total_states))
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
    additional_info = [[] for i in range(0, total_states)]
    for i in range(0, FA.total_states):
        additional_info[
            map_keys[(hashes[i], i in FA.accepting_states)]
        ] += FA.additional_info[i]
        additional_info[map_keys[(hashes[i], i in FA.accepting_states)]] = list(
            set(additional_info[map_keys[(hashes[i], i in FA.accepting_states)]])
        )
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
                mapped_j = map_keys[
                    (
                        hashes[FA.table[z][i][j]],
                        FA.table[z][i][j] in FA.accepting_states,
                    )
                ]
                if mapped_j not in table[z][mapped_i]:
                    table[z][mapped_i].append(mapped_j)
    FA.table = table
    FA.accepting_states = accepting_states
    FA.total_states = total_states
    FA.alphabet = alphabet
    FA.start_state = start_state
    FA.additional_info = additional_info
    return FA


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
        rs %= MOD
    return rs
