from lexing.lexer_generator.finite_automata import *
from common.token_class import *
from common.parse_nodes.parse_tree import *
from common.parse_nodes.parse_node import *
from parsing.parser_generator_lr.parsing_table import ParsingTable


class GrammarLR0:
    # Parameters
    def __init__(
        self,
        non_terminals: list[str],
        terminals: list[str],
        start_symbol: str,
        productions: dict[str, list[list[str]]],
    ) -> None:
        # Body
        self.EOF = "$"
        self.non_terminals = non_terminals
        self.terminals = terminals + [self.EOF]
        self.start_symbol = start_symbol
        self.productions = productions
        self.automatonLR0 = self.build_lr0_automaton()

    def is_production(self, prod : list[str]) -> bool:
        for key in self.productions:
            for pr in self.productions[key]:
                if pr == prod:
                    return True
        return False
    
    def find_key_given_prod(self, prod : list[str]) -> str:
        for key in self.productions:
            for pr in self.productions[key]:
                if pr == prod:
                    return key
        return ""

    def find_st_given_item(self, itemToFound : tuple[int, list[str]]) -> int:
        for st in range(0, self.automatonLR0.total_states):
            for item in self.automatonLR0.additional_info:
                if itemToFound == item:
                    return st
        return -1

    def build_parsing_table(self) -> ParsingTable:
        pt = ParsingTable(
            self.automatonLR0.total_states, self.terminals, self.non_terminals
        )
        for ch in self.automatonLR0.alphabet:
            for st in range(0, self.automatonLR0.total_states):
                index_ch = self.automatonLR0.alphabet.index(ch)
                if len(self.automatonLR0.table[index_ch][st]) > 0:
                    to = self.automatonLR0.table[index_ch][st][0]
                    if ch in self.terminals:
                        pt.add_shift_transition(st, ch, to)
                    else:
                        pt.add_nonterminal_transition(st, ch, to)

        pt.add_accept_transition(self.find_st_given_item((1, [self.start_symbol])), self.EOF)

        for st in range(0, self.automatonLR0.total_states):
            for item in self.automatonLR0.additional_info[st]:
                if item[0] == len(item[1]) and self.is_production(item[1]):
                    key = self.find_key_given_prod(item[1])
                    for terminal in self.terminals:
                        pt.add_reduce_transition(st, terminal, key, len(item[1]))

        return pt
                    
    def build_lr0_automaton(self):
        transitions = []
        mapped: list[tuple[int, list[str]]] = []

        def add_new_state(st: tuple[int, list[str]]) -> bool:
            if st not in mapped:
                mapped.append(st)
                return True
            return False

        def map_state(st: tuple[int, list[str]]) -> int:
            return mapped.index(st)

        def add_transition(
            letter: str, source: tuple[int, list[str]], dest: tuple[int, list[str]]
        ):
            transitions.append([map_state(source), map_state(dest), letter])

        accepting_states = []

        start_state = (0, [self.start_symbol])
        add_new_state(start_state)

        pending : list[tuple[int, list[str]]] = []
        pending.append(start_state)
        while len(pending) > 0:
            next = pending.pop()
            if next[0] < len(next[1]):
                next_symbol = next[1][next[0]]
                if next_symbol in self.non_terminals:
                    for prod in self.productions[next_symbol]:
                        new_st = (0, prod)
                        if add_new_state(new_st):
                            pending.append(new_st)
                        add_transition(EPSILON, next, new_st)
                new_st = (next[0] + 1, next[1])
                if add_new_state(new_st):
                    pending.append(new_st)
                add_transition(next_symbol, next, new_st)

        start_state = map_state(start_state)
        total_states = len(mapped)
        alphabet = self.non_terminals + self.terminals + [EPSILON]
        table = [[] for _ in range(0, len(alphabet))]
        for z in range(0, len(alphabet)):
            for j in range(0, total_states):
                table[z].append([])

        for tr in transitions:
            table[alphabet.index(tr[2])][tr[0]].append(tr[1])

        additional_info = [[] for _ in range(0, total_states)]
        for st in mapped:
            additional_info[map_state(st)].append(st)

        nfa = NFA(
            start_state,
            total_states,
            alphabet,
            accepting_states,
            table,
            additional_info,
            False,
        )
        dfa = nfa.ConvertNFA_DFA()
        return dfa