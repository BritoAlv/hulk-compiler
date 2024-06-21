from abc import ABC, abstractmethod
from common.constants import EPSILON
from lexing.lexer_generator.utils import *

class FA(ABC):
    def __init__(
        self,
        start_state: int,
        total_states: int,
        alphabet: list[str],
        accepting_states: list[int],
        table: list[list[list[int]]],
        additional_info=[],
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
                for m in range(0, len(table[i][j])):
                    assert 0 <= table[i][j][m] < self.total_states

        self.additional_info = additional_info
        if len(self.additional_info) == 0:
            self.additional_info = [[] for _ in range(0, self.total_states)]
        else:
            assert(self.total_states == len(self.additional_info))
        assert len(self.additional_info) == total_states
        if reduce:
            self = FA.Remove_Equal(self)
            self = FA.Remove_Disconnected(self)

    @abstractmethod
    def next_state(self, char: str, actual: int):
        pass
    
    @abstractmethod
    def simulate(self, input: str):
        pass

    @staticmethod
    def dfs(state: int, visited: list[bool], choices: list[str], FAut: "FA"):
        cr = [state]
        visited[state] = True
        for choice in choices:
            assert choice in FAut.alphabet
            for st in FAut.table[FAut.reverse[choice]][state]:
                if not visited[st]:
                    more = FA.dfs(st, visited, choices, FAut)
                    for rs in more:
                        if rs not in cr:
                            cr.append(rs)
        return cr

    @staticmethod
    def Remove_Disconnected(FAut: "FA"):
        # print("STARTS WITH " + str(FA.total_states))
        reachable = FAut.dfs(
            FAut.start_state, [False for _ in range(0, FAut.total_states)], FAut.alphabet, FAut
        )
        # print(reachable)
        # print(FA.start_state)
        remove = []
        for i in range(FAut.total_states - 1, -1, -1):
            if i not in reachable:
                remove.append(i)
        for x in remove:
            FA.remove_state(FAut, x)
        # print("ENDS WITH " + str(FA.total_states))
        return FA

    @staticmethod
    def remove_state(FAut: "FA", st: int):
        if FAut.start_state > st:
            FAut.start_state -= 1
        if st in FAut.accepting_states:
            FAut.accepting_states.remove(st)
        for z in range(0, len(FAut.accepting_states)):
            if FAut.accepting_states[z] > st:
                FAut.accepting_states[z] -= 1
        for z in range(0, len(FAut.alphabet)):
            for q in range(0, FAut.total_states):
                if st in FAut.table[z][q]:
                    FAut.table[z][q].remove(st)
                for d in range(0, len(FAut.table[z][q])):
                    if FAut.table[z][q][d] > st:
                        FAut.table[z][q][d] -= 1
        for z in range(0, len(FAut.alphabet)):
            del FAut.table[z][st]
        FAut.additional_info.pop(st)
        FAut.total_states -= 1
        assert(len(FAut.additional_info) == FAut.total_states) # type: ignore
        return FAut

    @staticmethod
    def Remove_Equal(FAut: "FA"):
        assert(FAut.total_states == len(FAut.additional_info)) # type: ignore
        # print("STARTS WITH " + str(FA.total_states))
        dict = {}
        hashes = [FA.compute_hash(i, FAut) for i in range(0, FAut.total_states)]
        for i in range(0, FAut.total_states):
            hash = hashes[i]
            flag = i in FAut.accepting_states
            if (hash, flag) not in dict:
                dict[(hash, flag)] = []
            dict[(hash, flag)].append(i)

        keys = list(dict.keys())
        map_keys = {}
        for i in range(0, len(keys)):
            map_keys[keys[i]] = i
        start_state = map_keys[
            (hashes[FAut.start_state], FAut.start_state in FAut.accepting_states)
        ]
        total_states = len(keys)
        additional_info = [[] for i in range(0, total_states)]
        for i in range(0, FAut.total_states):
            additional_info[
                map_keys[(hashes[i], i in FAut.accepting_states)]
            ] += FAut.additional_info[i]
            additional_info[map_keys[(hashes[i], i in FAut.accepting_states)]] = list(
                set(additional_info[map_keys[(hashes[i], i in FAut.accepting_states)]])
            )
        alphabet = FAut.alphabet
        accepting_states = [
            map_keys[(hashes[x], x in FAut.accepting_states)] for x in FAut.accepting_states
        ]
        accepting_states = list(set(accepting_states))
        table = [[] for _ in range(0, len(FAut.alphabet))]
        for z in range(0, len(FAut.alphabet)):
            for j in range(0, total_states):
                table[z].append([])
        for z in range(0, len(FAut.alphabet)):
            for i in range(0, FAut.total_states):
                mapped_i = map_keys[(hashes[i], i in FAut.accepting_states)]
                for j in range(0, len(FAut.table[z][i])):
                    mapped_j = map_keys[
                        (
                            hashes[FAut.table[z][i][j]],
                            FAut.table[z][i][j] in FAut.accepting_states,
                        )
                    ]
                    if mapped_j not in table[z][mapped_i]:
                        table[z][mapped_i].append(mapped_j)
        FAut.table = table
        FAut.accepting_states = accepting_states
        FAut.total_states = total_states
        FAut.alphabet = alphabet
        FAut.start_state = start_state
        FAut.additional_info = additional_info
        return FAut

    @staticmethod
    def compute_hash(st: int, FAut: "FA"):
        MOD = 1000000007
        rs = 0
        for i in range(0, len(FAut.alphabet)):
            FAut.table[i][st].sort()
            M = ord(FAut.alphabet[i])
            M %= MOD
            M *= hash(tuple(FAut.table[i][st])) % MOD
            M %= MOD
            rs += M
            rs %= MOD
        return rs

class DFA(FA):
    def __init__(
        self,
        start_state: int,
        total_states: int,
        alphabet: list[str],
        accepting_states: list[int],
        table: list[list[list[int]]],
        additional_info=[],
        reduce: bool = True,
    ):
        super().__init__(start_state, total_states, alphabet, accepting_states, table, additional_info, reduce)
        for i in range(0, len(table)):
            for j in range(0, total_states):
                assert 0 <= len(table[i][j]) <= 1
                
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


class NFA(FA):
    def __init__(
        self,
        start_state: int,
        total_states: int,
        alphabet: list[str],
        accepting_states: list[int],
        table: list[list[list[int]]],
        additional_info,
        reduce: bool = True,
    ):
        super().__init__(start_state, total_states, alphabet, accepting_states, table, additional_info, reduce)


    def next_state(self, char: str, actual: int):
        assert char in self.alphabet
        assert 0 <= actual < self.total_states
        return self.table[self.reverse[char]][actual]

    def simulate(self, input: str):
        return super().simulate(input)

    def EpsilonClosure(self, state: int):
        assert 0 <= state < self.total_states
        if EPSILON not in self.alphabet:
            return [state]
        visited = [False for _ in range(0, self.total_states)]
        return FA.dfs(state, visited, [EPSILON], self)

    def reachable(self, char: str, states: list[int]):
        assert char in self.alphabet
        rs = []
        for st in states:
            assert 0 <= st < self.total_states
            nextStates = self.next_state(char, st)
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

    def ConvertNFA_DFA(self) -> DFA:

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