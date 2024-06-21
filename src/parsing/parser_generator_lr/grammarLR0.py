from abc import ABC, abstractmethod
import os
from grammar import Grammar
from lexing.lexer_generator.finite_automata import *
from common.token_class import *
from common.parse_nodes.parse_tree import *
from common.parse_nodes.parse_node import *
from parsing.parser_generator_lr.parsing_table import ParsingTable


class LR0Item:
    def __init__(self, production: list[str], dot_index: int, prod_key : str) -> None:
        self.production = production
        self.dot_index = dot_index
        self.prod_key = prod_key

    def __str__(self) -> str:
        return f"{self.prod_key} -> {' '.join(self.production[:self.dot_index])} . {' '.join(self.production[self.dot_index:])}"

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, LR0Item):
            return False
        return self.production == value.production and self.dot_index == value.dot_index and self.prod_key == value.prod_key


class GrammarLR0(Grammar):
    # Parameters
    def __init__(
        self,
        name,
        non_terminals: list[str],
        terminals: list[str],
        start_symbol: str,
        productions: dict[str, list[list[str]]],
    ) -> None:
        super().__init__(name, non_terminals, terminals, start_symbol, productions)
    
    def buildAutomaton(self) -> DFA:
        return self.build_lr0_automaton()
                    
    def build_lr0_automaton(self):
        transitions = []
        mapped: list[LR0Item] = []

        def add_new_state(item: LR0Item) -> bool:
            if item not in mapped:
                mapped.append(item)
                return True
            return False

        def map_item(item: LR0Item) -> int:
            return mapped.index(item)

        def add_transition(
            letter: str, source: LR0Item, dest: LR0Item
        ):
            transitions.append([map_item(source), map_item(dest), letter])

        accepting_states = []

        start_state = LR0Item([self.start_symbol], 0, self.start_symbol)
        add_new_state(start_state)

        pending : list[LR0Item] = []
        pending.append(start_state)
        while len(pending) > 0:
            next = pending.pop()
            if next.dot_index < len(next.production):
                next_symbol = next.production[next.dot_index]
                if next_symbol in self.non_terminals:
                    for prod in self.productions[next_symbol]:
                        new_st = LR0Item(prod, 0, next_symbol)
                        if add_new_state(new_st):
                            pending.append(new_st)
                        add_transition(EPSILON, next, new_st)
                new_st = LR0Item(next.production, next.dot_index + 1, next.prod_key)
                if add_new_state(new_st):
                    pending.append(new_st)
                add_transition(next_symbol, next, new_st)

        start_state = map_item(start_state)
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
            additional_info[map_item(st)].append(st)

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

    def bpt(self) -> ParsingTable:
            pt = ParsingTable(
                self.automaton.total_states, self.terminals, self.non_terminals, self.productions
            )
            for ch in self.automaton.alphabet:
                for st in range(0, self.automaton.total_states):
                    index_ch = self.automaton.alphabet.index(ch)
                    if len(self.automaton.table[index_ch][st]) > 0:
                        to = self.automaton.table[index_ch][st][0]
                        if ch in self.terminals:
                            pt.add_shift_transition(st, ch, to)
                        else:
                            pt.add_nonterminal_transition(st, ch, to)

            for st in self.find_st_given_item(LR0Item([self.start_symbol], 1, self.start_symbol)):
                pt.add_accept_transition(st, self.EOF)

            for st in range(0, self.automaton.total_states):
                for item in self.automaton.additional_info[st]:
                    if item.dot_index == len(item.production) and self.is_production(item.production):
                        key = item.prod_key
                        for terminal in self.terminals:
                            pt.add_reduce_transition(st, terminal, key, len(item.production))

            return pt