from lexing.lexer_generator.finite_automata import *
from common.token_class import *
from common.parse_nodes.parse_tree import *
from common.parse_nodes.parse_node import *
from parsing.parser_generator_lr.parsing_table import ParsingTable
from parsing.parser_generator_lr.first_set import First_Set_Calculator

class LR1Item:
    def __init__(self, production: list[str], dot_index: int, prod_key : str, lookahead : str) -> None:
        self.production = production
        self.dot_index = dot_index
        self.prod_key = prod_key
        self.lookahead = lookahead

    def __str__(self) -> str:
        return f"{self.prod_key} -> {' '.join(self.production[:self.dot_index])} . {' '.join(self.production[self.dot_index:])}, {self.lookahead}"

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, LR1Item):
            return False
        return self.production == value.production and self.dot_index == value.dot_index and self.prod_key == value.prod_key and self.lookahead == value.lookahead

class GrammarLR1:
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
        self.First_Set_Calculator = First_Set_Calculator(self.non_terminals, self.terminals, self.start_symbol, self.productions)
        self.automatonLR1 = self.build_lr1_automaton()

        
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

    def find_st_given_item(self, itemToFound : LR1Item) -> int:
        for st in range(0, self.automatonLR1.total_states):
            for item in self.automatonLR1.additional_info[st]:
                if itemToFound == item:
                    return st
        return -1

    def build_parsing_table(self) -> ParsingTable:
        pt = ParsingTable(
            self.automatonLR1.total_states, self.terminals, self.non_terminals
        )
        for ch in self.automatonLR1.alphabet:
            for st in range(0, self.automatonLR1.total_states):
                index_ch = self.automatonLR1.alphabet.index(ch)
                if len(self.automatonLR1.table[index_ch][st]) > 0:
                    to = self.automatonLR1.table[index_ch][st][0]
                    if ch in self.terminals:
                        pt.add_shift_transition(st, ch, to)
                    else:
                        pt.add_nonterminal_transition(st, ch, to)

        pt.add_accept_transition(
            self.find_st_given_item(LR1Item([self.start_symbol], 1, self.start_symbol, self.EOF)), 
            self.EOF
        )

        for st in range(0, self.automatonLR1.total_states):
            for item in self.automatonLR1.additional_info[st]:
                if item.dot_index == len(item.production) and self.is_production(item.production):
                    key = item.prod_key
                    pt.add_reduce_transition(st, item.lookahead, key, len(item.production))
        return pt
                    
    def build_lr1_automaton(self):
        transitions = []
        mapped: list[LR1Item] = []

        def add_new_state(st: LR1Item) -> bool:
            if st not in mapped:
                mapped.append(st)
                return True
            return False

        def map_state(st: LR1Item) -> int:
            return mapped.index(st)

        def add_transition(
            letter: str, source: LR1Item, dest: LR1Item
        ):
            transitions.append([map_state(source), map_state(dest), letter])

        accepting_states = []

        start_state = LR1Item([self.start_symbol], 0, self.start_symbol, self.EOF)
        add_new_state(start_state)
        pending : list[LR1Item] = []
        pending.append(start_state)
        while len(pending) > 0:
            next = pending.pop()
            if next.dot_index < len(next.production):
                next_symbol = next.production[next.dot_index]
                if next_symbol in self.non_terminals:
                    for prod in self.productions[next_symbol]:
                        for term in self.First_Set_Calculator.list_first_set( next.production[next.dot_index+1:]  + [next.lookahead]):
                            new_st = LR1Item(prod, 0, next_symbol, term)
                            if add_new_state(new_st):
                                pending.append(new_st)
                            add_transition(EPSILON, next, new_st)
                
                new_st = LR1Item(next.production, next.dot_index + 1, next.prod_key, next.lookahead)
                if add_new_state(new_st):
                    pending.append(new_st)
                add_transition(next_symbol, next, new_st)

        start_state = map_state(start_state)
        total_states = len(mapped)
        alphabet = self.non_terminals + self.terminals + [EPSILON]
        table = [[] for _ in range(0, len(alphabet))]
        for z in range(0, len(alphabet)):
            for _ in range(0, total_states):
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